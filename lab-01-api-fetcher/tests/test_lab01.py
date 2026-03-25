"""Tests for Lab 01: API Fetcher"""
import pytest
from unittest.mock import patch, MagicMock
from solution import fetch_issues, filter_open


MOCK_ISSUES = [
    {"id": 1, "title": "Fix tokenizer bug", "state": "open"},
    {"id": 2, "title": "Add YAML support", "state": "closed"},
    {"id": 3, "title": "Update README", "state": "open"},
]


def test_fetch_issues_returns_list():
    with patch("solution.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = MOCK_ISSUES
        result = fetch_issues("toon-format", "toon")
    assert isinstance(result, list), "fetch_issues should return a list"


def test_fetch_issues_correct_keys():
    with patch("solution.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = MOCK_ISSUES
        result = fetch_issues("toon-format", "toon")
    assert len(result) > 0, "Result should not be empty"
    assert "id" in result[0], "Each issue must have 'id'"
    assert "title" in result[0], "Each issue must have 'title'"
    assert "state" in result[0], "Each issue must have 'state'"


def test_filter_returns_only_open():
    open_issues = filter_open(MOCK_ISSUES)
    assert all(i["state"] == "open" for i in open_issues), "All returned issues must be open"


def test_filter_count():
    open_issues = filter_open(MOCK_ISSUES)
    assert len(open_issues) == 2, "Should find exactly 2 open issues in mock data"
