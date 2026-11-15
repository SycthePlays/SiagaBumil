"""Phase 4 - export the trained model so the website can run it.

Run:  python pipeline/07_export.py   (after 06_experiments.py)
Out:  web/model.json        the whole model as plain numbers (source of truth)
      web/results.json      copy of results/summary.json for the "How it works" section
      web/test_cases.json   30 inputs + the answers Python gives (for the JS parity test)
      web/img/*.png         key plots
      models/sigapbumil_lr.joblib   scikit-learn copy of the same model

Nothing is tuned here. Features and thresholds are READ from
results/cv_comparison.json; the model is the same logistic regression,
fitted on the same training rows with the same settings as in 05.
"""
import json
import shutil

import joblib
import numpy as np
import pandas as pd

from common import (B1_HIGH_CUTOFFS, CLASSES, LABEL, ORDER, PROCESSED, RAW_FEATURES, RESULTS,
                    ROOT, add_features, decide, make_lr)
from units import c_to_f, mgdl_to_mmol

WEB = ROOT / "web"
MODELS = ROOT / "models"

# Names shown in the "Why?" list on the result card.
FEATURE_LABELS = {
    "Age": {"id": "Usia", "en": "Age"},
    "SystolicBP": {"id": "Tekanan darah sistolik", "en": "Systolic blood pressure"},
    "DiastolicBP": {"id": "Tekanan darah diastolik", "en": "Diastolic blood pressure"},
    "BS": {"id": "Gula darah", "en": "Blood sugar"},
    "BodyTemp": {"id": "Suhu tubuh", "en": "Body temperature"},
    "HeartRate": {"id": "Nadi", "en": "Pulse"},
}

# What the bidan types, in Indonesian units.
INPUT_KEYS = ["age", "sbp", "dbp", "sugar_mgdl", "temp_c", "pulse"]

# Synthetic demo mothers for the example chips (made up by us, not real patients).
DEMOS = {
    "routine": (25, 110, 70, 110, 36.7, 72),
    # Every number is below the single-number danger cutoffs, but together they are risky.
    "borderline": (37, 135, 88, 150, 36.8, 92),
    "high": (38, 150, 95, 250, 37.0, 88),
}
# Extra fixed cases: two that sit exactly on / just under every danger-sign
# cutoff (140/90 mmHg, 200 mg/dL, 38.0 C), then healthy-looking mothers so
# the "recheck" and "routine" answers are tested too (random inputs mostly
# land on "refer").
FIXED = [(30, 140, 90, 200, 38.0, 80), (30, 139, 89, 199, 37.9, 80),
         (28, 120, 80, 125, 36.9, 78), (26, 118, 78, 120, 36.8, 76), (31, 115, 75, 122, 36.7, 80),
         (22, 100, 65, 112, 36.7, 70), (24, 115, 75, 115, 36.7, 74), (29, 105, 68, 108, 36.7, 68),
         (33, 112, 72, 110, 36.7, 66)]


def to_model_units(inp: dict) -> dict:
    """Form units -> dataset units (mmol/L, Fahrenheit). Same as web/inference.js."""
    return {"Age": inp["age"], "SystolicBP": inp["sbp"], "DiastolicBP": inp["dbp"],
            "BS": mgdl_to_mmol(inp["sugar_mgdl"]), "BodyTemp": c_to_f(inp["temp_c"]),
            "HeartRate": inp["pulse"]}


def random_inputs(n: int) -> list:
    """Made-up inputs spread over the ranges the web form accepts."""
    rng = np.random.default_rng(42)
    out = []
    for _ in range(n):
        sbp = int(rng.integers(85, 166))
        dbp = int(rng.integers(50, min(sbp - 10, 105) + 1))  # diastolic is always below systolic
        out.append((int(rng.integers(15, 46)), sbp, dbp, int(rng.integers(80, 321)),
                    round(float(rng.uniform(35.5, 39.5)), 1), int(rng.integers(55, 121))))
    return out


