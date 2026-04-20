from pathlib import Path

import pandas as pd
import pytest

from scripts.load_to_bigquery import _latest_file, _normalize_dataframe


def test_latest_file_returns_lexicographically_latest(tmp_path: Path):
    for name in ["teams_20240101.parquet", "teams_20240201.parquet", "teams_20240115.parquet"]:
        (tmp_path / name).touch()

    latest = _latest_file(tmp_path, "teams_*.parquet")
    assert latest.name == "teams_20240201.parquet"


def test_latest_file_raises_on_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        _latest_file(tmp_path, "teams_*.parquet")


def test_normalize_dataframe_serializes_list_and_dict_values():
    df = pd.DataFrame(
        {
            "plain": ["a"],
            "list_col": [[1, 2]],
            "dict_col": [{"k": "v"}],
            "num": [10],
        }
    )

    out = _normalize_dataframe(df)
    assert out.loc[0, "plain"] == "a"
    assert out.loc[0, "list_col"] == "[1, 2]"
    assert out.loc[0, "dict_col"] == '{"k": "v"}'
    assert out.loc[0, "num"] == 10
