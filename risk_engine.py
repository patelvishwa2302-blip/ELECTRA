# risk_engine.py

from database import MEDICINES, BRAND_ALIASES, lookup_medicine, lookup_key
from ayurvedic_db import AYURVEDIC_INTERACTIONS
from food_db import FOOD_INTERACTIONS
from rules import INTERACTION_RULES
from models import InteractionAlert, BurdenScore
from compartments import compartment_for


SEVERITY_SCORE = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
SCORE_TO_LABEL = {1: "low", 2: "moderate", 3: "high", 4: "critical"}


def analyze_medicines(scanned_brands, ayurvedic_list, food_list, patient):
    """
    Core analysis function.
    Returns a dict matching AnalyzeResponse structure.
    """

    # ── STEP 1: Resolve brand names → medicine dicts ─────────────
    resolved = []
    unrecognized = []
    for brand in scanned_brands:
        med = lookup_medicine(brand)
        if med:
            resolved.append(med)
        else:
            unrecognized.append(brand)

    classes_present = set(m["therapeutic_class"] for m in resolved)
    generics_present = set(m["generic"].lower() for m in resolved)

    # ── STEP 2: Detect duplicate generics ────────────────────────
    seen_generics = {}
    for med in resolved:
        g = med["generic"].lower()
        if g in seen_generics:
            seen_generics[g].append(med["brand"])
        else:
            seen_generics[g] = [med["brand"]]
    duplicates = {g: brands for g, brands in seen_generics.items() if len(brands) > 1}

    # ── STEP 3: Run each rule ─────────────────────────────────────
    alerts = []
    lock_compartments = set()
    hold_backs = []          # WHICH medicine is held back, and why


    for rule in INTERACTION_RULES:
        trigger = rule["trigger"]
        matched_meds = []

        # NEW: class + patient condition (e.g., NSAID + CKD) — check this FIRST
        if "patient_condition" in trigger:
            condition_met = getattr(patient, trigger["patient_condition"], False)
            if condition_met:
                matched_classes = set()
                for cls in trigger["classes"]:
                    meds_of_class = [m for m in resolved if m["therapeutic_class"] == cls]
                    if meds_of_class:
                        matched_meds.extend(meds_of_class)
                        matched_classes.add(cls)
                
                if len(matched_classes) >= rule.get("min_drugs_matching", len(trigger["classes"])):
                    alert = _build_alert(rule, matched_meds, patient, classes_present)
                    if alert:
                        alerts.append(alert)
                    if rule.get("lock_compartment_class"):
                                                _find_compartments_to_lock(rule, resolved, lock_compartments, hold_backs)


        # Rule type: class-based
        elif "classes" in trigger:
            matched_classes = set()
            for cls in trigger["classes"]:
                meds_of_class = [m for m in resolved if m["therapeutic_class"] == cls]
                if meds_of_class:
                    matched_meds.extend(meds_of_class)
                    matched_classes.add(cls)

            # Check if we have enough distinct required drug *types* (not just pill count)
            if len(matched_classes) >= rule.get("min_drugs_matching", len(trigger["classes"])):
                alert = _build_alert(rule, matched_meds, patient, classes_present)
                if alert:
                    alerts.append(alert)
                    if rule.get("lock_compartment_class"):
                        _find_compartments_to_lock(rule, resolved, lock_compartments, hold_backs)

        # Rule type: duplicate detection
        elif trigger.get("type") == "duplicate_generic" and duplicates:
            for generic, brands in duplicates.items():
                dup_meds = [m for m in resolved if m["generic"].lower() == generic]
                alert = _build_alert(rule, dup_meds, patient, classes_present)
                if alert:
                    alerts.append(alert)
                    # Hold back the SECOND brand tapped — the first is already in use.
                    hold = dup_meds[1] if len(dup_meds) > 1 else dup_meds[0]
                    _add_hold_back(hold, lock_compartments, hold_backs,
                                   "Same medicine as " + dup_meds[0]["brand"] +
                                   " (both " + generic + ")")

        elif trigger.get("type") == "duplicate_class":
            class_counts = {}
            for m in resolved:
                cls = m["therapeutic_class"]
                class_counts[cls] = class_counts.get(cls, 0) + 1
            dup_classes = [cls for cls, count in class_counts.items() if count >= 2]
            if dup_classes:
                for cls in dup_classes:
                    dup_meds = [m for m in resolved if m["therapeutic_class"] == cls]
                    alert = _build_alert(rule, dup_meds, patient, classes_present)
                    if alert:
                        alerts.append(alert)

        # Rule type: ayurvedic
        elif trigger.get("ayurvedic"):
            target_class = trigger.get("allopathic_class")
            target_classes = target_class if isinstance(target_class, list) else [target_class]
            allopathic_match = [m for m in resolved if m["therapeutic_class"] in target_classes]
            if allopathic_match and ayurvedic_list:
                alert = _build_alert(rule, allopathic_match, patient, classes_present, ayurvedic_involved=ayurvedic_list)
                if alert:
                    alerts.append(alert)

        # Rule type: food
        elif trigger.get("food"):
            food_key = trigger["food"]
            if food_key in food_list:
                target_classes = trigger.get("allopathic_class", [])
                if isinstance(target_classes, str):
                    target_classes = [target_classes]
                matched_meds = [m for m in resolved if m["therapeutic_class"] in target_classes]
                if matched_meds:
                    alert = _build_alert(rule, matched_meds, patient, classes_present, food_key=food_key)
                    if alert:
                        alerts.append(alert)

        # Rule type: scheduled substance
        elif "schedule" in trigger:
            scheduled = [m for m in resolved if m.get("schedule") in trigger["schedule"]]
            if scheduled:
                alert = _build_alert(rule, scheduled, patient, classes_present)
                if alert:
                    alerts.append(alert)

    # ── STEP 4: Ayurvedic cross-check ────────────────────────────
    for ayurved in ayurvedic_list:
        found_entry = next((entry for entry in AYURVEDIC_INTERACTIONS if ayurved.lower() in entry["name"].lower()), None)
        
        if found_entry:
            for med in resolved:
                cls = med["therapeutic_class"]
                if cls in found_entry["interacts_with_class"] or med["generic"].lower() in found_entry["interacts_with_generic"]:
                    alerts.append(InteractionAlert(
                        rule_id="AYUR-DYNAMIC",
                        name=f"{found_entry['name']} + {med['brand']}",
                        severity=found_entry["risk_level"],
                        risk_category="ayurvedic",
                        medicines_involved=[found_entry["name"], med["brand"]],
                        patient_explanation=found_entry["patient_message"],
                        doctor_explanation=found_entry["doctor_message"],
                        evidence=found_entry.get("evidence", "Natural Medicines Database"),
                        action="Discuss Ayurvedic medicine use with prescribing doctor.",
                        monitoring="Monitor for adverse effects specific to this combination."
                    ))
        else:
            # Fallback for unrecognized Ayurvedic medicine
            unrecognized.append(f"{ayurved} (Ayurvedic)")
            alerts.append(InteractionAlert(
                rule_id="AYUR-UNKNOWN",
                name=f"Unknown Ayurvedic Formulation: {ayurved}",
                severity="moderate",
                risk_category="ayurvedic_unknown",
                medicines_involved=[ayurved],
                patient_explanation=f"We don't have interaction data for {ayurved}. Please consult your doctor before mixing this with your prescriptions.",
                doctor_explanation=f"Product '{ayurved}' is not in the current interaction database. Proceed with caution.",
                evidence="System Safety Fallback",
                action="Consult treating physician before continuing.",
                monitoring="General safety monitoring."
            ))

    # ── STEP 5: Deduplicate + sort alerts by severity ─────────────
    seen_ids = set()
    unique_alerts = []
    for a in alerts:
        if a.rule_id not in seen_ids:
            seen_ids.add(a.rule_id)
            unique_alerts.append(a)

    unique_alerts.sort(key=lambda x: SEVERITY_SCORE.get(x.severity, 0), reverse=True)

    # ── STEP 6: Overall risk = worst severity ────────────────────
    if unique_alerts:
        overall_risk = unique_alerts[0].severity
    else:
        overall_risk = "low"

    # ── STEP 7: Polypharmacy Burden Score ─────────────────────────
    burden = _calculate_burden(resolved, patient)

    # ── STEP 8: Compartment locking logic ────────────────────────
    lock_list = list(lock_compartments)

    # ── STEP 9: OLED display text ─────────────────────────────────
    display_text = _generate_oled_text(overall_risk, unique_alerts)

    return {
        "overall_risk": overall_risk,
        "alerts": unique_alerts,
        "burden_score": burden,
        "lock_compartments": lock_list,
        "hold_backs": hold_backs,
        "buzzer": overall_risk in ["high", "critical"],
        "display_text": display_text,
        "whatsapp_sent": False,  # set in main.py after sending
        "unrecognized_medicines": unrecognized
    }


