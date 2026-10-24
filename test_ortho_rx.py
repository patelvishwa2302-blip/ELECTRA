"""
Simulates exactly what Electra shows when you enter the
Joint Line Orthopaedic Hospital prescription medicines.
"""
from risk_engine import analyze_medicines
from models import PatientProfile

# The medicines on the bill (as OCR would return them)
medicines = ["Apofec-SP", "Deflamat 6", "Reabzo-D"]
patient = PatientProfile(age=45, diabetes=False, hypertension=False, ckd=False, liver_disease=False)

result = analyze_medicines(
    scanned_brands=medicines,
    ayurvedic_list=[],
    food_list=[],
    patient=patient
)

print("=" * 65)
print("ELECTRA ANALYSIS — Joint Line Orthopaedic Prescription")
print("=" * 65)
print(f"\nOVERALL RISK: {result['overall_risk'].upper()}")
print(f"Buzzer:       {'YES' if result['buzzer'] else 'No'}")
print(f"Lock comps:   {result['lock_compartments'] or 'None'}")
print(f"\nOLED display:\n{result['display_text']}")

print(f"\nALERTS ({len(result['alerts'])}):")
for a in result['alerts']:
    print(f"\n  [{a.severity.upper()}] {a.name}")
    print(f"  Medicines: {', '.join(a.medicines_involved)}")
    print(f"  Patient:   {a.patient_explanation}")
    print(f"  Action:    {a.action}")
    print(f"  Evidence:  {a.evidence}")

b = result['burden_score']
print(f"\nBURDEN SCORE: Kidney={b.kidney} Liver={b.liver} "
      f"Cardiac={b.cardiac} Bleeding={b.bleeding} CNS={b.cns} "
      f"Overall={b.overall}/10")

unrecog = result.get('unrecognized_medicines', [])
print(f"\nUnrecognized: {unrecog if unrecog else 'None -- all recognised!'}")
print("\n" + "=" * 65)
