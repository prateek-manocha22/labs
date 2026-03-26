import pytest
from solution import is_anomaly, recommend_intervention

def test_normal_vitals():
    vitals = {
        "heart_rate": 75,
        "blood_pressure_sys": 120,
        "blood_pressure_dia": 80,
        "oxygen_saturation": 98
    }
    assert is_anomaly(vitals) is False
    assert recommend_intervention(vitals) == "Continue Observation"

def test_heart_rate_anomaly():
    vitals = {
        "heart_rate": 110,
        "blood_pressure_sys": 120,
        "blood_pressure_dia": 80,
        "oxygen_saturation": 98
    }
    assert is_anomaly(vitals) is True
    assert recommend_intervention(vitals) == "Immediate Physician Review"

def test_oxygen_anomaly():
    vitals = {
        "heart_rate": 75,
        "blood_pressure_sys": 120,
        "blood_pressure_dia": 80,
        "oxygen_saturation": 92
    }
    assert is_anomaly(vitals) is True
    assert recommend_intervention(vitals) == "Immediate Physician Review"

def test_borderline_cases():
    # Exactly on threshold should be normal
    vitals = {
        "heart_rate": 60,
        "blood_pressure_sys": 140,
        "blood_pressure_dia": 90,
        "oxygen_saturation": 95
    }
    assert is_anomaly(vitals) is False
