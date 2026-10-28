import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.preprocessing import LabelEncoder

def prepare_data():
    raw_path = os.path.join("data", "raw", "aw_fb_data.csv")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Reading raw dataset from {raw_path}...")
    df_raw = pd.read_csv(raw_path)
    print(f"Raw shape: {df_raw.shape}")
    
    # 1. Filter for Apple Watch data as done in Akhmetov et al. (2025)
    aw_df = df_raw[df_raw["device"] == "apple watch"].copy()
    print(f"Apple Watch subset shape: {aw_df.shape}")
    
    # 2. Drop non-feature index / device identifier columns
    cols_to_drop = ["Unnamed: 0", "X1", "device"]
    aw_clean = aw_df.drop(columns=[c for c in cols_to_drop if c in aw_df.columns]).copy()
    
    # 3. Create synthetic participant_id based on unique demographic tuple
    demo_cols = ["age", "gender", "height", "weight"]
    profiles = aw_clean.groupby(demo_cols).ngroup()
    aw_clean["participant_id"] = profiles
    n_participants = aw_clean["participant_id"].nunique()
    print(f"Constructed participant_id: {n_participants} unique participant cohorts found.")
    
    # 4. Save clean base dataset
    base_path = os.path.join(processed_dir, "apple_watch_clean.csv")
    aw_clean.to_csv(base_path, index=False)
    print(f"Saved cleaned Apple Watch dataset to {base_path}")
    
    # 5. Track 1: Sample-Level 80/20 Train/Test Split (for Paper Replication)
    # Stratified by target activity to maintain class balance in both splits
    train_sample, test_sample = train_test_split(
        aw_clean,
        test_size=0.20,
        random_state=42,
        stratify=aw_clean["activity"]
    )
    
    train_sample_path = os.path.join(processed_dir, "train_sample_split.csv")
    test_sample_path = os.path.join(processed_dir, "test_sample_split.csv")
    train_sample.to_csv(train_sample_path, index=False)
    test_sample.to_csv(test_sample_path, index=False)
    print(f"\n[Sample-Level Split] Train: {train_sample.shape[0]} rows, Test: {test_sample.shape[0]} rows")
    
    # 6. Track 2: Participant-Grouped Split (Evaluating Generalization to Unseen Subjects)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(aw_clean, groups=aw_clean["participant_id"]))
    train_grouped = aw_clean.iloc[train_idx].copy()
    test_grouped = aw_clean.iloc[test_idx].copy()
    
    train_grouped_path = os.path.join(processed_dir, "train_grouped_split.csv")
    test_grouped_path = os.path.join(processed_dir, "test_grouped_split.csv")
    train_grouped.to_csv(train_grouped_path, index=False)
    test_grouped.to_csv(test_grouped_path, index=False)
    
    train_p = train_grouped["participant_id"].nunique()
    test_p = test_grouped["participant_id"].nunique()
    overlap_p = set(train_grouped["participant_id"]).intersection(set(test_grouped["participant_id"]))
    print(f"[Participant-Grouped Split] Train: {train_grouped.shape[0]} rows ({train_p} subjects), Test: {test_grouped.shape[0]} rows ({test_p} subjects)")
    print(f"Participant Overlap in Grouped Split: {len(overlap_p)} subjects")
    
    # 7. Verification of Target Distribution
    print("\n--- Class Distribution: Sample Split ---")
    dist_df = pd.DataFrame({
        "Full Dataset": aw_clean["activity"].value_counts(),
        "Train Sample": train_sample["activity"].value_counts(),
        "Test Sample": test_sample["activity"].value_counts(),
        "Test %": (test_sample["activity"].value_counts() / aw_clean["activity"].value_counts() * 100).round(2)
    })
    print(dist_df)
    
    print("\n--- Class Distribution: Grouped Split ---")
    dist_grp_df = pd.DataFrame({
        "Train Grouped": train_grouped["activity"].value_counts(),
        "Test Grouped": test_grouped["activity"].value_counts(),
        "Test %": (test_grouped["activity"].value_counts() / aw_clean["activity"].value_counts() * 100).round(2)
    })
    print(dist_grp_df)

if __name__ == "__main__":
    prepare_data()
