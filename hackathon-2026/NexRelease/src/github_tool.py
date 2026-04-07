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











# import requests
# import os

# GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


# def _headers(access_token: str = "") -> dict:
#     """
#     Build request headers, preferring the per-request access_token over
#     the module-level GITHUB_TOKEN env var fallback.
#     """
#     token = access_token or GITHUB_TOKEN
#     h = {"Accept": "application/vnd.github+json"}
#     if token:
#         h["Authorization"] = f"token {token}"
#     return h


# def get_pr_info(repo: str, pr_number: int, access_token: str = "") -> dict:
#     """
#     Fetch PR metadata, CI status, and changed files.

#     Args:
#         repo:         Full repo name, e.g. "owner/repo".
#         pr_number:    Pull-request number.
#         access_token: OAuth token for the authenticated user.
#                       Falls back to the GITHUB_TOKEN env var if omitted.
#     """
#     headers = _headers(access_token)

#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
#     r = requests.get(url, headers=headers, timeout=10)
#     r.raise_for_status()
#     data = r.json()

#     # Fetch CI status using the same authenticated headers
#     sha = data.get("head", {}).get("sha", "")
#     ci_status = "unknown"
#     if sha:
#         cr = requests.get(
#             f"https://api.github.com/repos/{repo}/commits/{sha}/status",
#             headers=headers,
#             timeout=10,
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
#         "files":     _get_pr_files(repo, pr_number, access_token),
#     }


# def _get_pr_files(repo: str, pr_number: int, access_token: str = "") -> list:
#     """
#     Return a list of filenames changed in the given PR.

#     Args:
#         repo:         Full repo name, e.g. "owner/repo".
#         pr_number:    Pull-request number.
#         access_token: OAuth token forwarded from get_pr_info.
#     """
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
#     r = requests.get(url, headers=_headers(access_token), timeout=10)
#     if not r.ok:
#         return []
#     return [f.get("filename", "") for f in r.json()]


# def get_latest_pr(repo: str, access_token: str = "") -> dict:
#     """
#     Return the most recent PR (open or merged) for a repo.

#     Args:
#         repo:         Full repo name, e.g. "owner/repo".
#         access_token: OAuth token. Falls back to GITHUB_TOKEN env var.
#     """
#     headers = _headers(access_token)
#     url = f"https://api.github.com/repos/{repo}/pulls"

#     # Try open PRs first
#     r = requests.get(
#         url,
#         headers=headers,
#         params={"state": "open", "per_page": 1, "sort": "created", "direction": "desc"},
#         timeout=10,
#     )
#     if r.ok and r.json():
#         pr = r.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "open"}

#     # Fallback to closed / merged
#     r2 = requests.get(
#         url,
#         headers=headers,
#         params={"state": "closed", "per_page": 1, "sort": "updated", "direction": "desc"},
#         timeout=10,
#     )
#     if r2.ok and r2.json():
#         pr = r2.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "closed"}

#     raise ValueError(f"No PRs found in repo: {repo}")











# import requests
# import os

# GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


# def _headers(access_token: str = "") -> dict:
#     token = access_token or GITHUB_TOKEN
#     h = {"Accept": "application/vnd.github+json"}
#     if token:
#         h["Authorization"] = f"Bearer {token}"
#     return h


# def get_pr_info(repo: str, pr_number: int, access_token: str = "") -> dict:
#     headers = _headers(access_token)
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
#     r = requests.get(url, headers=headers, timeout=15)

#     if r.status_code == 403:
#         remaining = r.headers.get("X-RateLimit-Remaining", "?")
#         reset_time = r.headers.get("X-RateLimit-Reset", "?")
#         raise Exception(
#             f"GitHub API rate limit hit (remaining: {remaining}). "
#             f"Make sure a valid GitHub token is configured."
#         )

#     if r.status_code == 404:
#         raise Exception(f"PR #{pr_number} not found in repo {repo}.")

#     r.raise_for_status()
#     data = r.json()

#     sha = data.get("head", {}).get("sha", "")
#     ci_status = "no CI configured"
#     if sha:
#         cr = requests.get(
#             f"https://api.github.com/repos/{repo}/commits/{sha}/status",
#             headers=headers, timeout=10,
#         )
#         if cr.ok:
#             state = cr.json().get("state", "")
#             if state == "success":
#                 ci_status = "all checks passed"
#             elif state == "failure":
#                 ci_status = "checks failing"
#             elif state == "pending":
#                 ci_status = "checks pending"
#             else:
#                 ci_status = "no CI configured"

#     return {
#         "title":     data.get("title", ""),
#         "author":    data.get("user", {}).get("login", ""),
#         "body":      data.get("body", "") or "No description provided",
#         "ci_status": ci_status,
#         "pr_url":    data.get("html_url", ""),
#         "state":     data.get("state", ""),
#         "merged":    data.get("merged", False),
#         "files":     _get_pr_files(repo, pr_number, access_token),
#     }


