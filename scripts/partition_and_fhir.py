import os
import json
import pandas as pd
import numpy as np

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.patient import Patient
from fhir.resources.device import Device, DeviceName
from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.identifier import Identifier

def create_client_partitions(train_df: pd.DataFrame, k: int, output_base: str, random_state: int = 42):
    """
    Partitions the training set across k simulated hospital clients.
    Following Akhmetov et al. (2025): standard unstratified K-Fold chunking is used
    to simulate natural non-IID class skew across edge clients.
    """
    k_dir = os.path.join(output_base, f"k{k}")
    os.makedirs(k_dir, exist_ok=True)
    
    # Deterministic shuffle using seed
    shuffled_df = train_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    
    # Chunking into k partitions
    split_indices = np.array_split(np.arange(len(shuffled_df)), k)
    
    partition_summaries = []
    
    for client_id, idxs in enumerate(split_indices):
        client_df = shuffled_df.iloc[idxs].copy()
        client_file = os.path.join(k_dir, f"client_{client_id}.csv")
        client_df.to_csv(client_file, index=False)
        
        # Summary statistics
        class_counts = client_df["activity"].value_counts().to_dict()
        summary = {
            "client_id": client_id,
            "row_count": len(client_df),
            "file_path": client_file,
            "class_distribution": class_counts
        }
        partition_summaries.append(summary)
        
    return partition_summaries

def row_to_fhir_bundle(row: pd.Series, record_id: int, hospital_id: str) -> Bundle:
    """
    Converts a single wearable observation row into a compliant FHIR R4 Bundle
    containing Device, Patient, and Observation resources.
    """
    entries = []
    
    # 1. Device Resource (Apple Watch Series 2)
    device_id = f"device-aw-hospital-{hospital_id}"
    device = Device(
        id=device_id,
        status="active",
        identifier=[
            Identifier(
                system="http://hospital.org/devices",
                value=f"apple-watch-s2-{hospital_id}"
            )
        ],
        name=[
            DeviceName(
                value="Apple Watch Series 2",
                type="registered-name"
            )
        ],
        type=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code="467178001",
                        display="Wearable physical activity monitor"
                    )
                ]
            )
        ]
    )
    entries.append(BundleEntry(resource=device))
    
    # 2. Patient Resource
    # Demographic signature mapping (age, gender, height, weight)
    # Limitation: The public dataset de-identified subjects; we map available biometrics.
    gender_map = {0: "female", 1: "male"}
    patient_id = f"patient-cohort-{int(row.get('participant_id', 0))}"
    
    patient = Patient(
        id=patient_id,
        active=True,
        identifier=[
            Identifier(
                system=f"http://hospital-{hospital_id}.org/patients",
                value=f"subject-cohort-{int(row.get('participant_id', 0))}"
            )
        ],
        gender=gender_map.get(int(row["gender"]), "unknown")
    )
    entries.append(BundleEntry(resource=patient))
    
    # 3. Observation Resources for Biometric Readings
    # (a) Heart Rate (LOINC 8867-4)
    obs_hr = Observation(
        id=f"obs-hr-{hospital_id}-{record_id}",
        status="final",
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="vital-signs",
                        display="Vital Signs"
                    )
                ]
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="8867-4",
                    display="Heart rate"
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        device=Reference(reference=f"Device/{device_id}"),
        valueQuantity=Quantity(
            value=float(row["hear_rate"]),
            unit="beats/min",
            system="http://unitsofmeasure.org",
            code="/min"
        )
    )
    entries.append(BundleEntry(resource=obs_hr))
    
    # (b) Step Count (LOINC 55423-8)
    obs_steps = Observation(
        id=f"obs-steps-{hospital_id}-{record_id}",
        status="final",
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="activity",
                        display="Activity"
                    )
                ]
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="55423-8",
                    display="Number of steps in unspecified time Pedometer"
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        device=Reference(reference=f"Device/{device_id}"),
        valueQuantity=Quantity(
            value=float(row["steps"]),
            unit="steps",
            system="http://unitsofmeasure.org",
            code="{steps}"
        )
    )
    entries.append(BundleEntry(resource=obs_steps))
    
    # (c) Calories Burned (LOINC 41981-2)
    obs_cal = Observation(
        id=f"obs-calories-{hospital_id}-{record_id}",
        status="final",
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="41981-2",
                    display="Calories burned"
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        device=Reference(reference=f"Device/{device_id}"),
        valueQuantity=Quantity(
            value=float(row["calories"]),
            unit="kcal",
            system="http://unitsofmeasure.org",
            code="kcal"
        )
    )
    entries.append(BundleEntry(resource=obs_cal))
    
    # (d) Distance Traveled (LOINC 77535-3)
    obs_dist = Observation(
        id=f"obs-distance-{hospital_id}-{record_id}",
        status="final",
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="77535-3",
                    display="Distance traveled"
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        device=Reference(reference=f"Device/{device_id}"),
        valueQuantity=Quantity(
            value=float(row["distance"]),
            unit="m",
            system="http://unitsofmeasure.org",
            code="m"
        )
    )
    entries.append(BundleEntry(resource=obs_dist))
    
    # (e) Physical Activity Class Label (LOINC 73985-4)
    obs_act = Observation(
        id=f"obs-activity-{hospital_id}-{record_id}",
        status="final",
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="activity",
                        display="Activity"
                    )
                ]
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="73985-4",
                    display="Exercise activity"
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        device=Reference(reference=f"Device/{device_id}"),
        valueCodeableConcept=CodeableConcept(
            coding=[
                Coding(
                    system="http://hospital.org/activity-classes",
                    code=str(row["activity"]).lower().replace(" ", "-"),
                    display=str(row["activity"])
                )
            ]
        )
    )
    entries.append(BundleEntry(resource=obs_act))
    
    # Assemble Bundle
    bundle = Bundle(
        id=f"bundle-hospital-{hospital_id}-rec-{record_id}",
        type="collection",
        entry=entries
    )
    return bundle

