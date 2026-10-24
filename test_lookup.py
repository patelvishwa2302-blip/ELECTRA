from database import lookup_medicine

tests = [
    "Ecosprin 75",
    "ecosprin 75",
    "Ibuprofen",
    "Paracetamol",
    "Atorvastatin",
    "Aspirin",
    "Dolo 650",
    "Pantocid",
    "Tab Ecosprin 75",   # as OCR might return it with "Tab"
    "Tab. Ecosprin 75",  # with dot
    "Brufen 400mg",      # with mg suffix
    "Glycomet",
    "Amlodipine 5mg",
    "Metformin 500",
    "Atorva 10",         # brand NOT in database
    "Telvas 40",         # brand NOT in database
    "Nexito",            # brand NOT in database
]

print("=" * 55)
print(f"{'Input':<30} {'Result'}")
print("=" * 55)
for t in tests:
    result = lookup_medicine(t)
    found = result["brand"] if result else "NOT FOUND"
    print(f"{t:<30} {found}")
