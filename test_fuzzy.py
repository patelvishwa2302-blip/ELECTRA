from ocr import _known_names, _find_brand

brands, lookup = _known_names()

tests = [
    ("Ecoeprin 75",   "Ecosprin 75"),
    ("Bruffen 400",   "Brufen 400"),
    ("Glycomed 500",  "Glycomet 500"),
    ("Metolar25",     "Metolar 25"),
    ("Ecosprin",      "Ecosprin 75"),
    ("Tab Brufen",    "Brufen 400"),
    ("Pantocid40",    "Pantop 40"),
    ("Glycomat 500",  "Glycomet 500"),
    ("Stamlo5",       "Stamlo 5"),
    ("Clopilet75",    "Clopilet 75"),
]

print(f"{'Input':<25} {'Expected':<20} {'Got':<20} OK?")
print("-" * 80)
for inp, expected in tests:
    got = _find_brand(inp, brands, lookup)
    if got == expected:
        status = "YES"
    elif got:
        status = "PARTIAL -> " + str(got)
    else:
        status = "MISS"
    print(f"{inp:<25} {expected:<20} {str(got):<20} {status}")
