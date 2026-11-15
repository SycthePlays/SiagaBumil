"""Phase 3 - final evaluation. THE ONLY SCRIPT THAT READS THE TEST SET.

Run:  python pipeline/05_final_eval.py      (once)
Out:  results/test_metrics.json       B0, B1, M1, M2 on the held-out test set
      results/test_predictions.csv    one row per test mother (used by 06)
      results/confusion_*.png

Everything that could be tuned (features, thresholds) was fixed by
04_models.py using cross-validation and is only READ here. Nothing in this
file is adjusted after looking at the numbers. To protect that, the script
refuses to run a second time unless you pass --force (which only makes
sense for a clean rebuild, since the result is deterministic).
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (CLASSES, LABEL, ORDER, PROCESSED, RAW_FEATURES, RESULTS, add_features,
                    class_metrics, decide, make_lr, make_rf, rule_b1, triage_metrics)

OUT = RESULTS / "test_metrics.json"


def bootstrap_recall_ci(y, refer, n_boot=2000) -> list:
    """95% range for high-risk recall. We re-draw the test mothers at random
    (with repeats) 2000 times and see how much recall moves. The test set has
    only ~20 high-risk mothers, so this range is wide - and we report it."""
    rng = np.random.default_rng(42)
    values = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        high = y[i] == "high"
        if high.any():
            values.append(refer[i][high].mean())
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def plot_confusion(y, pred, columns, xlabel, title, path) -> None:
    """Grid of counts: rows = true risk, columns = what the approach said."""
    table = pd.crosstab(pd.Categorical(y, CLASSES), pd.Categorical(pred, columns), dropna=False)
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(table.values, cmap="Greens")
    ax.set_xticks(range(len(columns)), columns)
    ax.set_yticks(range(len(CLASSES)), CLASSES)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("True risk level")
    ax.set_title(title, fontsize=10)
    for r in range(table.shape[0]):
        for c in range(table.shape[1]):
            v = table.values[r, c]
            ax.text(c, r, v, ha="center", va="center", fontsize=13,
                    color="white" if v > table.values.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    if OUT.exists() and "--force" not in sys.argv:
        sys.exit("results/test_metrics.json already exists. The test set is used once. "
                 "Pass --force only for a clean rebuild.")

    cfg = json.loads((RESULTS / "cv_comparison.json").read_text())
    feats = cfg["features"]
    t_refer, t_recheck = cfg["thresholds"]["t_refer"], cfg["thresholds"]["t_recheck"]

    train = add_features(pd.read_csv(PROCESSED / "train.csv"))
    test = add_features(pd.read_csv(PROCESSED / "test.csv"))
    y_train, y = train[LABEL].to_numpy(), test[LABEL].to_numpy()

    # Fit on ALL training rows, predict the test rows.
    b0 = np.full(len(y), pd.Series(y_train).mode()[0])
    b1 = rule_b1(test)
    p1 = make_lr().fit(train[feats], y_train).predict_proba(test[feats])[:, ORDER]
    p2 = make_rf().fit(train[RAW_FEATURES], y_train).predict_proba(test[RAW_FEATURES])[:, ORDER]
    m1, m2 = np.array(CLASSES)[p1.argmax(axis=1)], np.array(CLASSES)[p2.argmax(axis=1)]
    action1 = decide(p1, t_refer, t_recheck)
    action2 = decide(p2, cfg["m2_t_refer"], t_recheck)

    rows = {
        "B0_majority": class_metrics(y, b0),
        "B1_clinical_rule": class_metrics(y, b1),
        "M1_logreg": class_metrics(y, m1),
        "M1_logreg_triage": triage_metrics(y, p1, t_refer, t_recheck),
        "M2_random_forest": class_metrics(y, m2),
        "M2_random_forest_triage": triage_metrics(y, p2, cfg["m2_t_refer"], t_recheck),
    }
    referred = {"B0_majority": b0 == "high", "B1_clinical_rule": b1 == "high",
                "M1_logreg": m1 == "high", "M1_logreg_triage": action1 == "refer",
                "M2_random_forest": m2 == "high", "M2_random_forest_triage": action2 == "refer"}
    for name, refer in referred.items():
        rows[name]["high_recall_ci95"] = bootstrap_recall_ci(y, refer)

    out = {"note": "Held-out test set, used once. Thresholds and features come from CV.",
           "n_test": int(len(y)), "features": feats,
           "thresholds": cfg["thresholds"], "m2_t_refer": cfg["m2_t_refer"], "rows": rows}
    OUT.write_text(json.dumps(out, indent=2))

    # One row per test mother, so 06_experiments.py never needs test.csv.
    pred = test[RAW_FEATURES + [LABEL]].copy()
    pred[["p_low", "p_mid", "p_high"]] = p1
    pred["m1_pred"], pred["action"] = m1, action1
    pred["b1_pred"], pred["m2_pred"], pred["m2_action"] = b1, m2, action2
    pred.to_csv(RESULTS / "test_predictions.csv", index=False)

    n = len(y)
    plot_confusion(y, b1, CLASSES, "Rule says", f"Clinical rule B1 (test, n={n})", RESULTS / "confusion_b1.png")
    plot_confusion(y, m1, CLASSES, "Model says", f"Logistic regression M1 (test, n={n})", RESULTS / "confusion_m1.png")
    plot_confusion(y, m2, CLASSES, "Model says", f"Random forest M2 (test, n={n})", RESULTS / "confusion_m2.png")
    plot_confusion(y, action1, ["routine", "recheck", "refer"], "Action shown to the bidan",
                   f"SigapBumil triage, M1 (test, n={n})", RESULTS / "confusion_m1_triage.png")

    for name, m in rows.items():
        lo, hi = m["high_recall_ci95"]
        extra = (f"macroF1={m['macro_f1']:.3f} acc={m['accuracy']:.3f}" if "macro_f1" in m
                 else f"actions={m['actions']} high->routine={m['high_sent_to_routine']}")
        print(f"{name:26s} recall={m['high_recall']:.3f} [{lo:.2f}-{hi:.2f}] "
              f"FN={m['high_fn']:2d} FP={m['high_fp']:2d} {extra}")


if __name__ == "__main__":
    main()
