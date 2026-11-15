"""Phase 2 - train and compare models using 5-fold CV on the TRAINING set.

Run:  python pipeline/04_models.py   (after 03_baselines.py)
Out:  results/cv_comparison.json       table: B0, B1, M1, M2
      results/cv_oof_predictions.csv   M1 out-of-fold predictions per train row
      results/threshold_curve.png      recall vs false alarms
      results/coefficients.png         what the logistic regression learned

"Out-of-fold" = each row is predicted by a model that never saw that row.
That lets us choose features and the referral threshold honestly,
without ever opening the test set.
"""
import json
import math

import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict

from common import (CLASSES, ENGINEERED, LABEL, ORDER, PROCESSED, RAW_FEATURES, RESULTS,
                    add_features, class_metrics, decide, make_cv, make_lr, make_rf,
                    refer_metrics, triage_metrics)

TARGET_RECALL = 0.90  # catch at least 9 of 10 high-risk mothers
T_RECHECK = 0.5       # DESIGN.md section 6 default


def oof_proba(model, X, y) -> np.ndarray:
    """Out-of-fold probabilities, columns in low, mid, high order."""
    return cross_val_predict(model, X, y, cv=make_cv(), method="predict_proba")[:, ORDER]


def tune_t_refer(y, p_high) -> float:
    """Highest threshold that still refers >= 90% of high-risk mothers.
    Higher threshold = fewer false alarms, so we want the highest that works.
    Rounded DOWN to 4 decimals so rounding can never lose a caught case."""
    for t in np.sort(np.unique(p_high))[::-1]:
        if np.mean(p_high[y == "high"] >= t) >= TARGET_RECALL:
            return math.floor(t * 1e4) / 1e4
    return 0.0


def curve(y, p_high):
    """Recall and number of false alarms at every threshold from 0 to 1."""
    ts = np.linspace(0, 1, 101)
    m = [refer_metrics(y, p_high >= t) for t in ts]
    return [r["high_fp"] for r in m], [r["high_recall"] for r in m]


