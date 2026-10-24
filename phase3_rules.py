# phase3_rules.py
# Electra - Phase 3 rules: the five drug-food interactions that had no rule.
#
# WHY THIS EXISTS
#   Your food_db.py already contains 8 food interactions, but only 2 of them
#   (grapefruit, dairy) had a matching rule in rules.py. The other five could
#   never fire - even though four of them are already checkboxes on the
#   dashboard. This file wires them up.
#
# HOW TO INSTALL (2 lines, at the very END of rules.py):
#
#     from phase3_rules import PHASE3_RULES
#     INTERACTION_RULES = INTERACTION_RULES + PHASE3_RULES
#
# Rule count goes from 24 -> 29. Update that number everywhere.
#
# NOTE ON CLASS NAMES
#   The banana/coconut-water entry in food_db.py lists
#   "potassium_sparing_diuretic", which is not a class in database.py. The rule
#   below uses "diuretic" instead, so Aldactone (spironolactone) matches too.

PHASE3_RULES = [
    {
        "id": "FOOD-003",
        "name": "Alcohol + Diabetes / Antibiotic / Painkiller / Sleeping Tablet",
        "trigger": {"food": "alcohol",
                    "allopathic_class": ["antidiabetic", "antibiotic", "analgesic", "benzodiazepine"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "high",
        "patient_modifiers": {},
        "patient_explanation": "Do not drink alcohol while you are taking these medicines. Alcohol can cause serious problems with them - very low blood sugar, liver damage, a bad reaction with flushing and vomiting, or extreme drowsiness.",
        "doctor_explanation": "Alcohol + metformin: lactic acidosis risk. Alcohol + metronidazole: disulfiram-like reaction. Alcohol + paracetamol: CYP2E1 induction causing toxic NAPQI accumulation. Alcohol + benzodiazepines: additive CNS and respiratory depression.",
        "evidence": "BNF: interactions with alcohol; FDA labelling (metronidazole-alcohol reaction)",
        "action": "Avoid all alcohol until these medicines are finished. Ask your doctor if you are unsure.",
        "lock_compartment_class": None,
        "monitoring": "Watch for flushing, vomiting, drowsiness, or very low blood sugar."
    },
    {
        "id": "FOOD-004",
        "name": "Vitamin K Vegetables + Blood Thinner",
        "trigger": {"food": "high_vitamin_k", "allopathic_class": ["anticoagulant"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "moderate",
        "patient_modifiers": {},
        "patient_explanation": "You take a blood-thinning medicine. Eating a lot of spinach, methi or other green leafy vegetables can make it work less well. Keep your diet steady - do not suddenly eat much more or much less of them.",
        "doctor_explanation": "A sudden increase in dietary vitamin K competes at the VKOR enzyme, reducing the anticoagulant effect and dropping the INR into the subtherapeutic range. Advise consistent (not zero) vitamin K intake.",
        "evidence": "Holbrook et al., Arch Intern Med 2005; NICE CKS: anticoagulation and diet",
        "action": "Keep green leafy vegetable intake consistent from day to day. Tell your doctor if your diet changes.",
        "lock_compartment_class": None,
        "monitoring": "INR monitoring."
    },
    {
        "id": "FOOD-005",
        "name": "High-Potassium Foods + BP Medicine",
        "trigger": {"food": "banana_coconut_water",
                    "allopathic_class": ["ace_inhibitor", "arb", "diuretic"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "high",
        "patient_modifiers": {},
        "patient_explanation": "While you take this blood-pressure medicine, do not eat too many bananas, or drink too much coconut water or orange juice. They raise the potassium in your body, which can affect your heart.",
        "doctor_explanation": "ACE inhibitors and ARBs reduce aldosterone, causing potassium retention. Combined with a high-potassium diet this risks hyperkalaemia (K > 6.5 mEq/L) and arrhythmia. Monitor serum potassium.",
        "evidence": "MHRA Drug Safety Update: ACE inhibitors and ARBs - hyperkalaemia; NICE CKS",
        "action": "Limit bananas, coconut water and orange juice. Ask your doctor when to check your potassium.",
        "lock_compartment_class": None,
        "monitoring": "Potassium level; watch for palpitations or muscle weakness."
    },
    {
        "id": "FOOD-006",
        "name": "Morning Milk + Thyroid Tablet",
        "trigger": {"food": "milk_thyroid", "allopathic_class": ["thyroid_hormone"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "moderate",
        "patient_modifiers": {},
        "patient_explanation": "Take your thyroid tablet first thing in the morning on an empty stomach, with plain water. Wait at least 30 minutes before milk, tea or breakfast.",
        "doctor_explanation": "Calcium in milk chelates levothyroxine, reducing absorption by 17-40%. Administer at least 30-60 minutes before calcium-containing food or drink.",
        "evidence": "BNF: levothyroxine interactions; NICE CKS: hypothyroidism",
        "action": "Take the tablet on an empty stomach, and wait 30 minutes before milk or tea.",
        "lock_compartment_class": None,
        "monitoring": "TSH at follow-up."
    },
    {
        "id": "FOOD-007",
        "name": "Licorice / Mulethi + BP Medicine",
        "trigger": {"food": "liquorice_candy", "allopathic_class": ["antihypertensive"]},
        "min_drugs_matching": 1,
        "risk_category": "food_drug",
        "base_severity": "moderate",
        "patient_modifiers": {},
        "patient_explanation": "Licorice-flavoured sweets, mulethi or licorice drinks can raise your blood pressure and cancel the effect of your blood pressure medicine. Avoid them.",
        "doctor_explanation": "Glycyrrhizin inhibits 11-beta-HSD2, producing pseudohyperaldosteronism: sodium retention and hypertension that resists antihypertensive treatment.",
        "evidence": "EMA guidance on glycyrrhizin intake; Sigurjonsdottir et al., J Hum Hypertens 2001",
        "action": "Stop licorice sweets and drinks. Tell your doctor if your blood pressure stays high.",
        "lock_compartment_class": None,
        "monitoring": "Home blood pressure monitoring."
    },
]
