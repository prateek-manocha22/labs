"""Tests for Lab 03: TOON Converter"""
import pytest
from solution import json_to_toon, count_tokens

DATA = [
    {"id": 1, "name": "Alice", "score": 92},
    {"id": 2, "name": "Bob",   "score": 87},
]


def test_toon_has_header():
    result = json_to_toon(DATA)
    assert result.startswith("# fields:"), "First line must start with '# fields:'"


def test_toon_header_contains_all_keys():
    result = json_to_toon(DATA)
    header = result.splitlines()[0]
    for key in DATA[0].keys():
        assert key in header, f"Header must contain key '{key}'"


def test_toon_correct_row_count():
    result = json_to_toon(DATA)
    lines = [l for l in result.splitlines() if not l.startswith("#")]
    assert len(lines) == len(DATA), "Number of data rows must match input length"


def test_toon_uses_pipe_separator():
    result = json_to_toon(DATA)
    data_lines = [l for l in result.splitlines() if not l.startswith("#")]
    assert all("|" in l for l in data_lines), "Each data row must use '|' separator"


def test_count_tokens_basic():
    assert count_tokens("hello world foo") == 3


def test_count_tokens_empty():
    assert count_tokens("") == 0