def _build_alert(rule, matched_meds, patient, classes_present, ayurvedic_involved=None, food_key=None):
    """Build an InteractionAlert with patient-modifier adjusted severity."""
    base = SEVERITY_SCORE.get(rule["base_severity"], 2)

    # Apply patient modifiers
    modifiers = rule.get("patient_modifiers", {})
    score = base
    if modifiers.get("age_gt_65") and patient.age > 65:
        score += modifiers["age_gt_65"]
    if modifiers.get("age_gt_75") and patient.age > 75:
        score += modifiers["age_gt_75"]
    if modifiers.get("ckd") and patient.ckd:
        score += modifiers["ckd"]
    if modifiers.get("concurrent_anticoagulant") and "anticoagulant" in classes_present:
        score += modifiers["concurrent_anticoagulant"]
    if modifiers.get("nsaid_concurrent") and "nsaid" in classes_present:
        score += modifiers["nsaid_concurrent"]
    if modifiers.get("beta_blocker_concurrent") and "beta_blocker" in classes_present:
        score += modifiers["beta_blocker_concurrent"]

        # ── Phase 3: modifiers that were written into rules but never applied ──
    if modifiers.get("alcohol") and getattr(patient, "alcohol", False):
        score += modifiers["alcohol"]
    if modifiers.get("copd") and getattr(patient, "copd", False):
        score += modifiers["copd"]
    if modifiers.get("sleep_apnoea") and getattr(patient, "sleep_apnoea", False):
        score += modifiers["sleep_apnoea"]
    if modifiers.get("dehydration") and getattr(patient, "dehydration", False):
        score += modifiers["dehydration"]
    if modifiers.get("bradycardia") and getattr(patient, "bradycardia", False):
        score += modifiers["bradycardia"]
    if modifiers.get("hypokalemia") and getattr(patient, "hypokalemia", False):
        score += modifiers["hypokalemia"]
    if modifiers.get("hypomagnesemia") and getattr(patient, "hypomagnesemia", False):
        score += modifiers["hypomagnesemia"]
    if modifiers.get("female") and getattr(patient, "sex", "") == "female":
        score += modifiers["female"]


    # Cap at 4 (critical)
    score = min(score, 4)
    severity = SCORE_TO_LABEL.get(score, "high")

    med_names = [m["brand"] for m in matched_meds]
    if ayurvedic_involved:
        med_names = ayurvedic_involved + med_names
    if food_key:
        med_names = [food_key] + med_names

    return InteractionAlert(
        rule_id=rule["id"],
        name=rule["name"],
        severity=severity,
        risk_category=rule["risk_category"],
        medicines_involved=med_names,
        patient_explanation=rule["patient_explanation"],
        doctor_explanation=rule["doctor_explanation"],
        evidence=rule["evidence"],
        action=rule["action"],
        monitoring=rule.get("monitoring", ""),
        refer_to_doctor=rule.get("refer_to_doctor", False)
    )


