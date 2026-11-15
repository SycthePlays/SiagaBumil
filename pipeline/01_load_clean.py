"""Phase 1 — load the UCI Maternal Health Risk data and clean it.

Run:  python pipeline/01_load_clean.py
Out:  data/raw/maternal_health_risk.csv   (untouched original, committed)
      data/processed/clean.csv            (what every later script uses)
      results/cleaning_log.json           (row counts for DATA.md / README)

Why this order matters: the public file contains many repeated rows. If we
split first, the same mother's numbers land in both train and test and the
test score looks better than it really is (leakage). So we clean BEFORE
splitting.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "maternal_health_risk.csv"
CLEAN = ROOT / "data" / "processed" / "clean.csv"
LOG = ROOT / "results" / "cleaning_log.json"

FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
LABEL = "RiskLevel"


def load_raw() -> pd.DataFrame:
    """Use the committed CSV if it exists; download from UCI only the first time.
    This keeps the pipeline reproducible offline and in Colab."""
    if not RAW.exists():
        from ucimlrepo import fetch_ucirepo

        data = fetch_ucirepo(id=863).data
        RAW.parent.mkdir(parents=True, exist_ok=True)
        pd.concat([data.features, data.targets], axis=1).to_csv(RAW, index=False)
    return pd.read_csv(RAW)


def main() -> None:
    df = load_raw()
    assert list(df.columns) == FEATURES + [LABEL], df.columns
    assert df.isna().sum().sum() == 0, "unexpected missing values"

    # "low risk" -> "low" etc. Shorter names, same meaning.
    df[LABEL] = df[LABEL].str.replace(" risk", "", regex=False)
    assert set(df[LABEL]) == {"low", "mid", "high"}

    log = {"raw_rows": len(df), "raw_class_counts": df[LABEL].value_counts().to_dict()}

    # 1) Exact duplicates: same 6 vitals AND same label. Keep one copy.
    dedup = df.drop_duplicates()
    log["exact_duplicate_rows_removed"] = len(df) - len(dedup)
    log["rows_after_exact_dedupe"] = len(dedup)

    # 2) Conflicting duplicates: same 6 vitals but DIFFERENT labels.
    # We cannot know which label is right, and keeping them would let the
    # same vitals sit in both train and test. So we drop the whole group
    # and report how many there were (it is a finding about label noise).
    conflict = dedup.duplicated(subset=FEATURES, keep=False)
    log["conflicting_vital_groups"] = int(dedup[conflict].groupby(FEATURES).ngroups)
    log["conflicting_rows_removed"] = int(conflict.sum())
    clean = dedup[~conflict]

    # 3) Impossible values (DESIGN.md §3): a heart rate of 7 bpm is a typo.
    bad = (clean["HeartRate"] < 40) | (clean["SystolicBP"] < 60)
    log["implausible_rows_removed"] = int(bad.sum())
    log["implausible_rows"] = clean[bad].to_dict(orient="records")
    clean = clean[~bad].reset_index(drop=True)

    # Kept on purpose, but flagged: ages above 60 are unlikely pregnancies.
    log["rows_age_over_60_kept"] = int((clean["Age"] > 60).sum())

    log["clean_rows"] = len(clean)
    log["clean_class_counts"] = clean[LABEL].value_counts().to_dict()

    # After cleaning, every set of vitals appears exactly once.
    assert not clean.duplicated(subset=FEATURES).any()

    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN, index=False)
    LOG.write_text(json.dumps(log, indent=2))
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
