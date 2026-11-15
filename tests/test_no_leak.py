"""The test set must share no rows with the training set (no leakage)."""
from pathlib import Path

import pandas as pd

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]


def test_no_vitals_shared_between_train_and_test():
    train = pd.read_csv(PROCESSED / "train.csv")
    test = pd.read_csv(PROCESSED / "test.csv")
    # Compare on the 6 vitals only (stricter than comparing whole rows):
    # the same vitals with a different label would still be a leak.
    shared = train.merge(test, on=FEATURES, how="inner")
    assert len(shared) == 0, f"{len(shared)} vitals rows appear in both train and test"


def test_split_covers_clean_data_exactly():
    clean = pd.read_csv(PROCESSED / "clean.csv")
    train = pd.read_csv(PROCESSED / "train.csv")
    test = pd.read_csv(PROCESSED / "test.csv")
    assert len(train) + len(test) == len(clean)
    assert not clean.duplicated(subset=FEATURES).any()
    # Stratified: every class is present on both sides.
    assert set(train["RiskLevel"]) == set(test["RiskLevel"]) == {"low", "mid", "high"}
