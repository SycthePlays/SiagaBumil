"""Phase 1 — split the cleaned data into train (80%) and test (20%).

Run:  python pipeline/02_split.py
Out:  data/processed/train.csv, data/processed/test.csv

"Stratified" = both files keep the same low/mid/high proportions.
The test file is LOCKED: only pipeline/05_final_eval.py may read it, once.
All model choices and threshold tuning use cross-validation on train.csv.
"""
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
LOG = ROOT / "results" / "cleaning_log.json"


def main() -> None:
    clean = pd.read_csv(PROCESSED / "clean.csv")
    train, test = train_test_split(
        clean, test_size=0.20, stratify=clean["RiskLevel"], random_state=42
    )
    train.to_csv(PROCESSED / "train.csv", index=False)
    test.to_csv(PROCESSED / "test.csv", index=False)

    # Add the split sizes to the same log file that 01_load_clean.py wrote.
    log = json.loads(LOG.read_text())
    log["train_rows"] = len(train)
    log["test_rows"] = len(test)
    log["train_class_counts"] = train["RiskLevel"].value_counts().to_dict()
    log["test_class_counts"] = test["RiskLevel"].value_counts().to_dict()
    LOG.write_text(json.dumps(log, indent=2))
    print({k: log[k] for k in ("train_rows", "test_rows", "train_class_counts", "test_class_counts")})


if __name__ == "__main__":
    main()
