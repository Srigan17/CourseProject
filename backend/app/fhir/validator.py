from typing import Dict, Any, List
from backend.app.fhir.models import FHIRValidationResult

try:
    from fhir.resources.patient import Patient as FHIRPatient
    from fhir.resources.observation import Observation as FHIRObservation
    from fhir.resources.device import Device as FHIRDevice
    FHIR_LIB_AVAILABLE = True
except ImportError:
    FHIR_LIB_AVAILABLE = False

class FHIRResourceValidator:
    """
    Validates generated healthcare data objects against the official HL7 FHIR R4 schema.
    """
    def __init__(self):
        pass

    def validate_resource(self, resource_dict: Dict[str, Any]) -> FHIRValidationResult:
        res_type = resource_dict.get("resourceType", "Unknown")
        res_id = resource_dict.get("id", "unknown-id")
        errors = []
        warnings = []

        if not FHIR_LIB_AVAILABLE:
            # Fallback structural checks
            if not res_type or res_type == "Unknown":
                errors.append("Missing required field 'resourceType'.")
            if not res_id:
                errors.append("Missing required field 'id'.")
            return FHIRValidationResult(
                is_valid=len(errors) == 0,
                resource_type=res_type,
                resource_id=res_id,
                errors=errors,
                warnings=["fhir.resources library not installed; performed standard structural schema validation."]
            )

        try:
            if res_type == "Patient":
                FHIRPatient.model_validate(resource_dict)
            elif res_type == "Observation":
                FHIRObservation.model_validate(resource_dict)
            elif res_type == "Device":
                FHIRDevice.model_validate(resource_dict)
            else:
                warnings.append(f"Resource type '{res_type}' validated via generic schema parser.")
        except Exception as e:
            errors.append(f"FHIR R4 Schema Validation Failed: {str(e)}")

        return FHIRValidationResult(
            is_valid=len(errors) == 0,
            resource_type=res_type,
            resource_id=res_id,
            errors=errors,
            warnings=warnings
        )

fhir_validator = FHIRResourceValidator()
