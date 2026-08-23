#!/usr/bin/env python3
"""
Data Leakage & Speaker-Disjoint Split Verification Tool.

Enforces Constraint RC-07 (Strict Patient/Speaker Disjoint Splits) and
Constraint RC-06 (Speaker-Level Evaluation).

Usage:
    python model/src/evaluation/leakage_check.py
    python model/src/evaluation/leakage_check.py --manifest path/to/split_manifest.json
"""

import sys
import json
import csv
import argparse
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Split manifest not found at: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_split_integrity(manifest: dict, raw_index_path: Path = None) -> bool:
    print("=" * 70)
    print("RUNNING DATA LEAKAGE & SPEAKER DISJOINTNESS AUDIT")
    print(f"Dataset: {manifest.get('dataset_name')} ({manifest.get('dataset_version')})")
    print("=" * 70)

    splits = manifest.get("splits", {})
    train_speakers = set(splits.get("train", {}).get("speakers", []))
    val_speakers = set(splits.get("val", {}).get("speakers", []))
    test_speakers = set(splits.get("test", {}).get("speakers", []))

    all_speakers = train_speakers | val_speakers | test_speakers
    print(f"Total Unique Speakers in Splits: {len(all_speakers)}")
    print(f"  - Train Speakers: {len(train_speakers)}")
    print(f"  - Val Speakers:   {len(val_speakers)}")
    print(f"  - Test Speakers:  {len(test_speakers)}")

    violations = []

    # 1. Non-empty partitions
    if not train_speakers:
        violations.append("Train partition has 0 speakers!")
    if not val_speakers:
        violations.append("Val partition has 0 speakers!")
    if not test_speakers:
        violations.append("Test partition has 0 speakers!")

    # 2. Pairwise disjointness checks
    train_val_leakage = train_speakers & val_speakers
    if train_val_leakage:
        violations.append(f"LEAKAGE DETECTED: {len(train_val_leakage)} speaker(s) in BOTH Train and Val: {train_val_leakage}")

    train_test_leakage = train_speakers & test_speakers
    if train_test_leakage:
        violations.append(f"LEAKAGE DETECTED: {len(train_test_leakage)} speaker(s) in BOTH Train and Test: {train_test_leakage}")

    val_test_leakage = val_speakers & test_speakers
    if val_test_leakage:
        violations.append(f"LEAKAGE DETECTED: {len(val_test_leakage)} speaker(s) in BOTH Val and Test: {val_test_leakage}")

    # 3. Cross-Validation fold disjointness checks
    cv_folds = manifest.get("cross_validation_folds", {})
    print(f"\nChecking {len(cv_folds)} Cross-Validation Folds:")
    for fold_name, fold_data in cv_folds.items():
        f_train = set(fold_data.get("train_speakers", []))
        f_val = set(fold_data.get("val_speakers", []))
        f_leak = f_train & f_val
        if f_leak:
            violations.append(f"CV LEAKAGE in {fold_name}: {len(f_leak)} speaker(s) in both train and val: {f_leak}")
        else:
            print(f"  ✓ {fold_name}: Train ({len(f_train)}) and Val ({len(f_val)}) are strictly disjoint.")

    # 4. If raw_index provided, verify every recording belongs to exactly one split
    if raw_index_path and raw_index_path.exists():
        print(f"\nVerifying against raw index: {raw_index_path}")
        index_speakers = set()
        with open(raw_index_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                spk = row.get("speaker_id", "").strip()
                if spk:
                    index_speakers.add(spk)
        unassigned_speakers = index_speakers - all_speakers
        if unassigned_speakers:
            violations.append(f"Orphan speakers in raw index missing from split manifest: {unassigned_speakers}")
        else:
            print(f"  ✓ All {len(index_speakers)} speakers from raw index are mapped to splits.")

    # Print Class Balance per Split
    print("\n--- Class Balance per Partition ---")
    for split_name, sdata in splits.items():
        cb = sdata.get("class_balance", {})
        print(f"  {split_name.upper():<5}: {cb} (Total: {sdata.get('speaker_count')} speakers, {sdata.get('recording_count', 'N/A')} recordings)")

    print("=" * 70)
    if violations:
        print("❌ LEAKAGE CHECK FAILED WITH VIOLATIONS:")
        for v in violations:
            print(f"  - {v}")
        return False

    print("✅ SUCCESS: Zero data leakage detected! All splits and CV folds are strictly speaker-disjoint.")
    print("=" * 70)
    return True


def main():
    parser = argparse.ArgumentParser(description="Audit split manifest for speaker leakage.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to split_manifest.json"
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Path to raw_index.csv (optional)"
    )
    args = parser.parse_args()

    # Locate manifest if not specified
    if args.manifest is None:
        candidate = Path("model/artifacts/split_manifest_v1.0-20260823.json")
        if not candidate.exists():
            candidates = list(Path("model/artifacts").glob("split_manifest_*.json"))
            if candidates:
                candidate = candidates[0]
            else:
                print("Error: No split manifest found in model/artifacts/")
                sys.exit(1)
        args.manifest = candidate

    manifest_data = load_manifest(args.manifest)
    success = verify_split_integrity(manifest_data, args.index)
    if not success:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
