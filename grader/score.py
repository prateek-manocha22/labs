"""
Hackathon Auto-Grader
Reads pytest JSON report, computes score per lab, and writes
a Markdown summary to $GITHUB_STEP_SUMMARY.
"""
import json
import os
from pathlib import Path

LABS = [
    ("lab-01-api-fetcher", "Lab 01: API Fetcher"),
    ("lab-02-llm-json",    "Lab 02: LLM JSON Output"),
    ("lab-03-toon-convert","Lab 03: TOON Converter"),
    ("lab-04-vehicle-detect","Lab 04: Vehicle Detection"),
    ("lab-05-rag-qa",      "Lab 05: RAG Q&A"),
]
POINTS_PER_LAB = 20

def load_results(path: str = "test_results.json") -> dict:
    if not Path(path).exists():
        return {}
    with open(path) as f:
        return json.load(f)

def score_labs(data: dict) -> list[dict]:
    tests = data.get("tests", [])
    results = []
    for lab_dir, lab_name in LABS:
        lab_tests = [t for t in tests if lab_dir in t.get("nodeid", "")]
        total = len(lab_tests)
        passed = sum(1 for t in lab_tests if t.get("outcome") == "passed")
        points = round((passed / total) * POINTS_PER_LAB) if total else 0
        results.append({
            "name": lab_name,
            "passed": passed,
            "total": total,
            "points": points,
            "max": POINTS_PER_LAB,
        })
    return results

def build_summary(results: list[dict]) -> str:
    total_points = sum(r["points"] for r in results)
    max_points = len(LABS) * POINTS_PER_LAB
    pct = round((total_points / max_points) * 100) if max_points else 0

    lines = [
        "# 🎓 Hackathon Lab Score Report",
        "",
        f"## 🏆 Total Score: `{total_points} / {max_points}` ({pct}%)",
        "",
        "| Lab | Tests Passed | Points |",
        "|-----|-------------|--------|",
    ]
    for r in results:
        status = "✅" if r["passed"] == r["total"] and r["total"] > 0 else ("⚠️" if r["passed"] > 0 else "❌")
        lines.append(f"| {status} {r['name']} | {r['passed']}/{r['total']} | {r['points']}/{r['max']} |")

    lines += [
        "",
        "---",
        "> **Tip:** Push again after fixing failing tests — the score will update automatically.",
    ]
    return "\n".join(lines)

def main():
    data = load_results()
    results = score_labs(data)
    summary = build_summary(results)

    # Print to console
    print(summary)

    # Write to GitHub Step Summary (visible in Actions UI)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(summary)

if __name__ == "__main__":
    main()