# def _get_pr_files(repo: str, pr_number: int, access_token: str = "") -> list:
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
#     r = requests.get(url, headers=_headers(access_token), timeout=10)
#     if not r.ok:
#         return []
#     return [f.get("filename", "") for f in r.json()]


# def get_latest_pr(repo: str, access_token: str = "") -> dict:
#     headers = _headers(access_token)
#     url = f"https://api.github.com/repos/{repo}/pulls"
#     r = requests.get(
#         url, headers=headers,
#         params={"state": "open", "per_page": 1, "sort": "created", "direction": "desc"},
#         timeout=10,
#     )
#     if r.ok and r.json():
#         pr = r.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "open"}
#     r2 = requests.get(
#         url, headers=headers,
#         params={"state": "closed", "per_page": 1, "sort": "updated", "direction": "desc"},
#         timeout=10,
#     )
#     if r2.ok and r2.json():
#         pr = r2.json()[0]
#         return {"pr_number": pr["number"], "title": pr["title"], "state": "closed"}
#     raise ValueError(f"No PRs found in repo: {repo}")




import requests
import os
import time

# Fallback token from environment (optional — user tokens take priority)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _headers(token=None):
    """Build headers with auth token. User token takes priority over env token."""
    h = {"Accept": "application/vnd.github+json"}
    t = token or GITHUB_TOKEN
    if t:
        h["Authorization"] = f"Bearer {t}"
    return h


def _get_with_retry(url, headers, params=None, max_retries=3):
    """
    Make a GET request with exponential backoff retry logic.
    Handles 403 rate limit and 429 too-many-requests gracefully.
    """
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)

            # Rate limit hit — wait and retry
            if r.status_code in (403, 429):
                retry_after = int(r.headers.get("Retry-After", 0))
                reset_time  = int(r.headers.get("X-RateLimit-Reset", 0))
                remaining   = int(r.headers.get("X-RateLimit-Remaining", -1))

                if remaining == 0 and reset_time:
                    wait = max(reset_time - int(time.time()), 1)
                    # Cap wait at 30s so we don't hang forever
                    wait = min(wait, 30)
                elif retry_after:
                    wait = retry_after
                else:
                    wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s

                time.sleep(wait)
                continue

            return r

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
        except requests.exceptions.RequestException:
            raise

    return r  # return last response if all retries exhausted


def get_pr_info(repo: str, pr_number: int, token: str = None) -> dict:
    """
    Fetch PR details from GitHub API.
    Always pass token= from the logged-in user's session to avoid rate limits.
    Unauthenticated requests share a 60/hour limit across all IPs.
    Authenticated requests get 5000/hour per user.
    """
    headers = _headers(token)

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    r = _get_with_retry(url, headers)
    r.raise_for_status()
    data = r.json()

    # Fetch CI status
    sha = data.get("head", {}).get("sha", "")
    ci_status = "no CI configured"
    if sha:
        cr = _get_with_retry(
            f"https://api.github.com/repos/{repo}/commits/{sha}/status",
            headers
        )
        if cr.ok:
            ci_status = cr.json().get("state", "no CI configured")

    return {
        "title":     data.get("title", ""),
        "author":    data.get("user", {}).get("login", ""),
        "body":      data.get("body", "") or "",
        "ci_status": ci_status,
        "pr_url":    data.get("html_url", ""),
        "state":     data.get("state", ""),
        "merged":    data.get("merged", False),
    }


def _get_pr_files(repo: str, pr_number: int, token: str = None) -> list:
    """Fetch list of files changed in a PR."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    r = _get_with_retry(url, _headers(token))
    if not r.ok:
        return []
    return [f.get("filename", "") for f in r.json()]


def get_latest_pr(repo: str, token: str = None) -> dict:
    """Returns the most recent PR (open or merged) for a repo."""
    headers = _headers(token)
    url = f"https://api.github.com/repos/{repo}/pulls"

    # Try open PRs first
    r = _get_with_retry(url, headers, params={
        "state": "open", "per_page": 1, "sort": "created", "direction": "desc"
    })
    if r.ok and r.json():
        pr = r.json()[0]
        return {"pr_number": pr["number"], "title": pr["title"], "state": "open"}

    # Fallback to closed/merged
    r2 = _get_with_retry(url, headers, params={
        "state": "closed", "per_page": 1, "sort": "updated", "direction": "desc"
    })
    if r2.ok and r2.json():
        pr = r2.json()[0]
        return {"pr_number": pr["number"], "title": pr["title"], "state": "closed"}

    raise ValueError(f"No PRs found in repo: {repo}")