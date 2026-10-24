# models.py

from pydantic import BaseModel
from typing import List, Optional

class PatientProfile(BaseModel):
    age: int
    diabetes: bool = False
    hypertension: bool = False
    ckd: bool = False                          # chronic kidney disease
    liver_disease: bool = False
    kidney_function: str = "normal"            # "normal", "mild", "moderate", "severe"
    caregiver_phone: Optional[str] = None

        # --- Phase 2 patient fields ---
    sex: str = "male"                  # "male" or "female"
    pregnant: bool = False
    breastfeeding: bool = False
    gi_bleed_history: bool = False
    heart_failure: bool = False
    alcohol: bool = False
    copd: bool = False
    sleep_apnoea: bool = False
    dehydration: bool = False
    bradycardia: bool = False
    hypokalemia: bool = False
    hypomagnesemia: bool = False



class AnalyzeRequest(BaseModel):
    device_id: str = "web-dashboard"
    scanned_medicines: List[str]               # List of brand name strings
    scanned_tags: List[str] = []               # raw NFC tag UIDs (resolved by backend)
    ayurvedic_medicines: List[str] = []        # List of Ayurvedic medicine names
    foods: List[str] = []                      # List of food_key strings
    patient: PatientProfile

class InteractionAlert(BaseModel):
    rule_id: str
    name: str
    severity: str                              # "low", "moderate", "high", "critical"
    risk_category: str
    medicines_involved: List[str]
    patient_explanation: str
    doctor_explanation: str
    evidence: str
    action: str
    monitoring: str
    refer_to_doctor: bool = False      # True = identify the risk, refer to a doctor


class BurdenScore(BaseModel):
    kidney: int    # 1-10
    liver: int     # 1-10
    cardiac: int   # 1-10
    bleeding: int  # 1-10
    cns: int       # 1-10
    overall: float # average

class DeprescribeResult(BaseModel):
    removed_medicine: str
    new_severity: str
    risk_reduction: str
    suggested_alternative: Optional[str] = None

class HoldBack(BaseModel):
    """The ONE medicine being held back, and the compartment it lives in."""
    medicine: str
    compartment: int
    reason: str


class AnalyzeResponse(BaseModel):
    overall_risk: str                          # "low", "moderate", "high", "critical"
    alerts: List[InteractionAlert]
    burden_score: BurdenScore
    lock_compartments: List[int]               # compartment numbers [1,2,3] to lock
    hold_backs: List[HoldBack] = []            # WHICH medicine is held back, and why
    buzzer: bool
    display_text: str                          # for OLED (max 4 lines of 20 chars)
    tag_names: dict = {}                       # uid -> brand, so the box refreshes its copy
    whatsapp_sent: bool
    unrecognized_medicines: List[str] = []    # brands not found in database
    pending_tags: List[str] = []               # tag UIDs tapped but not assigned yet

class SimulateRemoveRequest(BaseModel):
    scanned_medicines: List[str]
    ayurvedic_medicines: List[str] = []
    foods: List[str] = []
    patient: PatientProfile
    remove_medicine: str                       # which one to simulate removing

class SimulateRemoveResponse(BaseModel):
    original_risk: str
    new_risk: str
    deprescribe_result: DeprescribeResult
    all_original_alerts: List[InteractionAlert]
    remaining_alerts: List[InteractionAlert]