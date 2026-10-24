# rules.py

INTERACTION_RULES = [

    # ─── BLEEDING RISKS ──────────────────────────────────────────
    {
        "id": "BLEED-001",
        "name": "Antiplatelet + NSAID",
        "trigger": {"classes": ["antiplatelet", "nsaid"]},
        "min_drugs_matching": 2,
        "risk_category": "bleeding",
        "base_severity": "high",
        "patient_modifiers": {
            "age_gt_65": +1,
            "ckd": +2,
            "concurrent_anticoagulant": +2,
            "alcohol": +1
        },
        "patient_explanation": "Two of your medicines thin the blood. Taking them together greatly increases the risk of stomach bleeding.",
        "doctor_explanation": "Aspirin (irreversible COX-1 inhibition, Ser530) + Ibuprofen (reversible COX-1 + gastric mucosal damage). Ibuprofen blocks aspirin's COX-1 binding site, reducing cardioprotection. Combined GI bleed risk 3x baseline.",
        "evidence": "Beers Criteria 2023 (AGS); FDA Drug Safety Communication: NSAIDs",
        "action": "Replace NSAID with Paracetamol 500mg. If NSAID necessary, add PPI (e.g. Pantoprazole) and monitor for melena.",
        "lock_compartment_class": "nsaid",
        "monitoring": "Watch for: black/tarry stools, unexplained bruising, blood in urine, gum bleeding"
    },
    {
        "id": "BLEED-002",
        "name": "Anticoagulant + Antiplatelet",
        "trigger": {"classes": ["anticoagulant", "antiplatelet"]},
        "min_drugs_matching": 2,
        "risk_category": "bleeding",
        "base_severity": "high",
        "patient_modifiers": {
            "age_gt_75": +2,
            "ckd": +2,
            "nsaid_concurrent": +2
        },
        "patient_explanation": "You are on two types of blood thinners. This combination is sometimes necessary but increases bleeding risk. Do not stop either without asking your doctor.",
        "doctor_explanation": "Dual antithrombotic therapy: warfarin/acenocoumarol + antiplatelet. Annual major bleed risk 2–4%. Risk increases significantly in CKD (reduced drug clearance) and age >75.",
        "evidence": "Eikelboom et al., Lancet 2012; Beers Criteria 2023",
        "action": "Confirm dual therapy indication. Add PPI. Annual GI bleed risk assessment. Minimize NSAID use.",
        "lock_compartment_class": None,
        "monitoring": "Monthly INR (warfarin). Watch for any unusual bleeding."
    },

    # ─── KIDNEY RISKS ────────────────────────────────────────────
    {
        "id": "KID-001",
        "name": "Triple Whammy (NSAID + ACE/ARB + Diuretic)",
        "trigger": {"classes": ["nsaid", "ace_inhibitor", "diuretic"]},
        "min_drugs_matching": 3,
        "risk_category": "renal",
        "base_severity": "critical",
        "patient_modifiers": {
            "ckd": +3,
            "dehydration": +2,
            "age_gt_65": +1
        },
        "patient_explanation": "Three of your medicines are working against your kidneys at the same time. This is a serious combination. Your doctor must review this immediately.",
        "doctor_explanation": "NSAID reduces prostaglandin-mediated afferent arteriole dilation. ACE/ARB reduces efferent arteriole constriction. Diuretic causes volume depletion. Together: severe reduction in GFR → acute kidney injury.",
        "evidence": "Loboz & Shenfield, Nephrology 2005; NICE CKS: NSAIDs in CKD",
        "action": "URGENT: Discontinue NSAID. Replace with Paracetamol. Monitor eGFR and serum creatinine. Reassess diuretic dose.",
        "lock_compartment_class": "nsaid",
        "monitoring": "URGENT: Creatinine within 1 week of starting combination"
    },
    {
        "id": "KID-002",
        "name": "NSAID in Kidney Disease",
        "trigger": {"classes": ["nsaid"], "patient_condition": "ckd"},
        "min_drugs_matching": 1,
        "risk_category": "renal",
        "base_severity": "high",
        "patient_modifiers": {},
        "patient_explanation": "You have a kidney condition, and your pain medicine (the Brufen/ibuprofen type) puts extra strain on the kidneys. Taken regularly, it can worsen kidney function. Ask your doctor if a kidney-safe option like paracetamol can be used instead.",
        "doctor_explanation": "NSAID in CKD: prostaglandin inhibition reduces renal perfusion and can accelerate eGFR decline. Avoid NSAIDs in CKD; prefer paracetamol for analgesia.",
        "evidence": "NICE CKS: NSAIDs in CKD; Beers Criteria 2023 (AGS)",
        "action": "Replace NSAID with Paracetamol 500mg. Check creatinine/eGFR if the NSAID must continue.",
        "lock_compartment_class": "nsaid",
        "monitoring": "Creatinine/eGFR within 1 week. Watch for reduced urine output and ankle swelling."
    },

    # ─── CNS / SEDATION RISKS ────────────────────────────────────
    {
        "id": "SED-001",
        "name": "CNS Depressant Stack (≥2 sedating drugs)",
        "trigger": {"classes": ["benzodiazepine", "opioid", "antipsychotic", "sedating_antihistamine"]},
        "min_drugs_matching": 2,
        "risk_category": "sedation",
        "base_severity": "high",
        "patient_modifiers": {
            "age_gt_65": +2,
            "alcohol": +3,
            "copd": +2
        },
        "patient_explanation": "Two or more of your medicines cause drowsiness. Together, they may cause dangerous over-sedation or breathing problems. Do not drive. Do not drink alcohol.",
        "doctor_explanation": "Additive CNS depression: risk of respiratory depression, falls (elderly), paradoxical agitation. Opioid + benzodiazepine: 3.86x higher overdose mortality (FDA Black Box Warning, 2016).",
        "evidence": "FDA Black Box Warning: Opioid + Benzodiazepine (2016); Beers Criteria 2023",
        "action": "Taper to monotherapy where possible. If combination necessary: use lowest doses. Naloxone prescription should be considered.",
        "lock_compartment_class": None,
        "monitoring": "Fall risk assessment. Respiratory rate monitoring. No driving."
    },
    {
        "id": "RESP-001",
        "name": "Opioid + Benzodiazepine (FDA Black Box)",
        "trigger": {"classes": ["opioid", "benzodiazepine"]},
        "min_drugs_matching": 2,
        "risk_category": "respiratory",
        "base_severity": "critical",
        "patient_modifiers": {
            "copd": +3,
            "sleep_apnoea": +3,
            "alcohol": +3
        },
        "patient_explanation": "This specific combination of medicines can cause your breathing to stop during sleep. This is a serious danger. Tell your doctor immediately.",
        "doctor_explanation": "FDA Black Box Warning (2016). Opioid + benzodiazepine causes additive CNS/respiratory depression. 30% of opioid overdose deaths involve benzodiazepines. Risk of respiratory arrest, especially during sleep.",
        "evidence": "FDA Drug Safety Communication: Opioid + Benzodiazepine, August 2016",
        "action": "Taper benzodiazepine if clinically possible. If combination necessary: prescribe naloxone. Avoid alcohol. Sleep monitoring.",
        "lock_compartment_class": "benzodiazepine",
        "monitoring": "Respiratory rate. Pulse oximetry (SpO₂ target >92%). Naloxone availability."
    },

    # ─── CARDIAC RISKS ───────────────────────────────────────────
    {
        "id": "QT-001",
        "name": "QT-Prolonging Agents Stack",
        "trigger": {"classes": ["antiarrhythmic", "antipsychotic", "fluoroquinolone", "ssri"]},
        "min_drugs_matching": 2,
        "risk_category": "cardiac",
        "base_severity": "high",
        "patient_modifiers": {
            "hypokalemia": +3,
            "hypomagnesemia": +2,
            "bradycardia": +2,
            "female": +1
        },
        "patient_explanation": "Two or more of your medicines affect the electrical rhythm of your heart. Together, they can cause a dangerous heart rhythm abnormality.",
        "doctor_explanation": "Additive hERG channel blockade → QTc prolongation → Torsades de Pointes risk. Risk increases with electrolyte abnormalities (K+ <3.5 mEq/L or Mg2+ <0.8 mEq/L).",
        "evidence": "CredibleMeds QTDrugs database (crediblemeds.org); AHA/ACC 2018",
        "action": "Check and correct electrolytes (K+, Mg2+). ECG monitoring. Avoid additional QT-prolonging drugs.",
        "lock_compartment_class": None,
        "monitoring": "ECG (QTc). Electrolytes (K+, Mg2+) every 3 months."
    },

    # ─── DIABETES RISKS ──────────────────────────────────────────
    {
        "id": "HYPO-001",
        "name": "Sulfonylurea + Fluoroquinolone + Beta-Blocker",
        "trigger": {"classes": ["sulfonylurea", "fluoroquinolone"]},
        "min_drugs_matching": 2,
        "risk_category": "hypoglycaemia",
        "base_severity": "high",
        "patient_modifiers": {
            "age_gt_65": +2,
            "ckd": +2,
            "beta_blocker_concurrent": +2
        },
        "patient_explanation": "Your antibiotic (fluoroquinolone) can affect your blood sugar control. Combined with your diabetes medicine, your blood sugar may drop dangerously low. Watch for shakiness, sweating, or confusion.",
        "doctor_explanation": "Fluoroquinolones cause both hypoglycaemia (via ATP-sensitive K+ channel stimulation in beta cells) and hyperglycaemia. Unpredictable glucose dysregulation. Beta-blockers mask tachycardia symptom of hypoglycaemia. FDA warning issued for all fluoroquinolones.",
        "evidence": "FDA Drug Safety Communication: Fluoroquinolone antibiotics, July 2018",
        "action": "Increase glucose monitoring frequency. Consider alternative antibiotic class. Warn patient about hypoglycaemia symptoms.",
        "lock_compartment_class": None,
        "monitoring": "Blood glucose monitoring 4x daily during fluoroquinolone course."
    },

    # ─── SEROTONIN RISKS ─────────────────────────────────────────
    {
        "id": "SER-001",
        "name": "Serotonin Syndrome Risk (SSRI + Serotonergic Agent)",
        "trigger": {"classes": ["ssri", "opioid"]},
        "min_drugs_matching": 2,
        "risk_category": "serotonin_syndrome",
        "base_severity": "high",
        "patient_modifiers": {
            "maoi_concurrent": +5,
            "triptans_concurrent": +2
        },
        "patient_explanation": "Two of your medicines both increase serotonin in the brain. Together they may cause serotonin syndrome: agitation, fever, shaking, rapid heart rate. This is a medical emergency if it occurs.",
        "doctor_explanation": "SSRIs + tramadol/fentanyl (serotonin-releasing/reuptake inhibiting opioids) → serotonin accumulation. Risk of serotonin syndrome: autonomic instability, neuromuscular hyperactivity, altered consciousness.",
        "evidence": "Boyer & Shannon, NEJM 2005; Hunter Serotonin Toxicity Criteria",
        "action": "Use non-serotonergic opioid (morphine, oxycodone) if SSRI is essential. Avoid tramadol with SSRIs.",
        "lock_compartment_class": None,
        "monitoring": "Watch for: agitation, confusion, rapid heartbeat, muscle twitching, fever. Immediate ER if suspected."
    },

    # ─── DUPLICATE DETECTION ─────────────────────────────────────
    {
        "id": "DUP-001",
        "name": "Exact Duplicate: Same Generic Under Two Brand Names",
        "trigger": {"type": "duplicate_generic"},
        "min_drugs_matching": 2,
        "risk_category": "duplication",
        "base_severity": "critical",
        "patient_modifiers": {},
        "patient_explanation": "You have TWO different brands of the SAME medicine! This means you could be taking double the dose. One must be stopped immediately.",
        "doctor_explanation": "Patient has been dispensed two brand-name products containing identical active ingredient. Risk of unintentional dose doubling. Common in India where multiple generics exist (e.g., Dolo 650 + Crocin = both Paracetamol).",
        "evidence": "Internal detection: brand-to-generic normalization",
        "action": "STOP one brand immediately. Confirm single source.",
        "lock_compartment_class": "duplicate",
        "monitoring": "Confirm patient understands these are the same medicine."
    },
    {
        "id": "DUP-002",
        "name": "Therapeutic Duplication: Same Drug Class",
        "trigger": {"type": "duplicate_class"},
        "min_drugs_matching": 2,
        "risk_category": "duplication",
        "base_severity": "moderate",
        "patient_modifiers": {},
        "patient_explanation": "You have two medicines from the same group. This usually means one was prescribed without knowing you were already on the other. Check with your doctor.",
        "doctor_explanation": "Two drugs from same therapeutic class (e.g., two antihypertensives from same class, two antiplatelets) prescribed, possibly by different doctors. Review for intended vs unintended duplication.",
        "evidence": "Internal detection: therapeutic class deduplication",
        "action": "Verify prescribing rationale. Usually one should be discontinued.",
        "lock_compartment_class": None,
        "monitoring": "Reconcile with all prescribing physicians."
    },

    # ─── CONTROLLED SUBSTANCES ───────────────────────────────────
    {
        "id": "CTRL-001",
        "name": "Controlled Substance (Schedule H1 / X) Present",
        "trigger": {"schedule": ["H1", "X"]},
        "min_drugs_matching": 1,
        "risk_category": "controlled",
        "base_severity": "moderate",
        "patient_modifiers": {},
        "patient_explanation": "One of your medicines is a controlled substance. It must only be taken exactly as prescribed. Never share it or use extra doses.",
        "doctor_explanation": "Patient list contains Schedule H1/X drug. Flag for monitoring: verify valid prescription, check for dependency indicators, ensure appropriate dosing.",
        "evidence": "Drugs and Cosmetics Act, India; Schedule H1 notification 2013",
        "action": "Confirm valid prescription. Document dose and duration.",
        "lock_compartment_class": None,
        "monitoring": "Periodic prescription validation. Watch for dose escalation requests."
    },

    # ─── FOOD INTERACTIONS ───────────────────────────────────────
    {
        "id": "FOOD-001",
        "name": "Grapefruit + Calcium Channel Blocker / Statin",
        "trigger": {"food": "grapefruit_juice", "allopathic_class": ["calcium_channel_blocker", "statin"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "high",
        "patient_modifiers": {},
        "patient_explanation": "Grapefruit juice increases the amount of your blood pressure or cholesterol medicine in your blood by up to 5 times. This can cause dangerous side effects. Avoid grapefruit completely.",
        "doctor_explanation": "Grapefruit furanocoumarins irreversibly inhibit intestinal CYP3A4 for 24-72h. Single glass → 3-5x AUC increase for amlodipine, felodipine, and statins.",
        "evidence": "Bailey et al., CMAJ 2013; Grapefruit-drug interactions list, FDA",
        "action": "Switch to orange juice or other fruit juice. No other dose adjustment needed if grapefruit is avoided.",
        "lock_compartment_class": None,
        "monitoring": "BP monitoring if grapefruit consumption continues."
    },
    {
        "id": "FOOD-002",
        "name": "Dairy + Fluoroquinolone / Tetracycline",
        "trigger": {"food": "dairy", "allopathic_class": ["fluoroquinolone", "tetracycline"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "high",
        "patient_modifiers": {},
        "patient_explanation": "Milk, curd, and cheese can reduce your antibiotic's effect by 50-70%. Take the antibiotic 2 hours before or 6 hours after eating dairy products.",
        "doctor_explanation": "Calcium chelation reduces quinolone and tetracycline absorption by 30-70%. Critical for adequate antibiotic levels for treatment success.",
        "evidence": "Polk et al., Antimicrob Agents Chemother 1989; Neuvonen, Drugs 1976",
        "action": "Counsel patient on timing. Administer antibiotic on empty stomach or 2h away from calcium-rich foods.",
        "lock_compartment_class": None,
        "monitoring": "Clinical response to antibiotic (fever, symptoms)."
    },

    # ── NSAID + CORTICOSTEROID (from Joint Line Orthopaedic prescription) ────
    {
        "id": "GI-002",
        "name": "NSAID + Corticosteroid (GI Bleed Risk)",
        "trigger": {"classes": ["nsaid", "corticosteroid"]},
        "min_drugs_matching": 2,
        "risk_category": "bleeding",
        "base_severity": "high",
        "patient_modifiers": {
            "age_gt_65": +1,
            "ckd": +1,
            "concurrent_anticoagulant": +2
        },
        "patient_explanation": (
            "You are taking a pain medicine (NSAID) and a steroid together. "
            "This combination significantly increases the risk of stomach bleeding or ulcers. "
            "Always take both with food. Tell your doctor if you get stomach pain, black stools, or vomiting blood."
        ),
        "doctor_explanation": (
            "NSAID + corticosteroid: 15x increased GI ulcer risk (Piper et al., BMJ 1991). "
            "Both independently damage gastric mucosa — NSAIDs by inhibiting COX-1/prostaglandin "
            "synthesis, corticosteroids by reducing mucosal repair and increasing acid secretion. "
            "Combined risk exceeds sum of individual risks. A PPI (rabeprazole, pantoprazole) "
            "MUST be co-prescribed — if not already, add it."
        ),
        "evidence": "Piper et al., BMJ 1991; Gabriel et al., Ann Intern Med 1991; Beers Criteria 2023",
        "action": "Ensure PPI is co-prescribed (rabeprazole 20mg or pantoprazole 40mg). Take both medicines with food. Avoid alcohol. Warn patient to report black/tarry stools immediately.",
        "lock_compartment_class": "nsaid",
        "monitoring": "Watch for: black/tarry stools, coffee-ground vomiting, sudden stomach pain. H. pylori test if prolonged combination needed."
    },

    # ── CORTICOSTEROID + ANTIDIABETIC (steroid raises blood sugar) ───────────
    {
        "id": "DM-001",
        "name": "Corticosteroid + Antidiabetic (Steroid Hyperglycaemia)",
        "trigger": {"classes": ["corticosteroid", "antidiabetic"]},
        "min_drugs_matching": 2,
        "risk_category": "hyperglycaemia",
        "base_severity": "moderate",
        "patient_modifiers": {
            "age_gt_65": +1
        },
        "patient_explanation": (
            "Steroids raise blood sugar levels. If you also take diabetes medicine, "
            "your sugar control may become unpredictable — it may go high during the steroid course. "
            "Check your blood sugar more often while taking the steroid."
        ),
        "doctor_explanation": (
            "Glucocorticoids cause steroid-induced hyperglycaemia via: increased hepatic gluconeogenesis, "
            "reduced peripheral glucose uptake, and impaired insulin secretion. Effect is dose-dependent "
            "and peaks 4–8 hours post-dose. May unmask latent T2DM. Antidiabetic dose adjustment "
            "often required during steroid course."
        ),
        "evidence": "Clore & Thurby-Hay, Endocr Pract 2009; ADA Standards of Medical Care 2023",
        "action": "Increase blood glucose monitoring frequency (post-meal). Consider dose adjustment of antidiabetic. Taper steroids gradually — do not stop abruptly.",
        "lock_compartment_class": None,
        "monitoring": "Fasting and post-meal glucose daily during steroid course. HbA1c at next follow-up."
    }
]

from phase2_rules import PHASE2_RULES
INTERACTION_RULES = INTERACTION_RULES + PHASE2_RULES

from phase3_rules import PHASE3_RULES
INTERACTION_RULES = INTERACTION_RULES + PHASE3_RULES

