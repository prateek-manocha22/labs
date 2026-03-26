import requests
import json
from itertools import islice

def fetch_github_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response = requests.get(url)

    if response.status_code == 200:
        issues = list(response.json())  # explicit list() satisfies type checker
        print(f"Fetched {len(issues)} issues from {repo}")
        return issues
    else:
        print(f"Error: {response.status_code}")
        return []

if __name__ == "__main__":
    # Example: List issues for the public 'toon-format/toon' repo
    data = fetch_github_issues("toon-format", "toon")

    # Save the sample response for inspection
    with open("sample_response.json", "w") as f:
        json.dump(data, f, indent=4)

    for issue in list(islice(data, 5)):  # islice avoids list-slice type error
        print(f"- [{issue['state']}] {issue['title']}")
