"""Phase 3 - our own questions, plus the summary file the README reads.

Run:  python pipeline/06_experiments.py   (after 05_final_eval.py)
Out:  results/experiments.json   E1 duplicate leakage, E2 age groups, E4 failure cases
      results/leakage.png
      results/summary.json       every number the README / website shows

This script never opens test.csv. It reads the predictions that
05_final_eval.py saved, so the test set is still used only once.
(E3, the external dataset, was cut for time.)
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict, train_test_split

from common import (LABEL, PROCESSED, RAW_FEATURES, RESULTS, ROOT, add_features,
                    class_metrics, make_cv, make_lr, make_rf, refer_metrics, rule_b1)


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text())


# ---------------------------------------------------------------- E1 --------
def e1_duplicate_leakage(cv: dict, test: dict) -> dict:
    """What score would we have reported if we had NOT removed duplicates?
    Same models, same 80/20 recipe, but on the raw 1,014-row file."""
    raw = pd.read_csv(ROOT / "data" / "raw" / "maternal_health_risk.csv")
    raw[LABEL] = raw[LABEL].str.replace(" risk", "", regex=False)
    raw = add_features(raw)
    tr, te = train_test_split(raw, test_size=0.20, stratify=raw[LABEL], random_state=42)

    # How many "test" mothers have vitals the model already saw in training?
    seen = te.merge(tr[RAW_FEATURES].drop_duplicates(), on=RAW_FEATURES, how="inner")
    out = {"raw_rows": len(raw), "raw_test_rows": len(te),
           "raw_test_rows_also_in_train": len(seen),
           "raw_test_share_also_in_train": len(seen) / len(te), "models": {}}

    for key, make, cols in [("M1_logreg", make_lr, cv["features"]),
                            ("M2_random_forest", make_rf, RAW_FEATURES)]:
        holdout = class_metrics(te[LABEL], make().fit(tr[cols], tr[LABEL]).predict(te[cols]))
        raw_cv = class_metrics(raw[LABEL], cross_val_predict(make(), raw[cols], raw[LABEL], cv=make_cv()))
        pick = lambda m: {k: m[k] for k in ("accuracy", "macro_f1", "high_recall")}
        out["models"][key] = {
            "with_duplicates_holdout": pick(holdout),
            "after_cleaning_holdout": pick(test["rows"][key]),
            "with_duplicates_cv": pick(raw_cv),
            "after_cleaning_cv": pick(cv["rows"][key]),
        }

    fig, ax = plt.subplots(figsize=(6, 4))
    names = {"M1_logreg": "Logistic regression", "M2_random_forest": "Random forest"}
    x = np.arange(len(names))
    before = [out["models"][k]["with_duplicates_holdout"]["accuracy"] for k in names]
    after = [out["models"][k]["after_cleaning_holdout"]["accuracy"] for k in names]
    for xs, vals, label, colour in [(x - 0.2, before, "Raw file (duplicates on both sides)", "#B45309"),
                                    (x + 0.2, after, "After cleaning (our test set)", "#0F766E")]:
        bars = ax.bar(xs, vals, 0.4, label=label, color=colour)
        ax.bar_label(bars, fmt="%.2f")
    ax.set_xticks(x, names.values())
    ax.set_ylim(0, 1.15)  # head-room so the legend does not cover the bars
    ax.set_ylabel("Test accuracy")
    # Neutral title on purpose: only the model that can memorise rows is inflated.
    ax.set_title("Same recipe, raw file vs cleaned data")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(RESULTS / "leakage.png", dpi=150)
    return out


# ---------------------------------------------------------------- E2 --------
def age_group_table(pred: pd.DataFrame) -> dict:
    """High-risk recall per age group ("4 Terlalu": too young <20, too old >35)."""
    group = pd.cut(pred["Age"], [0, 19, 35, 200], labels=["<20", "20-35", ">35"])
    return {str(g): refer_metrics(part[LABEL], part["action"] == "refer")
            for g, part in pred.groupby(group, observed=False)}


# ---------------------------------------------------------------- E4 --------
def e4_failure_cases(test_pred: pd.DataFrame, oof: pd.DataFrame, feats: list) -> list:
    """The mistakes that matter most: high-risk mothers who were NOT referred.
    For each one we show which vitals pulled the 'high' score down.
    If the test set has few misses, we also show misses from cross-validation
    (training rows predicted by a model that never saw them)."""
    train = add_features(pd.read_csv(PROCESSED / "train.csv"))
    lr = make_lr().fit(train[feats], train[LABEL])
    coef_high = lr[-1].coef_[list(lr[-1].classes_).index("high")]

    def missed(df):
        return df[(df[LABEL] == "high") & (df["action"] != "refer")].sort_values("p_high").head(5)

    alarms = test_pred[(test_pred[LABEL] != "high") & (test_pred["action"] == "refer")]
    alarms = alarms.sort_values("p_high", ascending=False).head(3)

    cases = []
    for kind, rows in [("test_missed_high_risk", missed(test_pred)),
                       ("cv_missed_high_risk", missed(oof)),
                       ("test_false_alarm", alarms)]:
        for _, r in rows.iterrows():
            x = add_features(pd.DataFrame([r[RAW_FEATURES]]).astype(float))[feats]
            contrib = coef_high * lr[0].transform(x)[0]  # weight x standardized value
            order = np.argsort(contrib)
            cases.append({
                "kind": kind,
                "vitals": {f: float(r[f]) for f in RAW_FEATURES},
                "true": r[LABEL], "action": r["action"],
                "rule_b1_said": str(rule_b1(pd.DataFrame([r[RAW_FEATURES]]).astype(float))[0]),
                "p_low": round(r["p_low"], 3), "p_mid": round(r["p_mid"], 3), "p_high": round(r["p_high"], 3),
                "pulled_score_down": [{feats[i]: round(float(contrib[i]), 2)} for i in order[:2]],
                "pushed_score_up": [{feats[i]: round(float(contrib[i]), 2)} for i in order[::-1][:2]],
            })
    return cases


def main() -> None:
    cv, test, cleaning = load("cv_comparison.json"), load("test_metrics.json"), load("cleaning_log.json")
    test_pred = pd.read_csv(RESULTS / "test_predictions.csv")
    oof = pd.read_csv(RESULTS / "cv_oof_predictions.csv")

    experiments = {
        "E1_duplicate_leakage": e1_duplicate_leakage(cv, test),
        "E2_age_groups": {"test": age_group_table(test_pred), "cv": age_group_table(oof),
                          "note": "Small groups: read the counts, not just the recall."},
        "E3_external_dataset": "skipped for time",
        "E4_failure_cases": e4_failure_cases(test_pred, oof, cv["features"]),
    }
    (RESULTS / "experiments.json").write_text(json.dumps(experiments, indent=2))

    # One file with everything the README and website need. CV sits next to
    # test for every approach, because the test set is small.
    summary = {
        "data": cleaning,
        "features": cv["features"],
        "engineered_features_kept": cv["engineered_features_kept"],
        "feature_check": cv["feature_check"],
        "thresholds": cv["thresholds"],
        "deploy": cv["deploy"], "m2_beats_rule_in_cv": cv["m2_beats_rule"],
        "n_train": cv["rows"]["M1_logreg"]["n"], "n_test": test["n_test"],
        "results": {name: {"cv": cv["rows"][name], "test": test["rows"][name]} for name in test["rows"]},
        "experiments": experiments,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2))

    e1 = experiments["E1_duplicate_leakage"]
    print(f"E1: {e1['raw_test_rows_also_in_train']}/{e1['raw_test_rows']} raw test rows "
          f"({e1['raw_test_share_also_in_train']:.0%}) also appear in raw train")
    for k, m in e1["models"].items():
        print(f"  {k:18s} accuracy holdout: raw {m['with_duplicates_holdout']['accuracy']:.3f} -> "
              f"clean {m['after_cleaning_holdout']['accuracy']:.3f} | CV: raw "
              f"{m['with_duplicates_cv']['accuracy']:.3f} -> clean {m['after_cleaning_cv']['accuracy']:.3f}")
    for split in ("test", "cv"):
        for g, m in experiments["E2_age_groups"][split].items():
            rec = "n/a" if m["high_recall"] is None else f"{m['high_recall']:.2f}"
            print(f"E2 {split:4s} age {g:5s} n={m['n']:3d} high={m['n_high']:2d} recall={rec} FN={m['high_fn']} FP={m['high_fp']}")
    for c in experiments["E4_failure_cases"]:
        print("E4", c["kind"], list(c["vitals"].values()), "true:", c["true"], "action:", c["action"],
              "rule:", c["rule_b1_said"], "p_high:", c["p_high"], "down:", c["pulled_score_down"])


if __name__ == "__main__":
    main()
