"""Fail (exit code 1) if retrieval scores fall below the saved baseline."""
import json
import sys
from pathlib import Path

from src.evals.run_retrieval import main as run_retrieval

BASELINE = Path("src/evals/baseline.json")
TOLERANCE = 0.01  # the baseline is rounded to 2 decimals


def main():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    failures = []
    for retriever, expected in baseline.items():
        scores = run_retrieval(retriever)
        print()
        for metric, floor in expected.items():
            score = scores[metric]
            ok = score >= floor - TOLERANCE
            print(
                f"{retriever} {metric}: {score:.2f} (baseline {floor:.2f}) {'ok' if ok else 'FAILED'}")
            if not ok:
                failures.append(f"{retriever} {metric}")
    if failures:
        print("\nRegression in: " + ", ".join(failures))
        sys.exit(1)
    print("\nNo regressions.")


if __name__ == "__main__":
    main()
