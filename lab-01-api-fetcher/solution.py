import requests

def fetch_issues(owner: str, repo: str) -> list[dict]:
    """
    Fetch issues from a GitHub repository.
    API URL: https://api.github.com/repos/{owner}/{repo}/issues
    
    Returns:
        A list of dicts, each with keys: 'id', 'title', 'state'
    """
    # TODO: Make a GET request to the GitHub API
    # TODO: Parse the JSON response
    # TODO: Return a list of dicts with 'id', 'title', 'state'
    pass


def filter_open(issues: list[dict]) -> list[dict]:
    """
    Filter a list of issues and return only those with state == 'open'.
    
    Returns:
        A filtered list of issue dicts
    """
    # TODO: Filter the issues list and return only open ones
    pass
