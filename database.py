# database.py
# Electra - Indian medicine database: 50 medicines (brand -> generic -> class)
#
# COMPLETE v2 - all 50 medicines (demo 6 + Tier 2 + Tier 3).
# The first 6 entries and the BRAND_ALIASES / lookup functions are identical
# to the guide's originals. The remaining 44 fill the Tier 2 and Tier 3 lists
# from the backend guide, so every rule, the accuracy suite, and the OCR
# matcher can see the full cabinet.
#
# organ_load: 0-3 per organ - feeds the burden score.
# schedule: "OTC", "H", "H1" (controlled - Schedule H1), "X".
#   Note: alprazolam and codeine are Schedule H1 - this makes CTRL-001 fire
#   live, which the accuracy suite now covers.

MEDICINES = {

    # ==================== DEMO CRITICAL (6) ====================

    "ecosprin_75": {
        "brand": "Ecosprin 75",
        "generic": "Aspirin",
        "strength": "75mg",
        "therapeutic_class": "antiplatelet",
        "organ_load": {"kidney": 2, "liver": 1, "cardiac": 1, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["GI bleeding", "bruising", "tinnitus"],
        "timing": "morning_with_food",
        "avoid_with": ["alcohol", "nsaid", "other_antiplatelet"],
        "notes": "Blocks aspirin's cardioprotective effect if given with ibuprofen"
    },

    "brufen_400": {
        "brand": "Brufen 400",
        "generic": "Ibuprofen",
        "strength": "400mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["GI bleeding", "renal impairment", "fluid retention"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "diuretic", "ace_inhibitor"],
        "notes": "Nephrotoxic in CKD. Contraindicated with anticoagulants."
    },

    "glycomet_500": {
        "brand": "Glycomet 500",
        "generic": "Metformin",
        "strength": "500mg",
        "therapeutic_class": "antidiabetic",
        "organ_load": {"kidney": 3, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["lactic acidosis (if CKD)", "nausea", "diarrhoea"],
        "timing": "with_meals",
        "avoid_with": ["alcohol", "contrast_dye"],
        "notes": "STOP if eGFR < 30. Lactic acidosis risk in CKD."
    },

    "stamlo_5": {
        "brand": "Stamlo 5",
        "generic": "Amlodipine",
        "strength": "5mg",
        "therapeutic_class": "calcium_channel_blocker",
        "organ_load": {"kidney": 0, "liver": 2, "cardiac": 2, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["ankle oedema", "headache", "flushing"],
        "timing": "any_time",
        "avoid_with": ["grapefruit_juice"],
        "notes": "Grapefruit juice raises amlodipine level 5x via CYP3A4 inhibition"
    },

    "crocin_500": {
        "brand": "Crocin 500",
        "generic": "Paracetamol",
        "strength": "500mg",
        "therapeutic_class": "analgesic",
        "organ_load": {"kidney": 1, "liver": 2, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["hepatotoxicity (overdose)", "nausea"],
        "timing": "any_time",
        "avoid_with": ["alcohol"],
        "notes": "Overdose causes liver failure. Safe substitute for NSAIDs in elderly."
    },

    "shelcal_500": {
        "brand": "Shelcal 500",
        "generic": "Calcium Carbonate",
        "strength": "500mg",
        "therapeutic_class": "supplement",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["constipation", "hypercalcaemia"],
        "timing": "after_meals",
        "avoid_with": ["quinolone_antibiotic", "tetracycline", "levothyroxine"],
        "notes": "Calcium chelates quinolones and tetracyclines -> reduces absorption by 70%"
    },

    # ==================== TIER 2 (14) ====================

    "acitrom_2": {
        "brand": "Acitrom 2",
        "generic": "Acenocoumarol",
        "strength": "2mg",
        "therapeutic_class": "anticoagulant",
        "organ_load": {"kidney": 1, "liver": 2, "cardiac": 0, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["bleeding", "skin necrosis (rare)"],
        "timing": "evening",
        "avoid_with": ["nsaid", "antiplatelet", "alcohol", "ayurvedic_herbs"],
        "notes": "Vitamin K antagonist. Monthly INR monitoring essential."
    },

    "clopilet_75": {
        "brand": "Clopilet 75",
        "generic": "Clopidogrel",
        "strength": "75mg",
        "therapeutic_class": "antiplatelet",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 1, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["bleeding", "bruising"],
        "timing": "morning",
        "avoid_with": ["anticoagulant", "nsaid"],
        "notes": "Do not stop before surgery without doctor's advice."
    },

    "lasix_40": {
        "brand": "Lasix 40",
        "generic": "Furosemide",
        "strength": "40mg",
        "therapeutic_class": "diuretic",
        "organ_load": {"kidney": 3, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["dehydration", "low potassium", "gout"],
        "timing": "morning",
        "avoid_with": ["nsaid", "aminoglycosides"],
        "notes": "Check potassium. Triple-whammy risk with NSAID + ACE inhibitor."
    },

    "enam_5": {
        "brand": "Enam 5",
        "generic": "Enalapril",
        "strength": "5mg",
        "therapeutic_class": "ace_inhibitor",
        "organ_load": {"kidney": 2, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["dry cough", "high potassium", "angioedema (rare)"],
        "timing": "any_time",
        "avoid_with": ["nsaid", "potassium_supplements"],
        "notes": "ACE inhibitor. Avoid in pregnancy."
    },

    "telma_40": {
        "brand": "Telma 40",
        "generic": "Telmisartan",
        "strength": "40mg",
        "therapeutic_class": "arb",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["dizziness", "high potassium"],
        "timing": "any_time",
        "avoid_with": ["nsaid", "potassium_supplements"],
        "notes": "ARB. Monitor potassium if combined with spironolactone."
    },

    "alzolam_0_25": {
        "brand": "Alzolam 0.25",
        "generic": "Alprazolam",
        "strength": "0.25mg",
        "therapeutic_class": "benzodiazepine",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 3},
        "schedule": "H1",
        "side_effects": ["drowsiness", "dependence", "memory impairment"],
        "timing": "night",
        "avoid_with": ["opioid", "alcohol", "other_sedatives"],
        "notes": "Schedule H1 controlled. Fall risk in elderly. Never combine with opioids."
    },

    "tramazac_50": {
        "brand": "Tramazac 50",
        "generic": "Tramadol",
        "strength": "50mg",
        "therapeutic_class": "opioid",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["nausea", "constipation", "dizziness"],
        "timing": "with_food",
        "avoid_with": ["ssri", "benzodiazepine", "alcohol"],
        "notes": "Serotonin syndrome risk with SSRIs. Respiratory depression with benzodiazepines."
    },

    "azithral_500": {
        "brand": "Azithral 500",
        "generic": "Azithromycin",
        "strength": "500mg",
        "therapeutic_class": "antibiotic",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["nausea", "diarrhoea", "QT prolongation (rare)"],
        "timing": "empty_stomach",
        "avoid_with": ["antacids"],
        "notes": "Macrolide. Take 1 hour before food."
    },

    "ciplox_500": {
        "brand": "Ciplox 500",
        "generic": "Ciprofloxacin",
        "strength": "500mg",
        "therapeutic_class": "fluoroquinolone",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["tendon rupture (rare)", "QT prolongation", "blood sugar swings"],
        "timing": "any_time",
        "avoid_with": ["dairy", "calcium_supplements", "sulfonylurea"],
        "notes": "Avoid with milk. FDA 2018: blood sugar swings with diabetes medicines."
    },

    "fludac_20": {
        "brand": "Fludac 20",
        "generic": "Fluoxetine",
        "strength": "20mg",
        "therapeutic_class": "ssri",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 1, "cns": 1},
        "schedule": "H",
        "side_effects": ["nausea", "insomnia", "serotonin syndrome (with tramadol)"],
        "timing": "morning",
        "avoid_with": ["tramadol", "maoi", "other_ssri"],
        "notes": "SSRI. Serotonin syndrome risk with tramadol."
    },

    "amaryl_2": {
        "brand": "Amaryl 2",
        "generic": "Glimepiride",
        "strength": "2mg",
        "therapeutic_class": "sulfonylurea",
        "organ_load": {"kidney": 2, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 2},
        "schedule": "H",
        "side_effects": ["hypoglycaemia", "weight gain"],
        "timing": "morning_with_food",
        "avoid_with": ["fluoroquinolone", "alcohol", "beta_blocker"],
        "notes": "Hypoglycaemia risk. Beta-blockers mask the warning signs."
    },

    "metolar_25": {
        "brand": "Metolar 25",
        "generic": "Metoprolol",
        "strength": "25mg",
        "therapeutic_class": "beta_blocker",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["fatigue", "bradycardia", "masked hypoglycaemia"],
        "timing": "morning",
        "avoid_with": ["verapamil", "diltiazem"],
        "notes": "Masks hypoglycaemia symptoms in diabetics."
    },

    "pantop_40": {
        "brand": "Pantop 40",
        "generic": "Pantoprazole",
        "strength": "40mg",
        "therapeutic_class": "ppi",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["B12 deficiency (long-term)", "fracture risk (long-term)"],
        "timing": "morning_empty_stomach",
        "avoid_with": ["clopidogrel"],
        "notes": "Long-term use reduces calcium and B12 absorption."
    },

    "dolo_650": {
        "brand": "Dolo 650",
        "generic": "Paracetamol",
        "strength": "650mg",
        "therapeutic_class": "analgesic",
        "organ_load": {"kidney": 1, "liver": 2, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["hepatotoxicity (overdose)"],
        "timing": "any_time",
        "avoid_with": ["alcohol", "other_paracetamol_brands"],
        "notes": "Same medicine as Crocin - never take both together."
    },

    # ==================== TIER 3 (30) ====================

    "warfarin_5": {
        "brand": "Warfarin 5",
        "generic": "Warfarin",
        "strength": "5mg",
        "therapeutic_class": "anticoagulant",
        "organ_load": {"kidney": 1, "liver": 2, "cardiac": 0, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["bleeding", "skin necrosis (rare)"],
        "timing": "evening",
        "avoid_with": ["nsaid", "antiplatelet", "ayurvedic_herbs"],
        "notes": "INR monitoring monthly. Many herbs potentiate its effect."
    },

    "voveran_50": {
        "brand": "Voveran 50",
        "generic": "Diclofenac",
        "strength": "50mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["GI bleeding", "renal impairment", "cardiac events"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "diuretic", "ace_inhibitor"],
        "notes": "Highest GI-risk NSAI. Avoid in CKD and elderly."
    },

    "codeine_syrup": {
        "brand": "Codeine Cough Syrup",
        "generic": "Codeine",
        "strength": "100ml",
        "therapeutic_class": "opioid",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 3},
        "schedule": "H1",
        "side_effects": ["dependence", "constipation", "respiratory depression"],
        "timing": "as_needed",
        "avoid_with": ["benzodiazepine", "alcohol", "other_sedatives"],
        "notes": "Schedule H1 controlled. Never with benzodiazepines."
    },

    "avil_25": {
        "brand": "Avil 25",
        "generic": "Chlorpheniramine",
        "strength": "25mg",
        "therapeutic_class": "sedating_antihistamine",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["drowsiness", "dry mouth", "urinary retention (elderly men)"],
        "timing": "night",
        "avoid_with": ["benzodiazepine", "opioid", "alcohol"],
        "notes": "Beers Criteria: avoid sedating antihistamines in elderly."
    },

    "serenace_5": {
        "brand": "Serenace 5",
        "generic": "Haloperidol",
        "strength": "5mg",
        "therapeutic_class": "antipsychotic",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 2, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["extrapyramidal symptoms", "QT prolongation", "sedation"],
        "timing": "with_food",
        "avoid_with": ["fluoroquinolone", "other_qt_drugs"],
        "notes": "QT prolongation. Avoid in elderly (Beers Criteria)."
    },

    "emeset_4": {
        "brand": "Emeset 4",
        "generic": "Ondansetron",
        "strength": "4mg",
        "therapeutic_class": "antiemetic",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["headache", "constipation", "QT prolongation (high doses)"],
        "timing": "any_time",
        "avoid_with": ["other_qt_drugs"],
        "notes": "QT prolongation at higher doses."
    },

    "serta_50": {
        "brand": "Serta 50",
        "generic": "Sertraline",
        "strength": "50mg",
        "therapeutic_class": "ssri",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 1, "cns": 1},
        "schedule": "H",
        "side_effects": ["nausea", "sexual dysfunction", "serotonin syndrome (with tramadol)"],
        "timing": "morning",
        "avoid_with": ["tramadol", "maoi"],
        "notes": "SSRI. Serotonin syndrome risk with tramadol."
    },

    "amiodarone_200": {
        "brand": "Amiodarone 200",
        "generic": "Amiodarone",
        "strength": "200mg",
        "therapeutic_class": "antiarrhythmic",
        "organ_load": {"kidney": 2, "liver": 3, "cardiac": 2, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["thyroid dysfunction", "pulmonary fibrosis", "QT prolongation"],
        "timing": "with_food",
        "avoid_with": ["other_qt_drugs", "digoxin"],
        "notes": "Multiple interactions. Raises digoxin levels."
    },

    "lanoxin_0_25": {
        "brand": "Lanoxin 0.25",
        "generic": "Digoxin",
        "strength": "0.25mg",
        "therapeutic_class": "cardiac_glycoside",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["nausea", "visual halos", "arrhythmia"],
        "timing": "morning",
        "avoid_with": ["amiodarone", "low_potassium_states"],
        "notes": "Narrow therapeutic index. Monitor levels."
    },

    "gabapin_300": {
        "brand": "Gabapin 300",
        "generic": "Gabapentin",
        "strength": "300mg",
        "therapeutic_class": "anticonvulsant",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 0, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["dizziness", "drowsiness", "weight gain"],
        "timing": "night",
        "avoid_with": ["benzodiazepine", "opioid", "alcohol"],
        "notes": "Additive sedation with CNS depressants."
    },

    "lithosun_400": {
        "brand": "Lithosun 400",
        "generic": "Lithium",
        "strength": "400mg",
        "therapeutic_class": "mood_stabilizer",
        "organ_load": {"kidney": 3, "liver": 0, "cardiac": 2, "bleeding": 0, "cns": 2},
        "schedule": "H",
        "side_effects": ["tremor", "hypothyroidism", "toxicity"],
        "timing": "with_meals",
        "avoid_with": ["nsaid", "ace_inhibitor", "diuretic"],
        "notes": "NSAIDs and ACE inhibitors raise lithium levels dangerously."
    },

    "catapres_100": {
        "brand": "Catapres 100",
        "generic": "Clonidine",
        "strength": "100mcg",
        "therapeutic_class": "antihypertensive",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["dry mouth", "drowsiness", "rebound hypertension"],
        "timing": "night",
        "avoid_with": ["beta_blocker"],
        "notes": "Never stop suddenly when also on a beta-blocker."
    },

    "eptoin_100": {
        "brand": "Eptoin 100",
        "generic": "Phenytoin",
        "strength": "100mg",
        "therapeutic_class": "anticonvulsant",
        "organ_load": {"kidney": 0, "liver": 3, "cardiac": 0, "bleeding": 0, "cns": 2},
        "schedule": "H",
        "side_effects": ["gum hypertrophy", "ataxia", "osteomalacia"],
        "timing": "with_food",
        "avoid_with": ["warfarin", "many_enzyme_interactions"],
        "notes": "Enzyme inducer - reduces levels of many other drugs."
    },

    "tegretol_200": {
        "brand": "Tegretol 200",
        "generic": "Carbamazepine",
        "strength": "200mg",
        "therapeutic_class": "anticonvulsant",
        "organ_load": {"kidney": 0, "liver": 3, "cardiac": 1, "bleeding": 0, "cns": 3},
        "schedule": "H",
        "side_effects": ["drowsiness", "hyponatraemia", "rash"],
        "timing": "with_food",
        "avoid_with": ["warfarin", "oral_contraceptives"],
        "notes": "Enzyme inducer - many interactions."
    },

    "thyronorm_50": {
        "brand": "Thyronorm 50",
        "generic": "Levothyroxine",
        "strength": "50mcg",
        "therapeutic_class": "thyroid_hormone",
        "organ_load": {"kidney": 0, "liver": 0, "cardiac": 2, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["palpitations", "osteoporosis (long-term)"],
        "timing": "morning_empty_stomach",
        "avoid_with": ["calcium_supplements", "ashwagandha"],
        "notes": "Take on empty stomach. Separate from calcium by 4 hours."
    },

    "wysolone_10": {
        "brand": "Wysolone 10",
        "generic": "Prednisolone",
        "strength": "10mg",
        "therapeutic_class": "corticosteroid",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 1, "bleeding": 1, "cns": 2},
        "schedule": "H",
        "side_effects": ["hyperglycaemia", "osteoporosis", "infections"],
        "timing": "morning_with_food",
        "avoid_with": ["nsaid", "diabetes_medicines"],
        "notes": "Raises blood sugar. Never stop suddenly."
    },

    "hcq_200": {
        "brand": "HCQ 200",
        "generic": "Hydroxychloroquine",
        "strength": "200mg",
        "therapeutic_class": "antimalarial",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["retinopathy (long-term)", "hypoglycaemia"],
        "timing": "with_food",
        "avoid_with": ["other_qt_drugs"],
        "notes": "Annual eye check for long-term use."
    },

    "lipitor_10": {
        "brand": "Lipitor 10",
        "generic": "Atorvastatin",
        "strength": "10mg",
        "therapeutic_class": "statin",
        "organ_load": {"kidney": 0, "liver": 2, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["muscle pain", "rhabdomyolysis (rare)"],
        "timing": "night",
        "avoid_with": ["grapefruit_juice", "clarithromycin"],
        "notes": "Grapefruit raises levels - avoid completely."
    },

    "rosuvas_10": {
        "brand": "Rosuvas 10",
        "generic": "Rosuvastatin",
        "strength": "10mg",
        "therapeutic_class": "statin",
        "organ_load": {"kidney": 1, "liver": 2, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["muscle pain", "proteinuria"],
        "timing": "night",
        "avoid_with": ["grapefruit_juice", "warfarin"],
        "notes": "Grapefruit raises levels - avoid."
    },

    "rimactane_450": {
        "brand": "Rimactane 450",
        "generic": "Rifampicin",
        "strength": "450mg",
        "therapeutic_class": "antibiotic",
        "organ_load": {"kidney": 0, "liver": 3, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["orange urine (harmless)", "hepatitis"],
        "timing": "empty_stomach",
        "avoid_with": ["warfarin", "oral_contraceptives", "many_drugs"],
        "notes": "Powerful enzyme inducer - reduces effect of dozens of medicines."
    },

    "inh_300": {
        "brand": "INH 300",
        "generic": "Isoniazid",
        "strength": "300mg",
        "therapeutic_class": "antibiotic",
        "organ_load": {"kidney": 0, "liver": 3, "cardiac": 1, "bleeding": 2, "cns": 2},
        "schedule": "H",
        "side_effects": ["hepatitis", "peripheral neuropathy"],
        "timing": "morning",
        "avoid_with": ["paracetamol"],
        "notes": "Take with vitamin B6. Liver monitoring."
    },

    "clindac_300": {
        "brand": "Clindac 300",
        "generic": "Clindamycin",
        "strength": "300mg",
        "therapeutic_class": "antibiotic",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["diarrhoea", "C. difficile colitis"],
        "timing": "with_food",
        "avoid_with": ["erythromycin"],
        "notes": "Stop and report if severe diarrhoea occurs."
    },

    "flagyl_400": {
        "brand": "Flagyl 400",
        "generic": "Metronidazole",
        "strength": "400mg",
        "therapeutic_class": "antibiotic",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["metallic taste", "nausea"],
        "timing": "with_food",
        "avoid_with": ["alcohol"],
        "notes": "Strictly no alcohol during and 48 hours after."
    },

    "tetracycline_500": {
        "brand": "Tetracycline 500",
        "generic": "Tetracycline",
        "strength": "500mg",
        "therapeutic_class": "tetracycline",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["photosensitivity", "tooth discoloration"],
        "timing": "empty_stomach",
        "avoid_with": ["dairy", "calcium_supplements", "antacids"],
        "notes": "Never with milk. Avoid sun exposure."
    },

    "doxt_100": {
        "brand": "Doxt 100",
        "generic": "Doxycycline",
        "strength": "100mg",
        "therapeutic_class": "tetracycline",
        "organ_load": {"kidney": 1, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["photosensitivity", "oesophagitis"],
        "timing": "with_water_upright",
        "avoid_with": ["dairy", "calcium_supplements", "antacids"],
        "notes": "Take with a full glass of water, stay upright 30 minutes."
    },

    "furadantin_100": {
        "brand": "Furadantin 100",
        "generic": "Nitrofurantoin",
        "strength": "100mg",
        "therapeutic_class": "urinary_antibiotic",
        "organ_load": {"kidney": 3, "liver": 0, "cardiac": 0, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["nausea", "pulmonary reactions (long-term)"],
        "timing": "with_food",
        "avoid_with": ["magnesium_antacids"],
        "notes": "Avoid if eGFR < 60 - ineffective and toxic."
    },

    "aldactone_25": {
        "brand": "Aldactone 25",
        "generic": "Spironolactone",
        "strength": "25mg",
        "therapeutic_class": "diuretic",
        "organ_load": {"kidney": 2, "liver": 0, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["high potassium", "gynaecomastia"],
        "timing": "morning_with_food",
        "avoid_with": ["ace_inhibitor", "arb", "potassium_supplements"],
        "notes": "Dangerous hyperkalaemia with ACE inhibitors / ARBs."
    },

    "hctz_25": {
        "brand": "HCTZ 25",
        "generic": "Hydrochlorothiazide",
        "strength": "25mg",
        "therapeutic_class": "diuretic",
        "organ_load": {"kidney": 3, "liver": 0, "cardiac": 2, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["low potassium", "low sodium", "gout"],
        "timing": "morning",
        "avoid_with": ["nsaid", "sulfonylurea"],
        "notes": "Reduces effectiveness of sulfonylureas. NSAIDs block its action."
    },

    "tenormin_50": {
        "brand": "Tenormin 50",
        "generic": "Atenolol",
        "strength": "50mg",
        "therapeutic_class": "beta_blocker",
        "organ_load": {"kidney": 1, "liver": 0, "cardiac": 2, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["fatigue", "cold extremities", "bradycardia"],
        "timing": "morning",
        "avoid_with": ["verapamil", "diltiazem"],
        "notes": "Masks hypoglycaemia in diabetics."
    },

    "cardace_5": {
        "brand": "Cardace 5",
        "generic": "Ramipril",
        "strength": "5mg",
        "therapeutic_class": "ace_inhibitor",
        "organ_load": {"kidney": 2, "liver": 0, "cardiac": 1, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["dry cough", "high potassium"],
        "timing": "any_time",
        "avoid_with": ["nsaid", "potassium_supplements"],
        "notes": "ACE inhibitor. Avoid in pregnancy."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDICINES FROM YOUR REAL PRESCRIPTIONS (added from uploaded photos)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Photo 4: Tab. Actinac-SP ────────────────────────────────────────────
    "actinac_sp": {
        "brand": "Actinac-SP",
        "generic": "Aceclofenac + Serratiopeptidase",
        "strength": "100mg+15mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["GI bleeding", "renal impairment", "fluid retention"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "diuretic", "ace_inhibitor"],
        "compartment": 3,
        "notes": "Aceclofenac is a selective COX-2 NSAID. Serratiopeptidase is an anti-inflammatory enzyme. Same kidney/bleeding risks as all NSAIDs."
    },

    # ── Also common: Zerodol-SP (same drug class as Actinac-SP) ────────────
    "zerodol_sp": {
        "brand": "Zerodol-SP",
        "generic": "Aceclofenac + Serratiopeptidase",
        "strength": "100mg+15mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["GI bleeding", "renal impairment"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "diuretic"],
        "compartment": 3,
        "notes": "Aceclofenac NSAID combination. Avoid with antiplatelets (GI bleed risk)."
    },

    # ── Photo 5: Impacte / Imol ─────────────────────────────────────────────
    "imol_plus": {
        "brand": "Imol Plus",
        "generic": "Ibuprofen + Paracetamol",
        "strength": "400mg+325mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["GI bleeding", "renal impairment", "liver stress (high dose)"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "ace_inhibitor"],
        "compartment": 3,
        "notes": "Combination NSAID+analgesic. All NSAID cautions apply."
    },

    # ── Photo 5: Glycorel / Glucorel (Glipizide / Glimepiride brand) ────────
    "glycorel_5": {
        "brand": "Glycorel 5",
        "generic": "Glipizide",
        "strength": "5mg",
        "therapeutic_class": "sulfonylurea",
        "organ_load": {"kidney": 2, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["hypoglycaemia", "weight gain", "dizziness"],
        "timing": "morning_with_food",
        "avoid_with": ["fluoroquinolone", "alcohol", "beta_blocker"],
        "notes": "Sulfonylurea. Hypoglycaemia risk. Beta-blockers mask warning signs."
    },

    # ── Cap. Omeprazole (common PPI seen on many prescriptions) ────────────
    "omez_20": {
        "brand": "Omez 20",
        "generic": "Omeprazole",
        "strength": "20mg",
        "therapeutic_class": "ppi",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 0, "bleeding": 0, "cns": 0},
        "schedule": "H",
        "side_effects": ["B12 deficiency (long-term)", "hypomagnesaemia"],
        "timing": "morning_empty_stomach",
        "avoid_with": ["clopidogrel"],
        "notes": "PPI. Like Pantop — reduces clopidogrel effectiveness. Long-term: B12/Mg deficiency."
    },

    # ── Pan-D (Pantoprazole + Domperidone — very commonly prescribed) ───────
    "pan_d": {
        "brand": "Pan-D",
        "generic": "Pantoprazole + Domperidone",
        "strength": "40mg+10mg",
        "therapeutic_class": "ppi",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["QT prolongation (domperidone)", "B12 deficiency"],
        "timing": "morning_empty_stomach",
        "avoid_with": ["clopidogrel", "other_qt_drugs"],
        "notes": "Domperidone has QT prolongation risk at higher doses."
    },

    # ── Combiflam (Ibuprofen + Paracetamol — very commonly prescribed OTC) ──
    "combiflam": {
        "brand": "Combiflam",
        "generic": "Ibuprofen + Paracetamol",
        "strength": "400mg+325mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "OTC",
        "side_effects": ["GI bleeding", "renal impairment"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant"],
        "compartment": 3,
        "notes": "One of India's most used OTC pain combinations. Same NSAID risks apply."
    },

    # ── Joint Line Orthopaedic Hospital prescription (uploaded photo) ─────────

    "apofec_sp": {
        "brand": "Apofec-SP",
        "generic": "Aceclofenac + Paracetamol + Serratiopeptidase",
        "strength": "100mg+325mg+15mg",
        "therapeutic_class": "nsaid",
        "organ_load": {"kidney": 3, "liver": 2, "cardiac": 2, "bleeding": 3, "cns": 0},
        "schedule": "H",
        "side_effects": ["GI bleeding", "renal impairment", "hepatotoxicity (paracetamol OD)"],
        "timing": "with_food",
        "avoid_with": ["antiplatelet", "anticoagulant", "diuretic", "ace_inhibitor", "corticosteroid"],
        "compartment": 3,
        "notes": "Triple combination NSAID. Aceclofenac (COX-2) + Paracetamol + enzyme. NSAID + steroid combination DOUBLES GI bleed risk."
    },

    "deflamat_6": {
        "brand": "Deflamat 6",
        "generic": "Deflazacort",
        "strength": "6mg",
        "therapeutic_class": "corticosteroid",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 1, "bleeding": 2, "cns": 1},
        "schedule": "H",
        "side_effects": ["GI bleeding (with NSAID)", "hyperglycaemia", "bone loss", "immune suppression"],
        "timing": "morning_with_food",
        "avoid_with": ["nsaid", "diabetes_medicines"],
        "notes": "Deflazacort is a corticosteroid. NSAID + steroid = high GI bleed risk. Doctor should co-prescribe a PPI (e.g. Rabeprazole)."
    },

    "reabzo_d": {
        "brand": "Reabzo-D",
        "generic": "Rabeprazole + Domperidone",
        "strength": "20mg+10mg",
        "therapeutic_class": "ppi",
        "organ_load": {"kidney": 0, "liver": 1, "cardiac": 1, "bleeding": 0, "cns": 1},
        "schedule": "H",
        "side_effects": ["QT prolongation (domperidone at high dose)", "B12 deficiency (long-term)"],
        "timing": "morning_empty_stomach",
        "avoid_with": ["clopidogrel", "other_qt_drugs"],
        "notes": "Rabeprazole PPI + Domperidone antiemetic. Commonly co-prescribed with NSAIDs/steroids to protect stomach lining."
    }
}



# Brand name aliases (different spellings -> same key)
BRAND_ALIASES = {
    # demo six
    "ecosprin": "ecosprin_75",
    "ecosprin 75": "ecosprin_75",
    "aspirin 75": "ecosprin_75",
    "aspirin": "ecosprin_75",
    "disprin": "ecosprin_75",
    "brufen": "brufen_400",
    "brufen 400": "brufen_400",
    "ibuprofen 400": "brufen_400",
    "ibuprofen": "brufen_400",
    "glycomet": "glycomet_500",
    "glycomet 500": "glycomet_500",
    "metformin 500": "glycomet_500",
    "metformin": "glycomet_500",
    "stamlo": "stamlo_5",
    "stamlo 5": "stamlo_5",
    "amlodipine 5": "stamlo_5",
    "amlodipine": "stamlo_5",
    "crocin": "crocin_500",
    "crocin 500": "crocin_500",
    "paracetamol 500": "crocin_500",
    "paracetamol": "crocin_500",
    "shelcal": "shelcal_500",
    "shelcal 500": "shelcal_500",
    "calcium": "shelcal_500",
    # tier two
    "acitrom": "acitrom_2",
    "acitrom 2": "acitrom_2",
    "acenocoumarol": "acitrom_2",
    "acenocoumarol 2": "acitrom_2",
    "clopilet": "clopilet_75",
    "clopilet 75": "clopilet_75",
    "clopidogrel": "clopilet_75",
    "clopidogrel 75": "clopilet_75",
    "lasix": "lasix_40",
    "lasix 40": "lasix_40",
    "furosemide": "lasix_40",
    "furosemide 40": "lasix_40",
    "enam": "enam_5",
    "enam 5": "enam_5",
    "enalapril": "enam_5",
    "enalapril 5": "enam_5",
    "telma": "telma_40",
    "telma 40": "telma_40",
    "telmisartan": "telma_40",
    "telmisartan 40": "telma_40",
    "alzolam": "alzolam_0_25",
    "alzolam 0.25": "alzolam_0_25",
    "alprazolam": "alzolam_0_25",
    "alprazolam 0.25": "alzolam_0_25",
    "tramazac": "tramazac_50",
    "tramazac 50": "tramazac_50",
    "tramadol": "tramazac_50",
    "tramadol 50": "tramazac_50",
    "azithral": "azithral_500",
    "azithral 500": "azithral_500",
    "azithromycin": "azithral_500",
    "azithromycin 500": "azithral_500",
    "ciplox": "ciplox_500",
    "ciplox 500": "ciplox_500",
    "ciprofloxacin": "ciplox_500",
    "ciprofloxacin 500": "ciplox_500",
    "fludac": "fludac_20",
    "fludac 20": "fludac_20",
    "fluoxetine": "fludac_20",
    "fluoxetine 20": "fludac_20",
    "amaryl": "amaryl_2",
    "amaryl 2": "amaryl_2",
    "glimepiride": "amaryl_2",
    "glimepiride 2": "amaryl_2",
    "metolar": "metolar_25",
    "metolar 25": "metolar_25",
    "metoprolol": "metolar_25",
    "metoprolol 25": "metolar_25",
    "pantop": "pantop_40",
    "pantop 40": "pantop_40",
    "pantoprazole": "pantop_40",
    "pantoprazole 40": "pantop_40",
    # v3 additions - real brands from our family prescriptions (Pantocid/Pan = pantoprazole)
    "pantocid": "pantop_40",
    "pantocid 40": "pantop_40",
    "pantocid 40 mg": "pantop_40",
    "pan 40": "pantop_40",
    "pan 40 mg": "pantop_40",

    # v4 additions - pharmacy-bought demo strips (compositions verified online)
    # MYPAR-500 = Paracetamol 500mg (Morepen) -> same as Crocin 500
    "mypar": "crocin_500",
    "mypar 500": "crocin_500",
    "mypar 500 mg": "crocin_500",
    "mypar-500": "crocin_500",
    # Crocin Advance = Paracetamol 500mg (GSK Optizorb) -> same as Crocin 500
    "crocin advance": "crocin_500",
    "crocin advance 500": "crocin_500",
    "crocin advance 500 mg": "crocin_500",
    # Azidoz-250LB = Azithromycin 250mg + probiotic -> same molecule as Azithral
    "azidoz": "azithral_500",
    "azidoz 250": "azithral_500",
    "azidoz 250 lb": "azithral_500",
    "azidoz-250lb": "azithral_500",

    # v5 additions - more strips from the family drawer (compositions verified)
    # Eltroxin 50 = Levothyroxine 50mcg -> same medicine as Thyronorm 50
    "eltroxin": "thyronorm_50",
    "eltroxin 50": "thyronorm_50",
    "eltroxin 50 mcg": "thyronorm_50",
    # Cipcal HD = Calcium Carbonate (500mg elemental) + Vitamin D3 -> same as Shelcal 500
    "cipcal hd": "shelcal_500",
    "cipcal": "shelcal_500",
    # Vridol 650 = Paracetamol 650mg -> same medicine as Dolo 650
    "vridol": "dolo_650",
    "vridol 650": "dolo_650",
    # Parasip 500 = Paracetamol 500mg -> same as Crocin 500
    "parasip 500": "crocin_500",
    # gap fix: typing "Paracetamol 650" was wrongly flagged
    "paracetamol 650": "dolo_650",
    "dolo": "dolo_650",
    "dolo 650": "dolo_650",
    "dolo 500": "dolo_650",
    # tier three
    "warfarin": "warfarin_5",
    "warfarin 5": "warfarin_5",
    "voveran": "voveran_50",
    "voveran 50": "voveran_50",
    "diclofenac": "voveran_50",
    "diclofenac 50": "voveran_50",
    "codeine": "codeine_syrup",
    "codeine syrup": "codeine_syrup",
    "codeine cough syrup": "codeine_syrup",
    "avil": "avil_25",
    "avil 25": "avil_25",
    "chlorpheniramine": "avil_25",
    "serenace": "serenace_5",
    "serenace 5": "serenace_5",
    "haloperidol": "serenace_5",
    "haloperidol 5": "serenace_5",
    "emeset": "emeset_4",
    "emeset 4": "emeset_4",
    "ondansetron": "emeset_4",
    "ondansetron 4": "emeset_4",
    "serta": "serta_50",
    "serta 50": "serta_50",
    "sertraline": "serta_50",
    "sertraline 50": "serta_50",
    "amiodarone": "amiodarone_200",
    "amiodarone 200": "amiodarone_200",
    "lanoxin": "lanoxin_0_25",
    "lanoxin 0.25": "lanoxin_0_25",
    "digoxin": "lanoxin_0_25",
    "digoxin 0.25": "lanoxin_0_25",
    "gabapin": "gabapin_300",
    "gabapin 300": "gabapin_300",
    "gabapentin": "gabapin_300",
    "gabapentin 300": "gabapin_300",
    "lithosun": "lithosun_400",
    "lithosun 400": "lithosun_400",
    "lithium": "lithosun_400",
    "catapres": "catapres_100",
    "catapres 100": "catapres_100",
    "clonidine": "catapres_100",
    "eptoin": "eptoin_100",
    "eptoin 100": "eptoin_100",
    "phenytoin": "eptoin_100",
    "tegretol": "tegretol_200",
    "tegretol 200": "tegretol_200",
    "carbamazepine": "tegretol_200",
    "thyronorm": "thyronorm_50",
    "thyronorm 50": "thyronorm_50",
    "levothyroxine": "thyronorm_50",
    "thyroxine": "thyronorm_50",
    "wysolone": "wysolone_10",
    "wysolone 10": "wysolone_10",
    "prednisolone": "wysolone_10",
    "prednisone": "wysolone_10",
    "hcq": "hcq_200",
    "hcq 200": "hcq_200",
    "hydroxychloroquine": "hcq_200",
    "lipitor": "lipitor_10",
    "lipitor 10": "lipitor_10",
    "atorvastatin": "lipitor_10",
    "atorvastatin 10": "lipitor_10",
    "rosuvas": "rosuvas_10",
    "rosuvas 10": "rosuvas_10",
    "rosuvastatin": "rosuvas_10",
    "rimactane": "rimactane_450",
    "rimactane 450": "rimactane_450",
    "rifampicin": "rimactane_450",
    "inh": "inh_300",
    "inh 300": "inh_300",
    "isoniazid": "inh_300",
    "clindac": "clindac_300",
    "clindac 300": "clindac_300",
    "clindamycin": "clindac_300",
    "flagyl": "flagyl_400",
    "flagyl 400": "flagyl_400",
    "metronidazole": "flagyl_400",
    "tetracycline": "tetracycline_500",
    "tetracycline 500": "tetracycline_500",
    "doxt": "doxt_100",
    "doxt 100": "doxt_100",
    "doxycycline": "doxt_100",
    "furadantin": "furadantin_100",
    "furadantin 100": "furadantin_100",
    "nitrofurantoin": "furadantin_100",
    "aldactone": "aldactone_25",
    "aldactone 25": "aldactone_25",
    "spironolactone": "aldactone_25",
    "hctz": "hctz_25",
    "hctz 25": "hctz_25",
    "hydrochlorothiazide": "hctz_25",
    "tenormin": "tenormin_50",
    "tenormin 50": "tenormin_50",
    "atenolol": "tenormin_50",
    "cardace": "cardace_5",
    "cardace 5": "cardace_5",
    "ramipril": "cardace_5",

    # ── NEW: from your prescription photos ────────────────────────────────────

    # Actinac-SP (Photo 4) — NSAID
    "actinac-sp": "actinac_sp",
    "actinac sp": "actinac_sp",
    "actinac": "actinac_sp",
    "actirac sp": "actinac_sp",       # common OCR misread
    "actirac-sp": "actinac_sp",
    "actinac-s": "actinac_sp",
    "aceclofenac": "actinac_sp",
    "aceclofenac 100": "actinac_sp",
    "zerodol-sp": "zerodol_sp",
    "zerodol sp": "zerodol_sp",
    "zerodol": "zerodol_sp",
    "hifenac sp": "actinac_sp",       # another brand of same drug
    "hifenac-sp": "actinac_sp",

    # Imol / Impacte (Photo 5) — NSAID combo
    "imol plus": "imol_plus",
    "imol": "imol_plus",
    "impacte": "imol_plus",
    "impact": "imol_plus",
    "impacte 400": "imol_plus",
    "combiflam": "combiflam",
    "ibugesic plus": "imol_plus",

    # Glycorel / Glucorel (Photo 5) — Sulfonylurea
    "glycorel": "glycorel_5",
    "glycorel 5": "glycorel_5",
    "glucorel": "glycorel_5",
    "glucorel 5": "glycorel_5",
    "glipizide": "glycorel_5",
    "glipizide 5": "glycorel_5",
    "glucotrol": "glycorel_5",

    # Omeprazole (common PPI)
    "omez": "omez_20",
    "omez 20": "omez_20",
    "omeprazole": "omez_20",
    "omeprazole 20": "omez_20",
    "ocid": "omez_20",
    "nexpro": "omez_20",
    "cap omeprazole": "omez_20",

    # Pan-D (Pantoprazole + Domperidone)
    "pan-d": "pan_d",
    "pan d": "pan_d",
    "pantop d": "pan_d",
    "pantop-d": "pan_d",
    "domperidone pantoprazole": "pan_d",

    # ── Joint Line Orthopaedic Hospital prescription ───────────────────────────
    # Apofec-SP (Aceclofenac + Paracetamol + Serratiopeptidase)
    "apofec-sp": "apofec_sp",
    "apofec sp": "apofec_sp",
    "apofec": "apofec_sp",
    "apofec-s": "apofec_sp",
    "apofec s": "apofec_sp",

    # Deflamat-6 (Deflazacort corticosteroid)
    "deflamat-6": "deflamat_6",
    "deflamat 6": "deflamat_6",
    "deflamat": "deflamat_6",
    "deflazacort": "deflamat_6",
    "deflazacort 6": "deflamat_6",
    "defcort": "deflamat_6",         # another brand of deflazacort
    "defcort 6": "deflamat_6",
    "dezacor": "deflamat_6",

    # Reabzo-D (Rabeprazole + Domperidone PPI)
    "reabzo-d": "reabzo_d",
    "reabzo d": "reabzo_d",
    "reabzo": "reabzo_d",
    "rabeprazole": "reabzo_d",
    "rabeprazole 20": "reabzo_d",
    "razo-d": "reabzo_d",
    "razo d": "reabzo_d",
    "razo": "reabzo_d",
    "rablet-d": "reabzo_d",
    "rabeloc-d": "reabzo_d",
    "rekool-d": "reabzo_d",
}



import re as _re

def _normalize_name(brand_name: str) -> str:
    """
    Normalize a medicine name string so that real-world OCR formats match
    the database.  Handles:
      - Dosage form prefixes:  Tab / Tab. / Cap / Cap. / Syp / Inj / Syr
      - Strength suffixes:     mg / mcg / ml / g  (with or without space)
      - Multiple spaces
    Examples:
      "Tab. Ecosprin 75mg"  ->  "ecosprin 75"
      "Cap Glycomet 500 mg" ->  "glycomet 500"
      "Brufen 400mg"        ->  "brufen 400"
    """
    s = brand_name.strip()
    # Strip dosage-form prefix (case-insensitive, optional dot, followed by space)
    s = _re.sub(r'^(?:tab\.?|cap\.?|syp\.?|syr\.?|inj\.?|drops?\.?)\s+', '', s, flags=_re.IGNORECASE)
    # Strip strength suffix units (e.g. "75mg" -> "75", "5 mcg" -> "5")
    s = _re.sub(r'\s*(mg|mcg|ml|g)\b', '', s, flags=_re.IGNORECASE)
    return s.strip().lower()


def lookup_medicine(brand_name: str):
    """Convert brand name string to medicine dict. Returns None if not found."""
    # Try 1: exact (lowercased) match first for speed
    key = brand_name.lower().strip()
    if key in BRAND_ALIASES:
        return MEDICINES.get(BRAND_ALIASES[key])
    if key in MEDICINES:
        return MEDICINES[key]

    # Try 2: normalized match (strips Tab., mg, etc.)
    norm = _normalize_name(brand_name)
    if norm in BRAND_ALIASES:
        return MEDICINES.get(BRAND_ALIASES[norm])
    if norm in MEDICINES:
        return MEDICINES[norm]

    return None


def lookup_key(brand_name: str):
    """Return the canonical key for a brand name."""
    key = brand_name.lower().strip()
    found = BRAND_ALIASES.get(key)
    if found:
        return found
    norm = _normalize_name(brand_name)
    return BRAND_ALIASES.get(norm, norm)

