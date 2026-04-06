# import requests
# import os

# GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# def _headers():
#     h = {"Accept": "application/vnd.github+json"}
#     if GITHUB_TOKEN:
#         h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
#     return h

# def get_pr_info(repo: str, pr_number: int) -> dict:
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
#     r = requests.get(url, headers=_headers(), timeout=10)
#     r.raise_for_status()
#     data = r.json()

#     # fetch CI status
#     sha = data.get("head", {}).get("sha", "")
#     ci_status = "unknown"
#     if sha:
#         cr = requests.get(
#             f"https://api.github.com/repos/{repo}/commits/{sha}/status",
#             headers=_headers(), timeout=10
#         )
#         if cr.ok:
#             ci_status = cr.json().get("state", "unknown")

#     return {
#         "title":     data.get("title", ""),
#         "author":    data.get("user", {}).get("login", ""),
#         "body":      data.get("body", "") or "",
#         "ci_status": ci_status,
#         "pr_url":    data.get("html_url", ""),
#         "state":     data.get("state", ""),
#         "merged":    data.get("merged", False),
#         "files":     _get_pr_files(repo, pr_number),
#     }

# def _get_pr_files(repo: str, pr_number: int) -> list:
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
#     r = requests.get(url, headers=_headers(), timeout=10)
#     if not r.ok:
#         return []
#     return [f.get("filename", "") for f in r.json()]

# def get_latest_pr(repo: str) -> dict:
#     """Returns the most recent PR (open or merged) for a repo."""
#     url = f"https://api.github.com/repos/{repo}/pulls"
#     # Try open PRs first
#     r = requests.get(url, headers=_headers(), params={"state": "open", "per_page": 1, "sort": "created", "direction": "desc"}, timeout=10)
#     if r.ok and r.json():
#         pr = r.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "open"}

#     # Fallback to closed/merged
#     r2 = requests.get(url, headers=_headers(), params={"state": "closed", "per_page": 1, "sort": "updated", "direction": "desc"}, timeout=10)
#     if r2.ok and r2.json():
#         pr = r2.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "closed"}

#     raise ValueError(f"No PRs found in repo: {repo}")











import requests
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _headers(access_token: str = "") -> dict:
    """
    Build request headers, preferring the per-request access_token over
    the module-level GITHUB_TOKEN env var fallback.
    """
    token = access_token or GITHUB_TOKEN
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"token {token}"
    return h


def get_pr_info(repo: str, pr_number: int, access_token: str = "") -> dict:
    """
    Fetch PR metadata, CI status, and changed files.

    Args:
        repo:         Full repo name, e.g. "owner/repo".
        pr_number:    Pull-request number.
        access_token: OAuth token for the authenticated user.
                      Falls back to the GITHUB_TOKEN env var if omitted.
    """
    headers = _headers(access_token)

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    # Fetch CI status using the same authenticated headers
    sha = data.get("head", {}).get("sha", "")
    ci_status = "unknown"
    if sha:
        cr = requests.get(
            f"https://api.github.com/repos/{repo}/commits/{sha}/status",
            headers=headers,
            timeout=10,
        )
        if cr.ok:
            ci_status = cr.json().get("state", "unknown")

    return {
        "title":     data.get("title", ""),
        "author":    data.get("user", {}).get("login", ""),
        "body":      data.get("body", "") or "",
        "ci_status": ci_status,
        "pr_url":    data.get("html_url", ""),
        "state":     data.get("state", ""),
        "merged":    data.get("merged", False),
        "files":     _get_pr_files(repo, pr_number, access_token),
    }


def _get_pr_files(repo: str, pr_number: int, access_token: str = "") -> list:
    """
    Return a list of filenames changed in the given PR.

    Args:
        repo:         Full repo name, e.g. "owner/repo".
        pr_number:    Pull-request number.
        access_token: OAuth token forwarded from get_pr_info.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    r = requests.get(url, headers=_headers(access_token), timeout=10)
    if not r.ok:
        return []
    return [f.get("filename", "") for f in r.json()]


def get_latest_pr(repo: str, access_token: str = "") -> dict:
    """
    Return the most recent PR (open or merged) for a repo.

    Args:
        repo:         Full repo name, e.g. "owner/repo".
        access_token: OAuth token. Falls back to GITHUB_TOKEN env var.
    """
    headers = _headers(access_token)
    url = f"https://api.github.com/repos/{repo}/pulls"

    # Try open PRs first
    r = requests.get(
        url,
        headers=headers,
        params={"state": "open", "per_page": 1, "sort": "created", "direction": "desc"},
        timeout=10,
    )
    if r.ok and r.json():
        pr = r.json()[0]
        return {"pr_number": pr["number"], "title": pr["title"], "state": "open"}

    # Fallback to closed / merged
    r2 = requests.get(
        url,
        headers=headers,
        params={"state": "closed", "per_page": 1, "sort": "updated", "direction": "desc"},
        timeout=10,
    )
    if r2.ok and r2.json():
        pr = r2.json()[0]
        return {"pr_number": pr["number"], "title": pr["title"], "state": "closed"}

    raise ValueError(f"No PRs found in repo: {repo}")