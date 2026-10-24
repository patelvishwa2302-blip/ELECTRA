# phase2_rules.py
# Electra - Phase 2 rules: pregnancy, breastfeeding, GI-bleed history, heart failure.
#
# HOW TO INSTALL (2 lines, at the very END of rules.py):
#
#     from phase2_rules import PHASE2_RULES
#     INTERACTION_RULES = INTERACTION_RULES + PHASE2_RULES
#
# Rule count goes from 14 -> 22. Update that number everywhere (deck, doc,
# video script, run sheet).
#
# Every rule here sets "refer_to_doctor": True - these are conditions where the
# app must NOT tell the patient what to do. It identifies the risk and sends
# them to a doctor.

PHASE2_RULES = [
    {
        "id": "PREG-001",
        "name": "NSAID in Pregnancy",
        "trigger": {"classes": ["nsaid"], "patient_condition": "pregnant"},
        "min_drugs_matching": 1,
        "risk_category": "pregnancy",
        "base_severity": "critical",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are pregnant, and this painkiller (the ibuprofen/diclofenac type) is not considered safe in pregnancy. It can affect your baby's kidneys and circulation. Do not take it — please speak to your doctor today about a safe option for pain or fever.",
        "doctor_explanation": "NSAIDs in pregnancy: avoid from 20 weeks (FDA Safety Communication, Oct 2020) due to fetal renal dysfunction and oligohydramnios; third-trimester use risks premature closure of the ductus arteriosus. Paracetamol is the preferred analgesic.",
        "evidence": "FDA Drug Safety Communication (Oct 2020); NICE CKS: NSAIDs in pregnancy",
        "action": "Do not take this medicine. Consult your doctor or obstetrician today for a safe alternative.",
        "lock_compartment_class": "nsaid",
        "monitoring": "Do not restart it without your doctor's approval."
    },
    {
        "id": "PREG-002",
        "name": "ACE inhibitor / ARB in Pregnancy",
        "trigger": {"classes": ["ace_inhibitor", "arb"], "patient_condition": "pregnant"},
        "min_drugs_matching": 1,
        "risk_category": "pregnancy",
        "base_severity": "critical",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are pregnant, and this blood-pressure medicine (the -pril or -sartan type) can harm your baby's kidneys. It should not be taken in pregnancy. Please contact your doctor straight away — do not stop or change any medicine on your own.",
        "doctor_explanation": "ACE inhibitors/ARBs are contraindicated in pregnancy (2nd/3rd trimester fetotoxicity: renal dysgenesis, oligohydramnios, skull hypoplasia). Switch to a pregnancy-safe antihypertensive (e.g. labetalol or methyldopa) under supervision.",
        "evidence": "NICE NG133 (Hypertension in pregnancy); EMA and FDA product labelling",
        "action": "Contact your doctor immediately. Do not change any medicine yourself.",
        "lock_compartment_class": None,
        "monitoring": "Doctor review required before the next dose."
    },
    {
        "id": "PREG-003",
        "name": "Warfarin / Acenocoumarol in Pregnancy",
        "trigger": {"classes": ["anticoagulant"], "patient_condition": "pregnant"},
        "min_drugs_matching": 1,
        "risk_category": "pregnancy",
        "base_severity": "critical",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are pregnant, and this blood thinner can harm your baby's development. It must be reviewed by your doctor urgently — please contact them today. Do not stop it on your own.",
        "doctor_explanation": "Warfarin/acenocoumarol are teratogenic (warfarin embryopathy) and cause fetal bleeding. NICE recommends switching to low-molecular-weight heparin in pregnancy. Urgent specialist review.",
        "evidence": "NICE NG133; warfarin embryopathy literature",
        "action": "Contact your doctor or obstetrician immediately for a medicine review.",
        "lock_compartment_class": None,
        "monitoring": "Specialist review; do not stop the medicine yourself."
    },
    {
        "id": "PREG-004",
        "name": "Statin in Pregnancy",
        "trigger": {"classes": ["statin"], "patient_condition": "pregnant"},
        "min_drugs_matching": 1,
        "risk_category": "pregnancy",
        "base_severity": "high",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are pregnant, and cholesterol medicines (statins) are usually stopped during pregnancy. Please speak to your doctor about this before your next dose.",
        "doctor_explanation": "Statins are contraindicated in pregnancy (cholesterol is required for fetal development). Usually discontinued; treat dyslipidaemia with diet during pregnancy.",
        "evidence": "NICE CKS; FDA product labelling",
        "action": "Speak to your doctor about whether this should be stopped.",
        "lock_compartment_class": None,
        "monitoring": "Doctor review."
    },
    {
        "id": "PREG-005",
        "name": "Tetracycline / Doxycycline in Pregnancy",
        "trigger": {"classes": ["tetracycline"], "patient_condition": "pregnant"},
        "min_drugs_matching": 1,
        "risk_category": "pregnancy",
        "base_severity": "high",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are pregnant, and this antibiotic (the tetracycline/doxycycline type) can affect your baby's teeth and bones. Please ask your doctor for a different antibiotic.",
        "doctor_explanation": "Tetracyclines deposit in fetal teeth and bone (dental staining, growth effects); avoided in pregnancy unless a serious infection leaves no alternative.",
        "evidence": "BNF; NICE CKS: antibiotics in pregnancy",
        "action": "Ask your doctor for a pregnancy-safe antibiotic.",
        "lock_compartment_class": None,
        "monitoring": "Doctor review."
    },

    # ─── BREASTFEEDING ────────────────────────────────────────────────────
    {
        "id": "LACT-001",
        "name": "Opioid while Breastfeeding",
        "trigger": {"classes": ["opioid"], "patient_condition": "breastfeeding"},
        "min_drugs_matching": 1,
        "risk_category": "breastfeeding",
        "base_severity": "high",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You are breastfeeding, and this painkiller (the codeine/tramadol type) can pass into your milk and make your baby very sleepy or cause breathing problems. Please do not take it — speak to your doctor about a safer option.",
        "doctor_explanation": "Codeine in breastfeeding: FDA warning (2007) — ultra-rapid CYP2D6 metabolisers convert codeine to morphine, causing infant opioid toxicity and death. Tramadol carries the same concern. Avoid opioids in breastfeeding where possible.",
        "evidence": "FDA Drug Safety Communication (2007); LactMed",
        "action": "Do not take this medicine. Ask your doctor for a breastfeeding-safe painkiller.",
        "lock_compartment_class": None,
        "monitoring": "Watch the baby for excessive sleepiness or poor feeding — seek help urgently if seen."
    },

    # ─── GI BLEEDING HISTORY ──────────────────────────────────────────────
    {
        "id": "GI-001",
        "name": "NSAID with History of Stomach Ulcer / GI Bleeding",
        "trigger": {"classes": ["nsaid"], "patient_condition": "gi_bleed_history"},
        "min_drugs_matching": 1,
        "risk_category": "bleeding",
        "base_severity": "critical",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You have had a stomach ulcer or bleeding in the stomach before, and this painkiller (the ibuprofen/diclofenac type) can cause it to happen again. Please do not take it — speak to your doctor about a safer option.",
        "doctor_explanation": "NSAIDs are contraindicated with a history of peptic ulceration or GI bleeding (Beers Criteria 2023; NICE CKS). If an NSAID is unavoidable, add gastroprotection and review continuously.",
        "evidence": "Beers Criteria 2023 (AGS); NICE CKS: NSAIDs and GI risk",
        "action": "Do not take this painkiller. Ask your doctor about a stomach-safe alternative.",
        "lock_compartment_class": "nsaid",
        "monitoring": "Watch for black or tarry stools, vomiting blood, or stomach pain — seek help urgently."
    },

    # ─── HEART FAILURE ────────────────────────────────────────────────────
    {
        "id": "HF-001",
        "name": "NSAID in Heart Failure",
        "trigger": {"classes": ["nsaid"], "patient_condition": "heart_failure"},
        "min_drugs_matching": 1,
        "risk_category": "cardiac",
        "base_severity": "high",
        "patient_modifiers": {},
        "refer_to_doctor": True,
        "patient_explanation": "You have heart failure, and this painkiller (the ibuprofen/diclofenac type) can make your body hold on to fluid and worsen your heart condition. Please speak to your doctor before taking it.",
        "doctor_explanation": "NSAIDs cause sodium and fluid retention and can precipitate decompensation in heart failure; they also blunt diuretic and ACE-inhibitor efficacy. Avoid in heart failure (EMA/NICE advice).",
        "evidence": "EMA advice on NSAIDs in heart failure; NICE CKS",
        "action": "Speak to your doctor about a heart-safe alternative for pain.",
        "lock_compartment_class": None,
        "monitoring": "Watch for weight gain, ankle swelling, or breathlessness — seek help if they worsen."
    },
]
