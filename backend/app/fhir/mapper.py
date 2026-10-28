import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import pandas as pd

class FHIRDataServiceAgent:
    """
    FHIR Data Service Agent (DS Agent) as defined in Akhmetov et al. (2025).
    Translates raw wearable device data into standardized HL7 FHIR R4 resources:
    - Patient
    - Device
    - Observation (Heart Rate, Steps, Calories, Temperature, Accelerometer, Activity)
    """
    def __init__(self):
        pass

    def map_apple_watch_record(self, row: Dict[str, Any], record_idx: int = 1) -> Dict[str, Any]:
        patient_id = f"patient-aw-{record_idx:04d}"
        device_id = f"device-apple-watch-s2"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Patient resource
        gender_str = "female" if str(row.get("gender", "")).lower() in ["female", "f", "0"] else "male"
        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [{
                "system": "http://hospital-federation.org/patients",
                "value": patient_id
            }],
            "gender": gender_str,
            "extension": [{
                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                "valueInteger": int(row.get("age", 25))
            }]
        }

        # Device resource
        device = {
            "resourceType": "Device",
            "id": device_id,
            "name": [{
                "value": "Apple Watch Series 2",
                "type": "user-friendly-name"
            }]
        }

        # Observations
        observations = []

        # 1. Heart Rate: LOINC 8867-4
        if "hear_rate" in row and pd.notnull(row["hear_rate"]):
            obs_hr = {
                "resourceType": "Observation",
                "id": f"obs-hr-{record_idx}",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "device": {"reference": f"Device/{device_id}"},
                "effectiveDateTime": now_iso,
                "valueQuantity": {
                    "value": round(float(row["hear_rate"]), 1),
                    "unit": "beats/min",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min"
                }
            }
            observations.append(obs_hr)

        # 2. Step Count: LOINC 55423-8
        if "steps" in row and pd.notnull(row["steps"]):
            obs_steps = {
                "resourceType": "Observation",
                "id": f"obs-steps-{record_idx}",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "activity",
                        "display": "Activity"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "55423-8",
                        "display": "Number of steps in 24 hour Measured"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "device": {"reference": f"Device/{device_id}"},
                "effectiveDateTime": now_iso,
                "valueQuantity": {
                    "value": int(float(row["steps"])),
                    "unit": "steps",
                    "system": "http://unitsofmeasure.org",
                    "code": "1"
                }
            }
            observations.append(obs_steps)

        # 3. Activity Type: LOINC 68516-4
        if "activity" in row and pd.notnull(row["activity"]):
            obs_act = {
                "resourceType": "Observation",
                "id": f"obs-activity-{record_idx}",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "activity",
                        "display": "Activity"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "68516-4",
                        "display": "Physical activity level"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "device": {"reference": f"Device/{device_id}"},
                "effectiveDateTime": now_iso,
                "valueCodeableConcept": {
                    "text": str(row["activity"])
                }
            }
            observations.append(obs_act)

        return {
            "patient": patient,
            "device": device,
            "observations": observations
        }

    def map_dat263x_record(self, row: Dict[str, Any], record_idx: int = 1) -> Dict[str, Any]:
        user_id = str(row.get("User_ID", record_idx))
        patient_id = f"patient-dat263x-{user_id}"
        now_iso = datetime.now(timezone.utc).isoformat()

        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "gender": str(row.get("Gender", "male")).lower(),
            "extension": [{
                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                "valueInteger": int(row.get("Age", 30))
            }]
        }

        device = {
            "resourceType": "Device",
            "id": "device-fitness-sensor",
            "name": [{"value": "Biometric Workout Tracker", "type": "user-friendly-name"}]
        }

        observations = []
        # Calorie expenditure: LOINC 41981-2
        if "Calories" in row and pd.notnull(row["Calories"]):
            observations.append({
                "resourceType": "Observation",
                "id": f"obs-cal-{record_idx}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "41981-2",
                        "display": "Calories burned"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now_iso,
                "valueQuantity": {
                    "value": round(float(row["Calories"]), 1),
                    "unit": "kcal",
                    "system": "http://unitsofmeasure.org",
                    "code": "kcal"
                }
            })

        # Heart rate during exercise: LOINC 8867-4
        if "Heart_Rate" in row and pd.notnull(row["Heart_Rate"]):
            observations.append({
                "resourceType": "Observation",
                "id": f"obs-hr-{record_idx}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now_iso,
                "valueQuantity": {
                    "value": round(float(row["Heart_Rate"]), 1),
                    "unit": "beats/min",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min"
                }
            })

        # Body temperature: LOINC 8310-5
        if "Body_Temp" in row and pd.notnull(row["Body_Temp"]):
            observations.append({
                "resourceType": "Observation",
                "id": f"obs-temp-{record_idx}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8310-5",
                        "display": "Body temperature"
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": now_iso,
                "valueQuantity": {
                    "value": round(float(row["Body_Temp"]), 1),
                    "unit": "Cel",
                    "system": "http://unitsofmeasure.org",
                    "code": "Cel"
                }
            })

        return {
            "patient": patient,
            "device": device,
            "observations": observations
        }

fhir_mapper = FHIRDataServiceAgent()
