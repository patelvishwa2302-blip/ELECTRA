# food_db.py

FOOD_INTERACTIONS = [
    {
        "food_key": "grapefruit_juice",
        "food_label": "Grapefruit Juice / Mousambi Juice",
        "interacts_with_class": ["calcium_channel_blocker", "statin"],
        "interacts_with_generic": ["amlodipine", "atorvastatin", "rosuvastatin", "simvastatin"],
        "risk_level": "high",
        "mechanism": "Furanocoumarin in grapefruit blocks intestinal CYP3A4 → drug level rises 5x",
        "patient_message": "Avoid grapefruit or grapefruit juice while taking your blood pressure / cholesterol medicine. It can raise the medicine level 5 times and cause side effects.",
        "doctor_message": "Grapefruit furanocoumarins irreversibly inhibit intestinal CYP3A4. Single glass → 3-5x increase in amlodipine/statin AUC. Effect lasts 24-72 hours."
    },
    {
        "food_key": "dairy",
        "food_label": "Dairy products (milk, curd, paneer)",
        "interacts_with_class": ["fluoroquinolone", "tetracycline"],
        "interacts_with_generic": ["ciprofloxacin", "ofloxacin", "levofloxacin", "tetracycline", "doxycycline"],
        "risk_level": "high",
        "mechanism": "Calcium chelates quinolone/tetracycline → reduces absorption by 50–70%",
        "patient_message": "Do not take your antibiotic with milk, curd, or cheese. Take it 2 hours before or after eating dairy. Dairy can reduce the medicine's effect by 50%.",
        "doctor_message": "Calcium ions form insoluble chelation complexes with quinolone carboxyl and ketone groups. Reduces Cmax and AUC by 30-70%. Administer 2h before or 6h after calcium-rich foods."
    },
    {
        "food_key": "alcohol",
        "food_label": "Alcohol",
        "interacts_with_class": ["antidiabetic", "antibiotic", "analgesic", "benzodiazepine"],
        "interacts_with_generic": ["metformin", "metronidazole", "paracetamol", "alprazolam"],
        "risk_level": "high",
        "mechanism": "Multiple: lactic acidosis (metformin), disulfiram-like reaction (metronidazole), hepatotoxicity (paracetamol), CNS depression (benzos)",
        "patient_message": "Do not drink alcohol while on these medicines. It can cause serious side effects: nausea, liver damage, very low blood sugar, or extreme drowsiness.",
        "doctor_message": "Alcohol + Metformin: lactic acidosis risk. Alcohol + Metronidazole: disulfiram-like reaction (flushing, vomiting). Alcohol + Paracetamol: CYP2E1 induction → toxic NAPQI accumulation. Alcohol + Benzos: respiratory depression."
    },
    {
        "food_key": "high_vitamin_k",
        "food_label": "Spinach / Palak, Methi, Kale",
        "interacts_with_class": ["anticoagulant"],
        "interacts_with_generic": ["warfarin", "acenocoumarol"],
        "risk_level": "moderate",
        "mechanism": "Vitamin K reduces anticoagulant effect → INR drops → clotting risk",
        "patient_message": "Eating large amounts of spinach, methi, or other green leafy vegetables regularly can reduce your blood-thinning medicine's effect. Keep your diet consistent.",
        "doctor_message": "Sudden increase in dietary Vitamin K competes with warfarin at VKOR enzyme → reduced anticoagulant effect → subtherapeutic INR. Advise consistent (not zero) Vitamin K intake."
    },
    {
        "food_key": "banana_coconut_water",
        "food_label": "Banana, Coconut water, Orange juice",
        "interacts_with_class": ["ace_inhibitor", "arb", "potassium_sparing_diuretic"],
        "interacts_with_generic": ["enalapril", "telmisartan", "spironolactone"],
        "risk_level": "high",
        "mechanism": "High potassium foods + potassium-sparing drugs → hyperkalaemia → cardiac arrest",
        "patient_message": "While taking your blood pressure medicine, avoid eating too many bananas, coconut water, or orange juice. These raise potassium levels which can affect your heart.",
        "doctor_message": "ACE inhibitors/ARBs reduce aldosterone → potassium retention. Combined with high dietary potassium → hyperkalaemia (K >6.5 mEq/L) → fatal arrhythmias. Monitor K+ every 3 months."
    },
    {
        "food_key": "tyramine_foods",
        "food_label": "Aged cheese, red wine, processed meats, fermented foods",
        "interacts_with_class": ["maoi"],
        "interacts_with_generic": ["phenelzine", "tranylcypromine", "selegiline"],
        "risk_level": "critical",
        "mechanism": "MAO inhibition prevents tyramine breakdown → severe hypertensive crisis",
        "patient_message": "AVOID aged cheese, red wine, and fermented foods completely while on MAO inhibitor medicine. This can cause a life-threatening blood pressure spike.",
        "doctor_message": "MAO-A inhibition → tyramine accumulates → norepinephrine surge → hypertensive crisis (BP > 200/120 mmHg). Potentially fatal. Strict dietary restriction mandatory."
    },
    {
        "food_key": "milk_thyroid",
        "food_label": "Milk (morning, near thyroid dose)",
        "interacts_with_class": ["thyroid_hormone"],
        "interacts_with_generic": ["levothyroxine"],
        "risk_level": "moderate",
        "mechanism": "Calcium in milk reduces levothyroxine absorption by 40%",
        "patient_message": "Take your thyroid tablet first thing in the morning on an empty stomach with plain water. Wait at least 30 minutes before drinking milk or tea.",
        "doctor_message": "Calcium (from milk) reduces levothyroxine absorption by 17-40% via chelation. Administer on empty stomach at least 30-60 min before calcium-containing foods."
    },
    {
        "food_key": "liquorice_candy",
        "food_label": "Licorice candy / Mulethi sweets",
        "interacts_with_class": ["antihypertensive"],
        "interacts_with_generic": ["enalapril", "telmisartan", "amlodipine", "atenolol"],
        "risk_level": "moderate",
        "mechanism": "Glycyrrhizin → pseudohyperaldosteronism → raises BP",
        "patient_message": "Licorice-flavored candies or drinks can raise blood pressure and cancel the effect of your blood pressure medicine.",
        "doctor_message": "Even moderate regular consumption of glycyrrhizin-containing licorice products induces 11β-HSD2 inhibition → sodium retention → hypertension that resists antihypertensives."
    }
]
