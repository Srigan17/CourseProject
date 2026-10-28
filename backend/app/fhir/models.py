from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class FHIRMappingDefinition(BaseModel):
    source_field: str
    fhir_resource: str
    loinc_code: Optional[str] = None
    loinc_display: Optional[str] = None
    unit: Optional[str] = None
    description: str

class FHIRValidationResult(BaseModel):
    is_valid: bool
    resource_type: str
    resource_id: str
    errors: List[str] = []
    warnings: List[str] = []