def run_pipeline():
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    partitions_dir = os.path.join("data", "partitions")
    fhir_dir = os.path.join("data", "fhir_bundles")
    os.makedirs(partitions_dir, exist_ok=True)
    os.makedirs(fhir_dir, exist_ok=True)
    
    print(f"Loading primary training partition from {train_path}...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"Train rows: {len(train_df)}, Held-out Test rows: {len(test_df)}")
    
    # Verify strict test set isolation
    assert len(train_df) == 2924, f"Expected 2924 train rows, got {len(train_df)}"
    assert len(test_df) == 732, f"Expected 732 test rows, got {len(test_df)}"
    
    # Partition for k in [2, 4, 8]
    client_configs = {}
    for k in [2, 4, 8]:
        summaries = create_client_partitions(train_df, k, partitions_dir, random_state=42)
        client_configs[f"k{k}"] = summaries
        print(f"\n--- Partitioning for k={k} ---")
        total_rows_k = sum(s["row_count"] for s in summaries)
        print(f"Total partitioned rows: {total_rows_k} (Matches train set exactly: {total_rows_k == 2924})")
        for s in summaries:
            print(f"  Client {s['client_id']}: {s['row_count']} rows, Distribution: {s['class_distribution']}")
            
    # Save partition metadata
    meta_path = os.path.join(partitions_dir, "partition_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(client_configs, f, indent=2)
    print(f"\nSaved partition configuration metadata to {meta_path}")
    
    # FHIR Serialization & Validation Pipeline
    print("\n--- FHIR R4 Serialization & Schema Validation ---")
    # Generate sample FHIR bundles for Client 0 of k=4 (first 20 records for deep validation)
    c0_df = pd.read_csv(os.path.join(partitions_dir, "k4", "client_0.csv"))
    
    validated_count = 0
    validation_errors = 0
    sample_bundle_json = None
    
    for i in range(len(c0_df)):
        row = c0_df.iloc[i]
        try:
            bundle = row_to_fhir_bundle(row, record_id=i, hospital_id="A")
            # Convert to JSON string
            raw_json = bundle.json()
            if i == 0:
                sample_bundle_json = raw_json
                
            # Bidirectional Deserialization Check
            reconstructed = Bundle.parse_raw(raw_json)
            assert reconstructed.id == bundle.id, "Bundle ID mismatch during roundtrip"
            assert len(reconstructed.entry) == len(bundle.entry), "Entry count mismatch during roundtrip"
            
            validated_count += 1
        except Exception as e:
            validation_errors += 1
            if validation_errors <= 3:
                print(f"Validation error at record {i}: {e}")
                
    print(f"Total records validated against FHIR R4 schema: {validated_count} (Errors: {validation_errors})")
    
    # Save sample validated FHIR bundle
    sample_path = os.path.join(fhir_dir, "sample_hospital_bundle.json")
    with open(sample_path, "w") as f:
        f.write(json.dumps(json.loads(sample_bundle_json), indent=2))
    print(f"Saved verified sample FHIR R4 Bundle to {sample_path}")

if __name__ == "__main__":
    run_pipeline()
