import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from rugbypy.team import fetch_team_stats


def _latest_teams_file() -> Path:
    teams_dir = Path("data/raw/teams")
    files = sorted(teams_dir.glob("teams_*.parquet"))
    if not files:
        raise FileNotFoundError("No teams parquet found in data/raw/teams")
    return files[-1]


def _to_text(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value)
    if text.endswith(".0"):
        return text[:-2]
    return text


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def main() -> None:
    run_date = datetime.utcnow().strftime("%Y%m%d")
    max_teams = _as_int("INGEST_MAX_TEAMS", 0)

    teams_file = _latest_teams_file()
    teams_df = pd.read_parquet(teams_file)
    team_ids = teams_df["team_id"].dropna().astype(str).tolist()

    if max_teams > 0:
        team_ids = team_ids[:max_teams]
        print(f"[fetch_team_stats] Limiting to first {len(team_ids)} teams")

    output_dir = Path("data/raw/team_stats")
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    total_rows = 0
    failures: list[dict[str, str]] = []

    for idx, team_id in enumerate(team_ids, start=1):
        try:
            print(f"[fetch_team_stats] ({idx}/{len(team_ids)}) team_id={team_id}")
            df = fetch_team_stats(team_id=team_id)
            if df is None or df.empty:
                success_count += 1
                continue

            latest_date = run_date
            if "game_date" in df.columns and not df["game_date"].dropna().empty:
                latest_date = _to_text(df["game_date"].dropna().max(), run_date)

            output_file = output_dir / f"{team_id}_{latest_date}.parquet"
            df.to_parquet(output_file, index=False)

            row_count = len(df)
            total_rows += row_count
            success_count += 1
            print(f"[fetch_team_stats] wrote {output_file} rows={row_count}")
        except Exception as exc:  # noqa: BLE001
            failure_count += 1
            failures.append({"team_id": team_id, "error": str(exc)})
            print(f"[fetch_team_stats] ERROR team_id={team_id}: {exc}")

    summary = {
        "run_date": run_date,
        "teams_input_file": str(teams_file),
        "teams_processed": len(team_ids),
        "teams_succeeded": success_count,
        "teams_failed": failure_count,
        "team_stats_total_rows": total_rows,
        "team_stats_dir": str(output_dir),
        "failures": failures,
    }

    summary_path = Path("data/raw/run_summaries") / f"fetch_team_stats_summary_{run_date}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[fetch_team_stats] Wrote summary: {summary_path}")
    print(f"[fetch_team_stats] teams_succeeded={success_count} teams_failed={failure_count} rows={total_rows}")


if __name__ == "__main__":
    main()
