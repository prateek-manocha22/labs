"""
Lab 06: Healthcare Agents - Solution Template
"""

# def is_anomaly(vitals: dict) -> bool:
#     """
#     Returns True if any vital sign is outside the normal range.
    
#     Thresholds:
#     - Heart Rate: [60, 100]
#     - BP Systolic: [90, 140]
#     - BP Diastolic: [60, 90]
#     - Oxygen Saturation: [95, 100]
#     """
#     # TODO: Implement anomaly detection logic
#     return False

# def recommend_intervention(vitals: dict, history: list = None) -> str:
#     """
#     Suggests an intervention based on the anomaly status.
#     """
#     if is_anomaly(vitals):
#         return "Immediate Physician Review"
#     return "Continue Observation"


#_----------------------------------------------------------------------
"""
Lab 06: Healthcare Agents - Solution Template
"""

def is_anomaly(vitals: dict) -> bool:
    """
    Returns True if any vital sign is outside the normal range.
    
    Thresholds:
    - Heart Rate: [60, 100]
    - BP Systolic: [90, 140]
    - BP Diastolic: [60, 90]
    - Oxygen Saturation: [95, 100]
    """
    # TODO: Implement anomaly detection logic
    if not (60 <= vitals["heart_rate"] <= 100):
        return True
    if not (90 <= vitals["blood_pressure_sys"] <= 140):
        return True
    if not (60 <= vitals["blood_pressure_dia"] <= 90):
        return True
    if not (95 <= vitals["oxygen_saturation"] <= 100):
        return True
    return False

def recommend_intervention(vitals: dict, history: list = None) -> str:
    """
    Suggests an intervention based on the anomaly status.
    """
    if is_anomaly(vitals):
        return "Immediate Physician Review"
    return "Continue Observation"