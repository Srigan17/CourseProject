from backend.app.fhir.mapper import fhir_mapper
from backend.app.fhir.validator import fhir_validator

def test_apple_watch_to_fhir_mapping_and_validation():
    sample_row = {
        "age": 28,
        "gender": "female",
        "height": 165,
        "weight": 60,
        "steps": 4500,
        "hear_rate": 78,
        "activity": "Self Pace walk"
    }
    bundle = fhir_mapper.map_apple_watch_record(sample_row, record_idx=1)
    
    assert "patient" in bundle
    assert "device" in bundle
    assert "observations" in bundle
    assert len(bundle["observations"]) == 3  # HR, steps, activity

    # Validate each
    p_val = fhir_validator.validate_resource(bundle["patient"])
    assert p_val.is_valid is True

    d_val = fhir_validator.validate_resource(bundle["device"])
    assert d_val.is_valid is True

    for obs in bundle["observations"]:
        o_val = fhir_validator.validate_resource(obs)
        assert o_val.is_valid is True

def test_dat263x_to_fhir_mapping():
    sample_row = {
        "User_ID": 1001,
        "Gender": "male",
        "Age": 35,
        "Height": 180,
        "Weight": 75,
        "Duration": 25,
        "Heart_Rate": 115,
        "Body_Temp": 39.5,
        "Calories": 180.0
    }
    bundle = fhir_mapper.map_dat263x_record(sample_row, record_idx=1)
    assert bundle["patient"]["resourceType"] == "Patient"
    assert len(bundle["observations"]) == 3  # Calories, HR, Temp
