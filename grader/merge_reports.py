"""
Merges per-lab pytest JSON reports into a single consolidated report.
Called by the GitHub Actions workflow after running all labs.
"""
import json
import glob

def merge():
    all_tests = []
    for report_file in glob.glob("test_results_*.json"):
        with open(report_file) as f:
            data = json.load(f)
            all_tests.extend(data.get("tests", []))

    merged = {"tests": all_tests}
    with open("test_results.json", "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Merged {len(all_tests)} test results from {len(glob.glob('test_results_*.json'))} labs.")

if __name__ == "__main__":
    merge()
