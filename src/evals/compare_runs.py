"""Compare saved answer runs: per-run scores, their spread, and questions that changed."""
import glob
import json
import sys
from pathlib import Path
from statistics import mean


def load_run(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return {row["id"]: row for row in rows}


def main(patterns):
    paths = [path for pattern in patterns for path in sorted(
        glob.glob(pattern))]
    runs = [load_run(path) for path in paths]
    print(f"{len(runs)} runs: " + ", ".join(Path(p).name for p in paths) + "\n")

    for label, key in (("fact recall", "fact_recall"), ("citation recall", "citation_recall")):
        per_run = [mean(r[key] for r in run.values() if r[key]
                        is not None) for run in runs]
        print(f"{label}: " + ", ".join(f"{v:.2f}" for v in per_run)
              + f"   mean {mean(per_run):.2f}, range {min(per_run):.2f} to {max(per_run):.2f}")

    costs = [sum(r["cost"] for r in run.values()) for run in runs]
    print(f"answer cost per run: " + ", ".join(f"${c:.2f}" for c in costs))

    print("\nquestions whose fact recall changed between runs:")
    for question_id in sorted(runs[0]):
        values = [run[question_id]["fact_recall"]
                  for run in runs if question_id in run]
        if len(set(values)) > 1:
            print(f"  {question_id}: " + ", ".join(f"{v:.2f}" for v in values))


if __name__ == "__main__":
    main(sys.argv[1:])