def main() -> None:
    cfg = json.loads((RESULTS / "cv_comparison.json").read_text())
    summary = json.loads((RESULTS / "summary.json").read_text())
    feats, th = cfg["features"], cfg["thresholds"]

    train = add_features(pd.read_csv(PROCESSED / "train.csv"))
    lr = make_lr().fit(train[feats], train[LABEL])
    scaler, clf = lr[0], lr[-1]
    # scikit-learn stores classes alphabetically; ORDER re-arranges rows to low, mid, high.
    coef, intercept = clf.coef_[ORDER], clf.intercept_[ORDER]

    cv_row = summary["results"]["M1_logreg_triage"]["cv"]
    test_row = summary["results"]["M1_logreg_triage"]["test"]
    demo_inputs = {name: dict(zip(INPUT_KEYS, values)) for name, values in DEMOS.items()}

    # ---- every case: what does Python answer? -----------------------------
    inputs = list(demo_inputs.values()) + [dict(zip(INPUT_KEYS, v)) for v in FIXED + random_inputs(18)]
    X = add_features(pd.DataFrame([to_model_units(i) for i in inputs]))
    proba = lr.predict_proba(X[feats])[:, ORDER]
    actions = decide(proba, th["t_refer"], th["t_recheck"])
    contrib = coef[CLASSES.index("high")] * scaler.transform(X[feats])  # weight x standardized value
    cases = []
    for i, inp in enumerate(inputs):
        top = [k for k in np.argsort(-contrib[i])[:3] if contrib[i][k] > 0]
        cases.append({
            "demo": list(DEMOS)[i] if i < len(DEMOS) else None,
            "input": inp,
            "proba": proba[i].tolist(),                    # low, mid, high
            "action": str(actions[i]),
            "reasons": [feats[k] for k in top],            # top 3 vitals that raised the risk
            "danger_signs": [f for f, cut in B1_HIGH_CUTOFFS.items() if X[f][i] >= cut],
        })

    model = {
        "version": "1.0",
        "trained_on": "UCI Maternal Health Risk (cleaned), train split, n=%d" % len(train),
        "features": feats,
        "units": {"BS": "mmol/L", "BodyTemp": "F"},
        "scaler": {"mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist()},
        "classes": CLASSES,
        "coef": coef.tolist(),
        "intercept": intercept.tolist(),
        "thresholds": {"t_refer": th["t_refer"], "t_recheck": th["t_recheck"]},
        "feature_labels": {f: FEATURE_LABELS[f] for f in feats},
        # Single-vital warning, independent of the model (same cutoffs as baseline B1, dataset units).
        "danger_cutoffs": B1_HIGH_CUTOFFS,
        "examples": [{"id": c["demo"], "input": c["input"], "expected_action": c["action"]}
                     for c in cases if c["demo"]],
        "metrics": {
            "test_n_high": test_row["n_high"], "test_high_recall": test_row["high_recall"],
            "test_high_fn": test_row["high_fn"], "test_high_fp": test_row["high_fp"],
            "test_high_recall_wilson95": test_row["high_recall_wilson95"],
            "cv_n_high": cv_row["n_high"], "cv_high_recall": cv_row["high_recall"],
            "cv_high_fn": cv_row["high_fn"], "cv_high_fp": cv_row["high_fp"],
            "cv_high_recall_wilson95": cv_row["high_recall_wilson95"],
        },
    }

    (WEB / "img").mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(exist_ok=True)
    (WEB / "model.json").write_text(json.dumps(model, indent=2))
    (WEB / "test_cases.json").write_text(json.dumps(cases, indent=1))
    shutil.copy(RESULTS / "summary.json", WEB / "results.json")
    for plot in ("threshold_curve.png", "confusion_m1_triage.png", "leakage.png", "coefficients.png"):
        shutil.copy(RESULTS / plot, WEB / "img" / plot)
    joblib.dump(lr, MODELS / "sigapbumil_lr.joblib")

    print("features:", feats, "| t_refer:", th["t_refer"], "| t_recheck:", th["t_recheck"])
    print("cases written:", len(cases), "| actions:", pd.Series(actions).value_counts().to_dict())
    for c in cases[: len(DEMOS)]:
        p = c["proba"]
        print(f"demo {c['demo']:10s} {list(c['input'].values())} -> low {p[0]:.3f} mid {p[1]:.3f} "
              f"high {p[2]:.3f} -> {c['action']} | reasons {c['reasons']} | danger {c['danger_signs']}")


if __name__ == "__main__":
    main()
