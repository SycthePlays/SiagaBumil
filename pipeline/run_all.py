"""Run the whole pipeline in order, from raw data to results.

Run:  python pipeline/run_all.py

Every step is deterministic (random_state=42), so a rebuild gives the same
numbers. 05 gets --force because a clean rebuild is the one valid reason
to re-run the final evaluation.
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ["01_load_clean.py"],
    ["02_split.py"],
    ["03_baselines.py"],
    ["04_models.py"],
    ["05_final_eval.py", "--force"],
    ["06_experiments.py"],
    ["07_export.py"],
]

for script, *args in STEPS:
    print(f"\n=== {script} ===", flush=True)
    subprocess.run([sys.executable, str(HERE / script), *args], check=True)

# Last step: check the browser code gives the same answers as Python.
print("\n=== tests/test_parity.mjs ===", flush=True)
if shutil.which("node"):
    subprocess.run(["node", str(HERE.parent / "tests" / "test_parity.mjs")], check=True)
else:
    print("node not found - skipped. Install Node.js and run: node tests/test_parity.mjs")