def main() -> None:
    train = add_features(pd.read_csv(PROCESSED / "train.csv"))
    y = train[LABEL].to_numpy()

    # --- M1: do the two engineered features help? -------------------------
    # Judge at the operating point that matters: false alarms when recall >= 0.90.
    options = {}
    for name, cols in {"raw6": RAW_FEATURES, "raw6+PP+MAP": RAW_FEATURES + ENGINEERED}.items():
        p = oof_proba(make_lr(), train[cols], y)
        t = tune_t_refer(y, p[:, 2])
        options[name] = {"cols": cols, "p": p, "t": t,
                         "argmax": class_metrics(y, np.array(CLASSES)[p.argmax(axis=1)]),
                         "triage": triage_metrics(y, p, t, T_RECHECK)}
    # Keep the extra features only if they give strictly fewer false alarms.
    keep = options["raw6+PP+MAP"]["triage"]["high_fp"] < options["raw6"]["triage"]["high_fp"]
    m1 = options["raw6+PP+MAP" if keep else "raw6"]

    # --- M2: random forest, default settings, for comparison --------------
    p2 = oof_proba(make_rf(), train[RAW_FEATURES], y)
    t2 = tune_t_refer(y, p2[:, 2])
    m2 = {"argmax": class_metrics(y, np.array(CLASSES)[p2.argmax(axis=1)]),
          "triage": triage_metrics(y, p2, t2, T_RECHECK)}

    # DESIGN.md section 5: deploy M1 unless M2 catches > 5 points more
    # high-risk mothers with a similar number of false alarms.
    gain = m2["argmax"]["high_recall"] - m1["argmax"]["high_recall"]
    m2_beats_rule = bool(gain > 0.05 and m2["argmax"]["high_fp"] <= m1["argmax"]["high_fp"] + 3)

    out = {
        "note": "5-fold stratified CV on the training set (n=%d). Test set not used." % len(y),
        "features": m1["cols"],
        "feature_check": {k: {"t_refer": v["t"], "fp_at_target_recall": v["triage"]["high_fp"],
                              "macro_f1": v["argmax"]["macro_f1"]} for k, v in options.items()},
        "engineered_features_kept": bool(keep),
        "thresholds": {"t_refer": m1["t"], "t_recheck": T_RECHECK, "target_recall": TARGET_RECALL},
        "m2_t_refer": t2,
        "deploy": "M1",
        "m2_beats_rule": m2_beats_rule,
        "deploy_reason": "Decided on CV only, before the test set was opened. M1 is deployed "
                         "because it is explainable and ports exactly to the browser. If "
                         "m2_beats_rule is true, the random forest was the stronger model in "
                         "CV and we say so in the write-up.",
        "rows": {
            **json.loads((RESULTS / "cv_baselines.json").read_text()),
            "M1_logreg": m1["argmax"],
            "M1_logreg_triage": m1["triage"],
            "M2_random_forest": m2["argmax"],
            "M2_random_forest_triage": m2["triage"],
        },
    }
    (RESULTS / "cv_comparison.json").write_text(json.dumps(out, indent=2))

    # Out-of-fold predictions of the chosen M1 (used later for age-group checks).
    oof = train[RAW_FEATURES + [LABEL]].copy()
    oof[["p_low", "p_mid", "p_high"]] = m1["p"]
    oof["action"] = decide(m1["p"], m1["t"], T_RECHECK)
    oof.to_csv(RESULTS / "cv_oof_predictions.csv", index=False)

    # --- plot: recall vs false alarms -------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for label, p, row, colour in [("Logistic regression (M1)", m1["p"], m1["triage"], "#0F766E"),
                                  ("Random forest (M2)", p2, m2["triage"], "#B45309")]:
        fp, rec = curve(y, p[:, 2])
        ax.plot(fp, rec, color=colour, label=label)
        ax.scatter([row["high_fp"]], [row["high_recall"]], color=colour, zorder=3)
    b1 = out["rows"]["B1_clinical_rule"]
    ax.scatter([b1["high_fp"]], [b1["high_recall"]], color="#1C1917", marker="x", s=70,
               label="Clinical rule (B1)", zorder=3)
    ax.axhline(TARGET_RECALL, color="#B91C1C", linestyle="--", linewidth=1, label="Target recall 0.90")
    ax.set_xlabel("False alarms (not high-risk, but referred)")
    ax.set_ylabel("High-risk recall (share of high-risk mothers referred)")
    ax.set_title("Cross-validation on training set (n=%d, %d high-risk)" % (len(y), (y == "high").sum()))
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(RESULTS / "threshold_curve.png", dpi=150)

    # --- plot: what pushes a prediction towards "high" ---------------------
    lr = make_lr().fit(train[m1["cols"]], y)
    coef_high = lr[-1].coef_[list(lr[-1].classes_).index("high")]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.barh(m1["cols"][::-1], coef_high[::-1], color="#0F766E")
    ax.axvline(0, color="#1C1917", linewidth=1)
    ax.set_xlabel('Weight towards "high risk" (per 1 standard deviation)')
    ax.set_title("Logistic regression: what raises the risk")
    fig.tight_layout()
    fig.savefig(RESULTS / "coefficients.png", dpi=150)

    # --- print the table ---------------------------------------------------
    print("features kept:", out["features"], "| t_refer =", m1["t"], "| M2 t_refer =", t2)
    print(json.dumps(out["feature_check"], indent=1))
    for name, m in out["rows"].items():
        extra = (f"macroF1={m['macro_f1']:.3f} acc={m['accuracy']:.3f}" if "macro_f1" in m
                 else f"actions={m['actions']} high->routine={m['high_sent_to_routine']}")
        print(f"{name:26s} recall={m['high_recall']:.3f} FN={m['high_fn']:3d} FP={m['high_fp']:3d} {extra}")
    print("M2 beats the deploy rule:", m2_beats_rule)


if __name__ == "__main__":
    main()
