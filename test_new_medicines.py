"""
test_new_medicines.py
Verifies all the newly added medicines work correctly.
"""
from database import lookup_medicine
from ayurvedic_db import AYURVEDIC_INTERACTIONS

print("=" * 60)
print("ALLOPATHIC — new medicines from prescription photos")
print("=" * 60)

allopathic_tests = [
    # Photo 4
    ("Actinac-SP",     "Actinac-SP"),
    ("Tab. Actinac-SP","Actinac-SP"),
    ("Actinac SP",     "Actinac-SP"),
    ("Actirac SP",     "Actinac-SP"),   # OCR misread
    ("Zerodol-SP",     "Zerodol-SP"),
    # Photo 5
    ("Impacte",        "Imol Plus"),
    ("Imol",           "Imol Plus"),
    ("Combiflam",      "Combiflam"),
    ("Glucorel",       "Glycorel 5"),
    ("Glycorel 5",     "Glycorel 5"),
    ("Glipizide",      "Glycorel 5"),
    ("Omez",           "Omez 20"),
    ("Omeprazole",     "Omez 20"),
    ("Pan-D",          "Pan-D"),
    ("Pan D",          "Pan-D"),
]

all_ok = True
for inp, expected in allopathic_tests:
    result = lookup_medicine(inp)
    got = result["brand"] if result else "NOT FOUND"
    ok = "YES" if got == expected else "FAIL"
    if ok == "FAIL":
        all_ok = False
    print(f"  {ok}  {inp:<25} -> {got}")

print()
print("=" * 60)
print("AYURVEDIC — new medicines from Kerala Ayurveda Sala")
print("=" * 60)

ayurveda_tests = [
    "Ashokarishta", "Ashokrishta", "Asokarishta", "Asokarishtam",
    "Chandanasava", "Chandanasavam",
    "Dhanwantharam Gulika", "Dhanwantharghulika",
    "Sukumara Kwatham", "Sukumara Kvaltham",
    "Kumaryasava", "Kumaryogasavam",
    "Rajapravarti Vatika", "Rajapraverti Vadikg",
    "Mensokot", "Mensa Kot",
    "Amruthu Oil", "Amruth oil",
]

ayur_names = [e["name"] for e in AYURVEDIC_INTERACTIONS]
ayur_aliases = []
for e in AYURVEDIC_INTERACTIONS:
    ayur_aliases.extend(e.get("also_known_as", []))

for name in ayurveda_tests:
    found = any(
        name.lower() in n.lower() or n.lower() in name.lower()
        for n in ayur_names + ayur_aliases
    )
    print(f"  {'YES' if found else 'FAIL'}  {name}")
    if not found:
        all_ok = False

print()
print("=" * 60)
if all_ok:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED — check above")
print("=" * 60)
