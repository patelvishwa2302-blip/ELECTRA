# ayurvedic_db.py

AYURVEDIC_INTERACTIONS = [
    {
        "name": "Ashwagandha",
        "also_known_as": ["Withania somnifera", "Indian ginseng"],
        "interacts_with_class": ["anticoagulant", "antiplatelet", "thyroid_hormone"],
        "interacts_with_generic": ["warfarin", "acenocoumarol", "aspirin", "levothyroxine"],
        "risk_level": "high",
        "mechanism": "Potentiates anticoagulant effect; may alter thyroid T3/T4 levels",
        "patient_message": "Ashwagandha can increase the blood-thinning effect of your medicine. This can cause unexpected bleeding.",
        "doctor_message": "Ashwagandha (withanolides) potentiates coumarin anticoagulants and antiplatelets. Monitor INR closely. Separate levothyroxine administration.",
        "evidence": "Natural Medicines Database; Cupp et al., herbal interactions review"
    },
    {
        "name": "Chyawanprash",
        "also_known_as": ["Chyavanaprash", "Amla formulation"],
        "interacts_with_class": ["anticoagulant", "antiplatelet"],
        "interacts_with_generic": ["warfarin", "aspirin"],
        "risk_level": "moderate",
        "mechanism": "High-dose Amla (vitamin C) and other constituents may affect platelet function and INR.",
        "patient_message": "Chyawanprash can add to the blood-thinning effect of your medicines. Check with your doctor.",
        "doctor_message": "Formulations containing high-dose Amla may alter INR and platelet aggregation.",
        "evidence": "Natural Medicines Database; Weintraub et al., JAMA 1972"
    },
    {
        "name": "Triphala",
        "also_known_as": ["Haritaki-Bibhitaki-Amalaki blend"],
        "interacts_with_class": ["antidiabetic", "sulfonylurea"],
        "interacts_with_generic": ["metformin", "glimepiride", "insulin"],
        "risk_level": "high",
        "mechanism": "Additive blood sugar lowering → hypoglycaemia",
        "patient_message": "Triphala can lower your blood sugar too much when taken with your diabetes medicine. Watch for dizziness, sweating, or shakiness.",
        "doctor_message": "Triphala's gallic acid and chebulic acid have hypoglycaemic properties. Additive effect with biguanides/sulfonylureas → symptomatic hypoglycaemia risk.",
        "evidence": "Babu et al., 2013, Journal of Ethnopharmacology"
    },
    {
        "name": "Guggulu",
        "also_known_as": ["Commiphora mukul", "Shallaki"],
        "interacts_with_class": ["thyroid_hormone"],
        "interacts_with_generic": ["levothyroxine"],
        "risk_level": "moderate",
        "mechanism": "Reduces intestinal drug absorption; may induce hepatic enzymes",
        "patient_message": "Guggulu can reduce how much of your thyroid medicine gets into your blood. Take them at least 4 hours apart.",
        "doctor_message": "Guggulu reduces levothyroxine bioavailability, likely via bile acid sequestration. May also induce CYP enzymes reducing systemic exposure.",
        "evidence": "Panda et al., Clinical Pharmacokinetics"
    },
    {
        "name": "Tulsi",
        "also_known_as": ["Holy Basil", "Ocimum sanctum"],
        "interacts_with_class": ["anticoagulant", "antiplatelet"],
        "interacts_with_generic": ["warfarin", "aspirin", "clopidogrel"],
        "risk_level": "moderate",
        "mechanism": "Eugenol in Tulsi inhibits platelet aggregation → additive anticoagulation",
        "patient_message": "Tulsi has blood-thinning properties. Taking it with your blood thinner increases bleeding risk.",
        "doctor_message": "Eugenol (key Tulsi constituent) inhibits platelet aggregation via TXA2 pathway. Additive effect with warfarin and antiplatelets.",
        "evidence": "Natural Medicines Database, 2022"
    },
    {
        "name": "Neem",
        "also_known_as": ["Azadirachta indica", "Margosa"],
        "interacts_with_class": ["antidiabetic", "sulfonylurea"],
        "interacts_with_generic": ["metformin", "glimepiride", "insulin"],
        "risk_level": "high",
        "mechanism": "Strong hypoglycaemic activity → severe hypoglycaemia when combined",
        "patient_message": "Neem strongly lowers blood sugar. Taking it with your diabetes medicine may make your blood sugar drop dangerously low.",
        "doctor_message": "Neem bark extract has strong hypoglycaemic properties (nimbolide). Severe additive hypoglycaemia documented with antidiabetics.",
        "evidence": "Neem: A tree for solving global problems, National Academies Press"
    },
    {
        "name": "Arjuna bark",
        "also_known_as": ["Terminalia arjuna", "Arjun"],
        "interacts_with_class": ["cardiac_glycoside", "antiarrhythmic"],
        "interacts_with_generic": ["digoxin", "amiodarone"],
        "risk_level": "high",
        "mechanism": "Arjuna has glycoside-like cardiac activity → additive bradycardia + AV block risk",
        "patient_message": "Arjuna bark has heart-slowing effects similar to your heart medicine. Together, your heart rate may drop too low.",
        "doctor_message": "Terminalia arjuna contains triterpenoid glycosides with positive inotropic effect. Additive bradycardia and potential AV block with digoxin/amiodarone.",
        "evidence": "Ram et al., J Ethnopharmacol 2012"
    },
    {
        "name": "Ginger (high dose supplement)",
        "also_known_as": ["Zingiber officinale", "Adrak"],
        "interacts_with_class": ["antiplatelet", "nsaid", "anticoagulant"],
        "interacts_with_generic": ["aspirin", "ibuprofen", "warfarin"],
        "risk_level": "moderate",
        "mechanism": "Gingerols inhibit thromboxane synthesis → amplified platelet inhibition",
        "patient_message": "High-dose ginger supplement (not food quantities) can increase bleeding when taken with your pain or blood-thinning medicine.",
        "doctor_message": "Gingerols inhibit TXA2 synthetase and platelet aggregation. Amplifies effect of antiplatelets and anticoagulants. Culinary ginger (small amounts) generally safe.",
        "evidence": "Vaes & Chyka, Ann Pharmacother 2000"
    },
    {
        "name": "Garlic (supplement)",
        "also_known_as": ["Allium sativum", "Lahsun supplement"],
        "interacts_with_class": ["anticoagulant", "antiplatelet", "antihypertensive"],
        "interacts_with_generic": ["warfarin", "aspirin"],
        "risk_level": "moderate",
        "mechanism": "Allicin inhibits platelet aggregation + fibrinolytic activity",
        "patient_message": "Garlic supplements (not regular food) can increase bleeding when taken with blood thinners.",
        "doctor_message": "Allicin and ajoene inhibit platelet aggregation. Case reports of bleeding with warfarin. Monitor INR. Distinguish supplement dose from dietary garlic.",
        "evidence": "Burnham et al., Pharmacotherapy 1995"
    },
    {
        "name": "Licorice / Mulethi",
        "also_known_as": ["Glycyrrhiza glabra", "Mulethi", "Liquorice"],
        "interacts_with_class": ["antihypertensive", "diuretic", "corticosteroid"],
        "interacts_with_generic": ["enalapril", "telmisartan", "furosemide", "prednisone"],
        "risk_level": "high",
        "mechanism": "Glycyrrhizin causes pseudohyperaldosteronism → sodium retention, potassium loss, hypertension",
        "patient_message": "Licorice raises blood pressure and cancels the effect of your blood pressure medicine. Avoid licorice-containing products.",
        "doctor_message": "Glycyrrhizin inhibits 11β-HSD2 → mineralocorticoid-like effect → sodium retention, hypokalemia, hypertension. Directly antagonizes antihypertensives.",
        "evidence": "Walker & Edwards, J Clin Pharm Ther 1994"
    },
    {
        "name": "Brahmi",
        "also_known_as": ["Bacopa monnieri", "Water hyssop"],
        "interacts_with_class": ["benzodiazepine", "sedative", "antiepileptic"],
        "interacts_with_generic": ["alprazolam", "diazepam", "phenytoin"],
        "risk_level": "moderate",
        "mechanism": "Bacosides enhance GABA receptor activity → CNS depression additive with sedatives",
        "patient_message": "Brahmi can make sedative medicines stronger. You may feel very drowsy or confused. Do not drive.",
        "doctor_message": "Brahmi (bacosides) modulate GABAergic transmission. Additive CNS depression with benzodiazepines and sedatives. Also may alter phenytoin metabolism.",
        "evidence": "Singh & Dhawan, Neuropharmacology 1997"
    },
    {
        "name": "Shatavari",
        "also_known_as": ["Asparagus racemosus", "Satmuli"],
        "interacts_with_class": ["diuretic"],
        "interacts_with_generic": ["furosemide", "spironolactone", "hydrochlorothiazide"],
        "risk_level": "low",
        "mechanism": "Mild diuretic activity → additive fluid/electrolyte loss",
        "patient_message": "Shatavari has mild diuretic (water-expelling) effects that may add to your diuretic medicine.",
        "doctor_message": "Shatavari has diuretic saponins. Additive effect with loop/thiazide diuretics may cause electrolyte imbalance. Monitor electrolytes.",
        "evidence": "Ayurvedic Pharmacopoeia of India"
    },
    {
        "name": "Amla (high dose)",
        "also_known_as": ["Emblica officinalis", "Indian gooseberry"],
        "interacts_with_class": ["anticoagulant"],
        "interacts_with_generic": ["warfarin", "acenocoumarol"],
        "risk_level": "moderate",
        "mechanism": "High Vitamin C content → may interfere with INR control",
        "patient_message": "High-dose Amla supplement (not occasional fruit) may affect your blood-thinning medicine. Get your INR checked if you start taking it.",
        "doctor_message": "High-dose ascorbic acid from Amla can reduce warfarin's anticoagulant effect (mechanism unclear — possibly increased vitamin K-dependent clotting factors). Monitor INR.",
        "evidence": "Weintraub et al., JAMA 1972; updated in Natural Medicines Database"
    },
    {
        "name": "Fenugreek (Methi)",
        "also_known_as": ["Trigonella foenum-graecum", "Methi seeds"],
        "interacts_with_class": ["antidiabetic", "anticoagulant"],
        "interacts_with_generic": ["metformin", "glimepiride", "warfarin"],
        "risk_level": "moderate",
        "mechanism": "4-hydroxyisoleucine stimulates insulin secretion → additive hypoglycaemia",
        "patient_message": "Fenugreek (methi) seeds in large quantities lower blood sugar. With your diabetes medicine, blood sugar may drop too much.",
        "doctor_message": "Fenugreek's 4-hydroxyisoleucine stimulates pancreatic beta cells. Additive with sulfonylureas. Also anticoagulant effect via coumarin derivatives — monitor INR with warfarin.",
        "evidence": "Sharma et al., Eur J Clin Nutr 1990"
    },
    {
        "name": "Karela (Bitter Gourd)",
        "also_known_as": ["Momordica charantia", "Bitter melon"],
        "interacts_with_class": ["antidiabetic", "sulfonylurea"],
        "interacts_with_generic": ["metformin", "glimepiride", "insulin"],
        "risk_level": "high",
        "mechanism": "Charantin, polypeptide-P have strong insulin-mimicking effects → severe hypoglycaemia",
        "patient_message": "Karela (bitter gourd) strongly lowers blood sugar. Taking it with diabetes medicine can drop your sugar to dangerously low levels. Watch for shaking, sweating, confusion.",
        "doctor_message": "Momordica charantia contains charantin (steroidal saponin) and polypeptide-P (plant insulin). Severe additive hypoglycaemia documented in case reports. Warn diabetic patients explicitly.",
        "evidence": "Basch et al., J Clin Pharm Ther 2003"
    },
    {
        "name": "Shankhpushpi",
        "also_known_as": ["Convolvulus pluricaulis", "Speed Weed"],
        "interacts_with_class": ["antiepileptic"],
        "interacts_with_generic": ["phenytoin"],
        "risk_level": "high",
        "mechanism": "Alkaloids reduce phenytoin plasma levels → seizure breakthrough risk",
        "patient_message": "Shankhpushpi reduces the level of your epilepsy medicine in your blood. This can cause seizures. Avoid if taking epilepsy medicine.",
        "doctor_message": "Shankhpushpi formulations reduce phenytoin plasma concentration, likely via hepatic enzyme induction or reduced absorption. Seizure breakthrough documented. Contraindicated with phenytoin.",
        "evidence": "Dandekar et al., J Ethnopharmacol 1992"
    },
    {
        "name": "Kava",
        "also_known_as": ["Piper methysticum", "Kava kava"],
        "interacts_with_class": ["benzodiazepine", "sedative", "alcohol"],
        "interacts_with_generic": ["alprazolam", "diazepam", "zolpidem"],
        "risk_level": "high",
        "mechanism": "Kavalactones potentiate GABA activity → severe CNS/respiratory depression",
        "patient_message": "Kava makes sedative medicines much stronger and can cause dangerously low breathing. Do not combine.",
        "doctor_message": "Kavalactones act on GABA-A and NMDA receptors. Potentially fatal CNS/respiratory depression with benzodiazepines. Also hepatotoxic — monitor LFTs.",
        "evidence": "Russmann et al., Ann Intern Med 2003; FDA advisory 2002"
    },
    {
        "name": "Valerian",
        "also_known_as": ["Valeriana officinalis", "Tagara"],
        "interacts_with_class": ["sedative", "benzodiazepine", "antidepressant"],
        "interacts_with_generic": ["alprazolam", "zolpidem", "fluoxetine"],
        "risk_level": "moderate",
        "mechanism": "Valerenic acid acts on GABA receptors → additive sedation",
        "patient_message": "Valerian root adds to the drowsiness of your medicine. Don't drive or use machines.",
        "doctor_message": "Valerenic acid modulates GABA-A receptors. Additive sedation with CNS depressants. May also inhibit CYP2D6 — monitor antidepressant levels.",
        "evidence": "Donath et al., Pharmacopsychiatry 2000"
    },
    {
        "name": "Pippali",
        "also_known_as": ["Piper longum", "Long pepper"],
        "interacts_with_class": ["statin", "benzodiazepine", "antiarrhythmic", "calcium_channel_blocker", "anticonvulsant"],
        "interacts_with_generic": [],
        "risk_level": "moderate",
        "mechanism": "Piperine is a potent CYP3A4 and P-glycoprotein inhibitor → raises levels of many drugs",
        "patient_message": "Pippali can increase the amount of many medicines in your blood, potentially making them too strong.",
        "doctor_message": "Piperine (major alkaloid) is a significant CYP3A4 and P-gp inhibitor. Increases bioavailability of: rifampicin, curcumin, resveratrol, and many others. Clinically significant when used in high-dose supplements.",
        "evidence": "Bhardwaj et al., Pharm Res 2002"
    },
    {
        "name": "Punarnava",
        "also_known_as": ["Boerhavia diffusa", "Spreading hogweed"],
        "interacts_with_class": ["diuretic", "antihypertensive"],
        "interacts_with_generic": ["furosemide", "enalapril", "telmisartan"],
        "risk_level": "low",
        "mechanism": "Punarnavine has diuretic and antihypertensive activity → additive BP lowering",
        "patient_message": "Punarnava has blood pressure and diuretic effects that add to your BP medicine. Your blood pressure may drop too low.",
        "doctor_message": "Punarnavine (alkaloid) has documented diuretic and hypotensive effects. Additive with antihypertensives and diuretics — monitor BP and electrolytes.",
        "evidence": "Ayurvedic Pharmacopoeia of India; Singh & Singh, Ethnopharmacol Rev"
    },

    # ── FROM YOUR KERALA AYURVEDA SALA PRESCRIPTIONS ─────────────────────────

    {
        "name": "Ashokarishta",
        "also_known_as": [
            "Ashokrishta", "Ashokartishta", "Asokarishta", "Asokarishtam",
            "Ashokarishta", "Ashoka arishtam"
        ],
        "interacts_with_class": ["anticoagulant", "antiplatelet", "corticosteroid"],
        "interacts_with_generic": ["warfarin", "acenocoumarol", "aspirin", "prednisolone"],
        "risk_level": "moderate",
        "mechanism": (
            "Saraca asoca bark (primary constituent) contains estrogenic flavonoids and "
            "tannins with mild platelet-inhibitory effects. Fermented formulation also "
            "contains ~5–10% self-generated alcohol which can potentiate anticoagulants."
        ),
        "patient_message": (
            "Ashokarishta is an Ayurvedic liquid tonic. It can slightly increase the "
            "blood-thinning effect of your medicine. Tell your doctor you are taking it."
        ),
        "doctor_message": (
            "Ashokarishta (Saraca asoca + 20+ herbs, fermented, ~8% alcohol) has mild "
            "platelet-inhibitory and estrogenic effects. The alcohol content (~8%) can "
            "potentiate anticoagulants (warfarin INR increase). Monitor INR. Caution with "
            "corticosteroids due to additive hormonal effects."
        ),
        "evidence": "Ayurvedic Pharmacopoeia of India Vol IV; Natural Medicines Database"
    },
    {
        "name": "Chandanasava",
        "also_known_as": [
            "Chandanasavam", "Chandan asava", "Chandana asavam"
        ],
        "interacts_with_class": ["diuretic", "nsaid", "ace_inhibitor"],
        "interacts_with_generic": ["furosemide", "ibuprofen", "enalapril", "telmisartan"],
        "risk_level": "low",
        "mechanism": (
            "Sandalwood (Santalum album) and associated herbs confer mild diuretic and "
            "cooling (anti-inflammatory) effects. Additive diuresis with loop/thiazide "
            "diuretics; mild synergism with NSAIDs on renal prostaglandins."
        ),
        "patient_message": (
            "Chandanasava is a sandalwood-based Ayurvedic tonic. It has mild diuretic "
            "(water-expelling) properties that can add to your water-pill or kidney medicine."
        ),
        "doctor_message": (
            "Chandanasava contains Santalum album with documented mild diuretic activity. "
            "Additive fluid loss with loop diuretics (furosemide). The ~8% fermentation "
            "alcohol may interact with NSAIDs — minor renal prostaglandin concern. "
            "Clinically low risk in healthy kidneys; monitor in CKD."
        ),
        "evidence": "Ayurvedic Formulary of India Part I; Pharmacopoeia of India"
    },
    {
        "name": "Dhanwantharam Gulika",
        "also_known_as": [
            "Dhanwantharghulika", "Dhanwantaram Gulika", "Dhanwantharam Gutika",
            "Dhanwantharghuli", "Dhanwantharam tablets"
        ],
        "interacts_with_class": ["nsaid", "analgesic", "anticoagulant"],
        "interacts_with_generic": ["ibuprofen", "paracetamol", "warfarin", "aspirin"],
        "risk_level": "moderate",
        "mechanism": (
            "Contains multiple herbs with anti-inflammatory, vata-alleviating properties "
            "(sesame, castor, bala etc.). Additive anti-inflammatory effect with NSAIDs; "
            "some constituents may mildly potentiate anticoagulants."
        ),
        "patient_message": (
            "Dhanwantharam Gulika is an Ayurvedic pain/inflammation tablet. Taking it "
            "alongside your pain medicine can make both stronger. Inform your doctor."
        ),
        "doctor_message": (
            "Dhanwantharam Gulika contains sesame (Sesamum indicum), Bala (Sida cordifolia) "
            "and other anti-inflammatory herbs. Potential additive anti-inflammatory effect "
            "with NSAIDs. Some herbal constituents may mildly inhibit platelet aggregation — "
            "caution with anticoagulants. Monitor for GI effects if combined with NSAIDs."
        ),
        "evidence": "Kottakkal Arya Vaidya Sala monograph; Ayurvedic Pharmacopoeia of India"
    },
    {
        "name": "Sukumara Kwatham",
        "also_known_as": [
            "Sukumara Kvaltham", "Sukumara Kashayam", "Sukumara kwatham tablets",
            "Sukumarakasayam", "Sukumaram kwatham"
        ],
        "interacts_with_class": ["antidiabetic", "diuretic"],
        "interacts_with_generic": ["metformin", "glimepiride", "furosemide"],
        "risk_level": "low",
        "mechanism": (
            "Sukumara Kwatham (Castor root, Eranda, Draksha etc.) has mild laxative and "
            "digestive properties. Castor root constituents may mildly lower blood sugar "
            "and cause additive diuresis with diuretics."
        ),
        "patient_message": (
            "Sukumara Kwatham is a digestive and gynecological Ayurvedic decoction. "
            "It is generally safe but inform your doctor if you take diabetes or water medicines."
        ),
        "doctor_message": (
            "Sukumara Kwatham contains Eranda (Ricinus communis root), Draksha (Vitis vinifera) "
            "and ~22 other herbs. Mild laxative effect — monitor electrolytes if co-prescribed "
            "with diuretics. Castor root has mild hypoglycaemic activity (in vitro); low clinical "
            "significance but monitor in diabetic patients."
        ),
        "evidence": "Sahasrayogam; Ashtanga Hridayam; Kottakkal AVS monograph"
    },
    {
        "name": "Kumaryasava",
        "also_known_as": [
            "Kumaryasavam", "Kumaryogasavam", "Kumari asavam", "Kumara yogasava"
        ],
        "interacts_with_class": ["antidiabetic", "sulfonylurea", "diuretic"],
        "interacts_with_generic": ["metformin", "glimepiride", "furosemide", "spironolactone"],
        "risk_level": "moderate",
        "mechanism": (
            "Primary constituent Aloe vera (Kumari) has documented hypoglycaemic effect "
            "via improved insulin sensitivity. Fermented formulation (~5–7% alcohol). "
            "Anthraquinones in Aloe have laxative/mild diuretic effect — additive with diuretics."
        ),
        "patient_message": (
            "Kumaryasava contains Aloe vera which can lower blood sugar. If you take "
            "diabetes medicine, your blood sugar may drop too low. Monitor carefully."
        ),
        "doctor_message": (
            "Kumaryasava is an Aloe vera-based fermented tonic. Aloe vera significantly "
            "lowers fasting blood glucose (multiple RCTs). Additive hypoglycaemia risk with "
            "metformin and sulfonylureas — clinically significant. Anthraquinones cause "
            "additive diuresis and possible electrolyte loss. Monitor glucose and K+ levels."
        ),
        "evidence": (
            "Yongchaiyudha et al., J Med Assoc Thai 1996; Vogler & Ernst, Br J Gen Pract 1999; "
            "Natural Medicines Database"
        )
    },
    {
        "name": "Rajapravarti Vatika",
        "also_known_as": [
            "Rajapraverti Vadikg", "Rajapravarti vatika", "Raja pravarti gutika",
            "Rajapravarti tablets"
        ],
        "interacts_with_class": ["anticoagulant", "corticosteroid", "antidiabetic"],
        "interacts_with_generic": ["warfarin", "prednisolone", "metformin"],
        "risk_level": "moderate",
        "mechanism": (
            "Classical emmenagogue tablet containing Tankana (borax), Hingu (asafoetida), "
            "Chitraka and other herbs. Emmenagogue herbs stimulate uterine contractions; "
            "some constituents have mild anticoagulant properties."
        ),
        "patient_message": (
            "Rajapravarti Vatika is an Ayurvedic tablet for menstrual health. Some of its "
            "ingredients can interact with blood-thinning or steroid medicines. Tell your doctor."
        ),
        "doctor_message": (
            "Rajapravarti Vatika (Tankana bhasma, Hingu, Chitraka, Yavakshara) is an "
            "emmenagogue with uterotonic herbs. Potential mild anticoagulant effect — "
            "caution with warfarin/acenocoumarol (monitor INR). Avoid in pregnancy. "
            "Some constituents may interfere with corticosteroid metabolism."
        ),
        "evidence": "Sahasrayogam; Ayurvedic Formulary of India; Kottakkal AVS monograph"
    },
    {
        "name": "Mensokot",
        "also_known_as": [
            "Mensa Kot", "Mensokot tablets", "Mensokot Kottakkal"
        ],
        "interacts_with_class": ["anticoagulant", "antiplatelet", "corticosteroid"],
        "interacts_with_generic": ["warfarin", "aspirin", "prednisolone"],
        "risk_level": "moderate",
        "mechanism": (
            "Proprietary Kottakkal formulation for menstrual disorders; contains Ashoka "
            "(Saraca asoca), Lodhra (Symplocos racemosa), and iron-based bhasmas. "
            "Estrogenic flavonoids from Ashoka + platelet effects; iron bhasmas may "
            "affect absorption of co-administered drugs."
        ),
        "patient_message": (
            "Mensokot is a Kottakkal Ayurvedic medicine for menstrual problems. It can "
            "mildly affect blood-thinning medicines. Do not take without telling your doctor."
        ),
        "doctor_message": (
            "Mensokot (Kottakkal AVS proprietary) contains Ashokarishta base + Lodhra + "
            "Loha bhasma (iron). Estrogenic effect from Saraca asoca may potentiate "
            "anticoagulants. Iron bhasma can chelate and reduce absorption of quinolones, "
            "tetracyclines, and levothyroxine — separate administration by ≥2 hours. "
            "Avoid in bleeding disorders."
        ),
        "evidence": "Kottakkal Arya Vaidya Sala product monograph; AVP formulary"
    },
    {
        "name": "Amruthu Oil",
        "also_known_as": [
            "Amruth oil", "Amruta oil", "Amrutham oil", "Amruthaprasha oil"
        ],
        "interacts_with_class": ["anticoagulant"],
        "interacts_with_generic": ["warfarin", "acenocoumarol"],
        "risk_level": "low",
        "mechanism": (
            "Ayurvedic medicated oil for external/internal use; contains Tinospora cordifolia "
            "(Guduchi/Amruth) with immunomodulatory properties. When taken internally, "
            "Guduchi may mildly potentiate anticoagulants."
        ),
        "patient_message": (
            "Amruthu Oil/Amruth extract is generally safe. If you take it internally along "
            "with blood-thinning medicine, tell your doctor."
        ),
        "doctor_message": (
            "Tinospora cordifolia (Guduchi) has immunomodulatory and mild antidiabetic "
            "properties. Low interaction risk for topical use. Internal use: monitor INR "
            "with anticoagulants. Clinically significant only in high-dose oral preparations."
        ),
        "evidence": "Ayurvedic Pharmacopoeia of India; Natural Medicines Database"
    }
]

