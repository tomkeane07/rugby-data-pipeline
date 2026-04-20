import pandas as pd

from scripts.ingest_rugby_data import _as_int, _to_date


def test_as_int_reads_env(monkeypatch):
    monkeypatch.setenv("INGEST_MAX_TEAMS", "7")
    assert _as_int("INGEST_MAX_TEAMS", 0) == 7


def test_as_int_uses_default_when_missing(monkeypatch):
    monkeypatch.delenv("INGEST_MAX_TEAMS", raising=False)
    assert _as_int("INGEST_MAX_TEAMS", 3) == 3


def test_to_date_handles_none_and_numeric_suffix():
    assert _to_date(None) == ""
    assert _to_date("20240101.0") == "20240101"
    assert _to_date(pd.Timestamp("2024-01-02")) == "2024-01-02 00:00:00"
