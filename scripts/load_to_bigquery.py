import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from google.cloud import bigquery


def _latest_file(path: Path, pattern: str) -> Path:
    files = sorted(path.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found for {pattern} in {path}")
    return files[-1]


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for col in normalized.columns:
        if normalized[col].dtype == "object":
            normalized[col] = normalized[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x
            )
    return normalized


def main() -> None:
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_raw = os.getenv("BQ_DATASET_RAW", "raw")

    if not project_id:
        raise EnvironmentError("GCP_PROJECT_ID is required")

    teams_file = _latest_file(Path("data/raw/teams"), "teams_*.parquet")
    team_stats_files = sorted(Path("data/raw/team_stats").glob("*.parquet"))
    match_details_files = sorted(Path("data/raw/match_details").glob("match_details_*.parquet"))

    if not team_stats_files:
        raise FileNotFoundError("No team_stats parquet files found in data/raw/team_stats")

    print(f"[load_to_bigquery] Using teams file: {teams_file}")
    print(f"[load_to_bigquery] team_stats files: {len(team_stats_files)}")
    print(f"[load_to_bigquery] match_details files: {len(match_details_files)}")

    teams_df = pd.read_parquet(teams_file)
    stats_df = pd.concat((pd.read_parquet(f) for f in team_stats_files), ignore_index=True)
    match_details_df = (
        pd.concat((pd.read_parquet(f) for f in match_details_files), ignore_index=True)
        if match_details_files
        else pd.DataFrame(columns=["match_id", "game_date", "season", "competition_id", "competition_name"])
    )

    teams_df = _normalize_dataframe(teams_df)
    stats_df = _normalize_dataframe(stats_df)
    match_details_df = _normalize_dataframe(match_details_df)

    if "game_date" in stats_df.columns:
        stats_df["game_date"] = pd.to_datetime(stats_df["game_date"], errors="coerce").dt.date
    if "game_date" in match_details_df.columns:
        match_details_df["game_date"] = pd.to_datetime(match_details_df["game_date"], errors="coerce").dt.date

    client = bigquery.Client(project=project_id)

    teams_table = f"{project_id}.{dataset_raw}.teams"
    stats_table = f"{project_id}.{dataset_raw}.team_stats"
    match_details_table = f"{project_id}.{dataset_raw}.match_details"

    teams_job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

    stats_job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="game_date",
        ),
        clustering_fields=["team_id"],
    )

    match_details_job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="game_date",
        ),
        clustering_fields=["competition_id"],
    )

    teams_job = client.load_table_from_dataframe(teams_df, teams_table, job_config=teams_job_config)
    teams_job.result()

    stats_job = client.load_table_from_dataframe(stats_df, stats_table, job_config=stats_job_config)
    stats_job.result()

    match_details_job = client.load_table_from_dataframe(
        match_details_df,
        match_details_table,
        job_config=match_details_job_config,
    )
    match_details_job.result()

    teams_rows = int(client.get_table(teams_table).num_rows)
    stats_rows = int(client.get_table(stats_table).num_rows)
    match_details_rows = int(client.get_table(match_details_table).num_rows)

    summary = {
        "run_finished": datetime.utcnow().isoformat() + "Z",
        "project_id": project_id,
        "teams_table": teams_table,
        "team_stats_table": stats_table,
        "teams_rows": teams_rows,
        "team_stats_rows": stats_rows,
        "match_details_rows": match_details_rows,
        "team_stats_files_loaded": len(team_stats_files),
        "match_details_files_loaded": len(match_details_files),
    }

    summary_path = Path("data/raw/run_summaries") / f"load_to_bigquery_summary_{datetime.utcnow().strftime('%Y%m%d')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[load_to_bigquery] Loaded teams rows: {teams_rows}")
    print(f"[load_to_bigquery] Loaded team_stats rows: {stats_rows}")
    print(f"[load_to_bigquery] Loaded match_details rows: {match_details_rows}")
    print(f"[load_to_bigquery] Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
