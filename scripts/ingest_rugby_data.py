import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from rugbypy.team import fetch_all_teams, fetch_team_stats


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _safe_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def _to_date(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.endswith(".0"):
        return text[:-2]
    return text


def main() -> None:
    run_started = datetime.utcnow().isoformat() + "Z"
    run_date = datetime.utcnow().strftime("%Y%m%d")

    output_root = Path(os.getenv("INGEST_OUTPUT_ROOT", "data/raw"))
    max_teams = _as_int("INGEST_MAX_TEAMS", 0)

    teams_path = output_root / "teams" / f"teams_{run_date}.parquet"
    team_stats_root = output_root / "team_stats"

    print("[ingest] Fetching all teams")
    teams_df = fetch_all_teams()
    _safe_to_parquet(teams_df, teams_path)
    print(f"[ingest] Wrote teams parquet: {teams_path} rows={len(teams_df)}")

    team_ids = teams_df["team_id"].dropna().astype(str).tolist()
    if max_teams > 0:
        team_ids = team_ids[:max_teams]
        print(f"[ingest] INGEST_MAX_TEAMS set. Processing first {len(team_ids)} teams")

    success_count = 0
    failure_count = 0
    total_rows = 0
    failures: list[dict[str, str]] = []

    for i, team_id in enumerate(team_ids, start=1):
        try:
            print(f"[ingest] ({i}/{len(team_ids)}) Fetching team stats for team_id={team_id}")
            team_df = fetch_team_stats(team_id=team_id)

            if team_df is None or team_df.empty:
                print(f"[ingest] team_id={team_id} returned no rows")
                success_count += 1
                continue

            dates = team_df.get("game_date")
            if dates is not None and not dates.dropna().empty:
                latest_date = _to_date(dates.dropna().max())
            else:
                latest_date = run_date

            output_file = team_stats_root / f"{team_id}_{latest_date}.parquet"
            _safe_to_parquet(team_df, output_file)

            row_count = len(team_df)
            total_rows += row_count
            success_count += 1
            print(f"[ingest] Wrote team stats parquet: {output_file} rows={row_count}")
        except Exception as exc:  # noqa: BLE001
            failure_count += 1
            failures.append({"team_id": team_id, "error": str(exc)})
            print(f"[ingest] ERROR team_id={team_id}: {exc}")

    summary = {
        "run_started": run_started,
        "run_finished": datetime.utcnow().isoformat() + "Z",
        "teams_total": int(len(teams_df)),
        "teams_processed": int(len(team_ids)),
        "teams_succeeded": int(success_count),
        "teams_failed": int(failure_count),
        "team_stats_total_rows": int(total_rows),
        "teams_parquet": str(teams_path),
        "team_stats_dir": str(team_stats_root),
        "failures": failures,
    }

    summary_path = output_root / "run_summaries" / f"ingest_summary_{run_date}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[ingest] Wrote summary: {summary_path}")

    if failure_count > 0:
        print(f"[ingest] Completed with failures: {failure_count}")
    else:
        print("[ingest] Completed successfully")


if __name__ == "__main__":
    main()
