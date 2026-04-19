import json
import os
from datetime import datetime
from pathlib import Path

from google.cloud import bigquery


def main() -> None:
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET_RAW", "raw")
    if not project_id:
        raise EnvironmentError("GCP_PROJECT_ID is required")
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path("docs/evidence/milestone4") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    client = bigquery.Client(project=project_id)

    queries = {
        "table_inventory": f"""
            SELECT table_name, table_type
            FROM `{project_id}.{dataset}.INFORMATION_SCHEMA.TABLES`
            WHERE table_name IN ('teams', 'team_stats')
            ORDER BY table_name
        """,
        "partition_cluster": f"""
            SELECT
              c.table_name,
              MAX(IF(c.is_partitioning_column = 'YES', c.column_name, NULL)) AS partitioning_column,
              ARRAY_AGG(
                IF(c.clustering_ordinal_position IS NOT NULL, c.column_name, NULL)
                IGNORE NULLS
                ORDER BY c.clustering_ordinal_position
              ) AS clustering_columns
            FROM `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMNS` c
            WHERE c.table_name = 'team_stats'
            GROUP BY c.table_name
        """,
        "row_counts": f"""
            SELECT 'teams' AS table_name, COUNT(*) AS row_count FROM `{project_id}.{dataset}.teams`
            UNION ALL
            SELECT 'team_stats' AS table_name, COUNT(*) AS row_count FROM `{project_id}.{dataset}.team_stats`
        """,
        "team_stats_date_bounds": f"""
            SELECT
              MIN(game_date) AS min_game_date,
              MAX(game_date) AS max_game_date,
              COUNT(DISTINCT team_id) AS distinct_teams
            FROM `{project_id}.{dataset}.team_stats`
        """,
    }

    results: dict[str, list[dict]] = {}
    for name, sql in queries.items():
        rows = [dict(r) for r in client.query(sql).result()]
        results[name] = rows
        (out_dir / f"{name}.json").write_text(
            json.dumps(rows, indent=2, default=str), encoding="utf-8"
        )

    summary = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "project_id": project_id,
        "dataset": dataset,
        "results": results,
    }
    (out_dir / "milestone4_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    md_lines: list[str] = [
        "# Milestone 4 BigQuery Validation Summary",
        "",
        f"- Timestamp (UTC): {summary['timestamp_utc']}",
        f"- Project: {project_id}",
        f"- Dataset: {dataset}",
        "",
        "## Table Presence",
    ]
    for row in results["table_inventory"]:
        md_lines.append(f"- {row['table_name']}: {row['table_type']}")

    md_lines.extend(["", "## Partition and Clustering (team_stats)"])
    if results["partition_cluster"]:
        row = results["partition_cluster"][0]
        md_lines.append(f"- partitioning_column: {row.get('partitioning_column')}")
        md_lines.append(
            f"- clustering_columns: {', '.join(row.get('clustering_columns') or [])}"
        )
    else:
        md_lines.append("- No metadata returned")

    md_lines.extend(["", "## Row Counts"])
    for row in results["row_counts"]:
        md_lines.append(f"- {row['table_name']}: {row['row_count']}")

    md_lines.extend(["", "## Date Bounds and Distinct Teams (team_stats)"])
    if results["team_stats_date_bounds"]:
        row = results["team_stats_date_bounds"][0]
        md_lines.append(f"- min_game_date: {row.get('min_game_date')}")
        md_lines.append(f"- max_game_date: {row.get('max_game_date')}")
        md_lines.append(f"- distinct_teams: {row.get('distinct_teams')}")

    (out_dir / "milestone4_validation.md").write_text(
        "\n".join(md_lines) + "\n", encoding="utf-8"
    )

    print(out_dir)


if __name__ == "__main__":
    main()