def _calculate_burden(resolved, patient):
    """Sum organ load scores across all medicines, apply patient multipliers."""
    totals = {"kidney": 0, "liver": 0, "cardiac": 0, "bleeding": 0, "cns": 0}
    for med in resolved:
        for organ, val in med.get("organ_load", {}).items():
            totals[organ] = totals.get(organ, 0) + val

    # Patient multipliers
    if patient.ckd:
        totals["kidney"] = min(int(totals["kidney"] * 1.5), 10)
    if patient.liver_disease:
        totals["liver"] = min(int(totals["liver"] * 1.5), 10)

    # Normalize to max 10
    for k in totals:
        totals[k] = min(totals[k], 10)

    overall = round(sum(totals.values()) / len(totals), 1)
    return BurdenScore(**totals, overall=overall)


def _generate_oled_text(overall_risk, alerts):
    """Generate short text for OLED display (max 4 lines, 20 chars each)."""
        # Referral cases (pregnancy, breastfeeding, serious conditions): no advice
    if alerts and any(getattr(a, "refer_to_doctor", False) for a in alerts) \
            and overall_risk in ("high", "critical"):
        return "CONSULT DOCTOR\nDo not change\nany medicine\nyourself"

    if overall_risk == "low":
        return "OK ALL CLEAR\nLOW RISK\nAll medicines safe"
    elif overall_risk == "moderate":
        return f"CAUTION\n{alerts[0].name[:18] if alerts else 'Interaction'}\nConsult doctor"
    elif overall_risk == "high":
        top = alerts[0].medicines_involved[0][:12] if alerts else "Medicine"
        return f"HIGH RISK!\n{top} FLAGGED\nSee dashboard\nConsult doctor"
    else:  # critical
        top = alerts[0].medicines_involved[-1][:12] if alerts else "Medicine"
        return f"CRITICAL!\n{top} LOCKED\nDO NOT TAKE\nSEEK DOCTOR NOW"



def _add_hold_back(med, lock_compartments, hold_backs, reason):
    """Lock this medicine's compartment, and record WHY it is held back."""
    for h in hold_backs:
        if h["medicine"] == med["brand"]:
            return

    comp = compartment_for(lookup_key(med["brand"]))
    lock_compartments.add(comp)
    hold_backs.append({
        "medicine": med["brand"],
        "compartment": comp,
        "reason": reason,
    })


def _find_compartments_to_lock(rule, resolved, lock_compartments, hold_backs):
    """Decide which compartment to lock, and which medicine to hold back.

    rule["lock_compartment_class"] is always the OPTIONAL kind of medicine —
    a painkiller or a sleeping tablet — never a blood thinner, a BP tablet or
    a thyroid tablet. That is what stops the lock taking away something the
    patient must have.
    """
    lock_class = rule.get("lock_compartment_class")
    candidates = [m for m in resolved if m["therapeutic_class"] == lock_class]
    if not candidates:
        return
    _add_hold_back(candidates[0], lock_compartments, hold_backs,
                   rule.get("name", lock_class))
