"""Shared pieces used by scripts 03-06, kept in one place so every script
measures things the same way (same features, same models, same metrics)."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

RAW_FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
ENGINEERED = ["PulsePressure", "MAP"]
LABEL = "RiskLevel"
CLASSES = ["low", "mid", "high"]  # the order we report in, everywhere

# scikit-learn sorts class names alphabetically (high, low, mid).
# ORDER re-arranges its probability columns into our low, mid, high order.
ORDER = [sorted(CLASSES).index(c) for c in CLASSES]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Two blood-pressure summaries doctors use. Both are simple formulas
    of systolic and diastolic BP, so the web app can compute them too."""
    df = df.copy()
    df["PulsePressure"] = df["SystolicBP"] - df["DiastolicBP"]
    df["MAP"] = df["DiastolicBP"] + df["PulsePressure"] / 3
    return df


def make_cv() -> StratifiedKFold:
    """5 folds, same shuffle every run, each fold keeps the class mix."""
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def make_lr():
    """M1: scale each feature, then logistic regression.
    class_weight='balanced' stops the model from ignoring the smaller classes."""
    return make_pipeline(
        StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000)
    )


def make_rf():
    """M2: random forest with default settings (no grid search - cut for time)."""
    return RandomForestClassifier(class_weight="balanced", random_state=42)


def rule_b1(df: pd.DataFrame) -> np.ndarray:
    """B1: fixed single-number cutoffs, no learning (DESIGN.md section 4).
    Simplified general thresholds, NOT an official clinical guideline."""
    high = (
        (df["SystolicBP"] >= 140)
        | (df["DiastolicBP"] >= 90)
        | (df["BS"] >= 11.1)
        | (df["BodyTemp"] >= 100.4)
    )
    mid = (
        (df["SystolicBP"] >= 130)
        | (df["DiastolicBP"] >= 80)
        | (df["BS"] >= 7.8)
        | (df["HeartRate"] > 100)
    )
    return np.select([high, mid], ["high", "mid"], default="low")


def decide(proba: np.ndarray, t_refer: float, t_recheck: float) -> np.ndarray:
    """Turn probabilities (columns low, mid, high) into the bidan's action.
    Same logic as web/app.js (DESIGN.md section 6)."""
    refer = proba[:, 2] >= t_refer
    recheck = (proba.argmax(axis=1) == 1) | (proba[:, 1] + proba[:, 2] >= t_recheck)
    return np.where(refer, "refer", np.where(recheck, "recheck", "routine"))


def wilson_ci(caught: int, total: int, z: float = 1.96):
    """95% range for a proportion (Wilson score interval). Unlike a bootstrap,
    it stays honest when every case was caught: 20 out of 20 does NOT prove
    100% recall, it gives roughly 84%-100%."""
    if total == 0:
        return None
    p = caught / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return [float(max(0.0, centre - half)), float(min(1.0, centre + half))]


def refer_metrics(y, refer) -> dict:
    """The numbers the Health track asks for, for the high-risk class:
    recall, missed cases (FN) and false alarms (FP), reported separately."""
    y = np.asarray(y)
    refer = np.asarray(refer, dtype=bool)
    is_high = y == "high"
    return {
        "n": int(len(y)),
        "n_high": int(is_high.sum()),
        "high_recall": float(refer[is_high].mean()) if is_high.any() else None,
        "high_recall_wilson95": wilson_ci(int((is_high & refer).sum()), int(is_high.sum())),
        "high_fn": int((is_high & ~refer).sum()),
        "high_fp": int((~is_high & refer).sum()),
    }


def class_metrics(y, pred) -> dict:
    """Metrics when the model simply answers low / mid / high."""
    y, pred = np.asarray(y), np.asarray(pred)
    kw = dict(labels=CLASSES, average=None, zero_division=0)
    out = refer_metrics(y, pred == "high")
    out.update(
        accuracy=float(accuracy_score(y, pred)),
        macro_f1=float(f1_score(y, pred, labels=CLASSES, average="macro", zero_division=0)),
        recall=dict(zip(CLASSES, map(float, recall_score(y, pred, **kw)))),
        precision=dict(zip(CLASSES, map(float, precision_score(y, pred, **kw)))),
    )
    return out


def triage_metrics(y, proba: np.ndarray, t_refer: float, t_recheck: float) -> dict:
    """Metrics for the 3-action decision. 'Refer' counts as catching a
    high-risk mother. A high-risk mother sent to 'routine' is the worst miss."""
    y = np.asarray(y)
    action = decide(proba, t_refer, t_recheck)
    out = refer_metrics(y, action == "refer")
    out["t_refer"] = t_refer
    out["high_sent_to_recheck"] = int(((y == "high") & (action == "recheck")).sum())
    out["high_sent_to_routine"] = int(((y == "high") & (action == "routine")).sum())
    out["actions"] = {a: int((action == a).sum()) for a in ("refer", "recheck", "routine")}
    return out
