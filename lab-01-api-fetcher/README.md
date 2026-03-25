# Lab 01: API Fetcher 🌐

**Points: 20 | Time: ~1 hour**

## Problem
Fetch open issues from the `toon-format/toon` GitHub repository (no auth required) and return structured data.

## Your Task
Open `solution.py` and implement the two functions marked with `# TODO`.

## Requirements
- `fetch_issues(owner, repo)` → returns a **list of dicts** with keys: `id`, `title`, `state`
- `filter_open(issues)` → returns only issues where `state == "open"`

## How to Test Locally
```bash
pip install requests pytest
pytest tests/
```
