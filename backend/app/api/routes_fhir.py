from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List
from backend.app.ml.datasets import dataset_manager
from backend.app.fhir.mapper import fhir_mapper
from backend.app.fhir.validator import fhir_validator

router = APIRouter(prefix="/fhir", tags=["FHIR Interoperability"])

@router.get("/status")
def get_fhir_status() -> Dict[str, Any]:
    return {
        "fhir_version": "HL7 FHIR Release 4 (R4) v4.0.1",
        "supported_resources": ["Patient", "Device", "Observation"],
        "interoperability_standard": "Syntactic & Semantic FHIR Interoperability",
        "loinc_codes": {
            "8867-4": "Heart rate (beats/min)",
            "55423-8": "Step count (steps)",
            "41981-2": "Calories burned / Energy expenditure (kcal)",
            "68516-4": "Physical activity level / Category",
            "8310-5": "Body temperature (Cel)"
        },
        "privacy_rule": "Raw FHIR patient resources reside strictly in local simulated organization silos. Model training exchanges parameters, not patient records."
    }

@router.get("/mappings")
def get_mappings() -> List[Dict[str, Any]]:
    return [
        {
            "source_dataset": "Apple Watch / Fitbit",
            "source_field": "hear_rate",
            "fhir_resource": "Observation",
            "loinc_code": "8867-4",
            "loinc_display": "Heart rate",
            "unit": "beats/min"
        },
        {
            "source_dataset": "Apple Watch / Fitbit",
            "source_field": "steps",
            "fhir_resource": "Observation",
            "loinc_code": "55423-8",
            "loinc_display": "Number of steps in 24 hour Measured",
            "unit": "steps"
        },
        {
            "source_dataset": "Apple Watch / Fitbit",
            "source_field": "activity",
            "fhir_resource": "Observation",
            "loinc_code": "68516-4",
            "loinc_display": "Physical activity level",
            "unit": "codeable concept"
        },
        {
            "source_dataset": "DAT263x",
            "source_field": "Calories",
            "fhir_resource": "Observation",
            "loinc_code": "41981-2",
            "loinc_display": "Calories burned",
            "unit": "kcal"
        },
        {
            "source_dataset": "DAT263x",
            "source_field": "Body_Temp",
            "fhir_resource": "Observation",
            "loinc_code": "8310-5",
            "loinc_display": "Body temperature",
            "unit": "Cel"
        }
    ]

@router.get("/generate/{dataset_id}")
def generate_fhir_from_dataset(dataset_id: str, record_index: int = Query(0, ge=0)) -> Dict[str, Any]:
    try:
        df = dataset_manager.load_dataset(dataset_id)
        if record_index >= len(df):
            raise IndexError(f"Record index {record_index} out of range (max {len(df)-1}).")
        row = df.iloc[record_index].to_dict()

        if dataset_id == "apple_watch":
            bundle = fhir_mapper.map_apple_watch_record(row, record_idx=record_index + 1)
        elif dataset_id == "dat263x":
            bundle = fhir_mapper.map_dat263x_record(row, record_idx=record_index + 1)
        else:
            bundle = fhir_mapper.map_apple_watch_record(row, record_idx=record_index + 1)

        # Validate generated resources
        val_patient = fhir_validator.validate_resource(bundle["patient"])
        val_device = fhir_validator.validate_resource(bundle["device"])
        val_observations = [fhir_validator.validate_resource(obs) for obs in bundle["observations"]]

        return {
            "dataset_id": dataset_id,
            "source_record": row,
            "fhir_bundle": bundle,
            "validation": {
                "patient_valid": val_patient.is_valid,
                "device_valid": val_device.is_valid,
                "observations_valid": all(v.is_valid for v in val_observations),
                "errors": val_patient.errors + val_device.errors + [e for v in val_observations for e in v.errors]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate")
def validate_custom_fhir_resource(resource: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    res = fhir_validator.validate_resource(resource)
    return res.model_dump()
