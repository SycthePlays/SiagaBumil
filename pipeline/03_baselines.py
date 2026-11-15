"""Phase 2 - baselines, measured on the TRAINING set only (5-fold CV).

Run:  python pipeline/03_baselines.py
Out:  results/cv_baselines.json

A model is only interesting if it beats something simple:
  B0  always answer the most common class ("low")  -> catches no high-risk mother
  B1  fixed clinical cutoffs, no learning          -> what a careful bidan could do
"""
import json

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import cross_val_predict

from common import LABEL, PROCESSED, RAW_FEATURES, RESULTS, class_metrics, make_cv, rule_b1


def main() -> None:
    train = pd.read_csv(PROCESSED / "train.csv")
    y = train[LABEL]

    # B0 learns "the most common class" inside each fold, like a real model would.
    b0 = cross_val_predict(
        DummyClassifier(strategy="most_frequent"), train[RAW_FEATURES], y, cv=make_cv()
    )
    # B1 learns nothing, so it is simply applied to every training row.
    b1 = rule_b1(train)

    out = {"B0_majority": class_metrics(y, b0), "B1_clinical_rule": class_metrics(y, b1)}
    (RESULTS / "cv_baselines.json").write_text(json.dumps(out, indent=2))
    for name, m in out.items():
        print(f"{name:18s} recall={m['high_recall']:.3f} FN={m['high_fn']} FP={m['high_fp']} "
              f"macroF1={m['macro_f1']:.3f} acc={m['accuracy']:.3f}")


if __name__ == "__main__":
    main()
