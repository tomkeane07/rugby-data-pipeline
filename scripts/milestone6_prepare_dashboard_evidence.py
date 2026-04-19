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
    out_dir = Path("docs/evidence/milestone6") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    client = bigquery.Client(project=project_id)

    base_select = f"""
        select
          f.game_date,
          f.team_name,
          f.score_difference,
          f.competition_id,
          f.competition_name
        from `{project_id}.{dataset}.fct_team_performance` f
    """

    league_queries = {
        "tile1_european_rugby_challenge_cup_query.sql": (
            base_select
            + """
        where f.competition_id = '83d92007'
        order by f.game_date, f.team_name
    """
        ),
        "tile2_european_rugby_champions_cup_query.sql": (
            base_select
            + """
        where f.competition_id = 'ee0c6883'
        order by f.game_date, f.team_name
    """
        ),
        "tile3_major_league_rugby_query.sql": (
            base_select
            + """
        where f.competition_name = 'Major League Rugby'
        order by f.game_date, f.team_name
    """
        ),
        "tile4_super_rugby_pacific_query.sql": (
            base_select
            + """
        where f.competition_name in ('Super Rugby Pacific', 'Super Rugby')
        order by f.game_date, f.team_name
    """
        ),
    }

    row_counts: dict[str, int] = {}
    for filename, query in league_queries.items():
        rows = [dict(r) for r in client.query(query).result()]
        row_counts[filename] = len(rows)
        (out_dir / filename).write_text(query.strip() + "\n", encoding="utf-8")
        sample_name = filename.replace("_query.sql", "_sample.json")
        (out_dir / sample_name).write_text(json.dumps(rows[:200], indent=2, default=str), encoding="utf-8")

    summary = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "project_id": project_id,
        "dataset": dataset,
        "chart_metric": "score_difference",
        "chart_dimension": "game_date",
        "chart_breakdown_dimension": "team_name",
        "league_row_counts": row_counts,
    }
    (out_dir / "milestone6_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    checklist_md = [
        "# Milestone 6 Looker Studio Checklist",
        "",
        f"- Timestamp (UTC): {summary['timestamp_utc']}",
        f"- BigQuery source table: {project_id}.{dataset}.fct_team_performance",
        "",
        "## Tile 1 (Temporal)",
        "- Chart type: Time series",
        "- Dimension: game_date",
        "- Breakdown dimension: team_name",
        "- Metric: score_difference",
        "- League filter: competition_id = 83d92007 (European Rugby Challenge Cup)",
        "",
        "## Tile 2 (Temporal)",
        "- Chart type: Time series",
        "- Dimension: game_date",
        "- Breakdown dimension: team_name",
        "- Metric: score_difference",
        "- League filter: competition_id = ee0c6883 (European Rugby Champions Cup)",
        "",
        "## Tile 3 (Temporal)",
        "- Chart type: Time series",
        "- Dimension: game_date",
        "- Breakdown dimension: team_name",
        "- Metric: score_difference",
        "- League filter: competition_name = Major League Rugby",
        "",
        "## Tile 4 (Temporal)",
        "- Chart type: Time series",
        "- Dimension: game_date",
        "- Breakdown dimension: team_name",
        "- Metric: score_difference",
        "- League filter: competition_name in (Super Rugby Pacific, Super Rugby)",
        "",
        "## Screenshot Evidence To Capture",
        "1. Dashboard with all four tiles visible",
        "2. A tile showing team_name breakdown active",
        "3. A tile filtered to one season",
        "4. Data source fields panel showing mapped metrics",
        "",
        "## Supporting Files",
        f"- tile1 query: {out_dir / 'tile1_european_rugby_challenge_cup_query.sql'}",
        f"- tile2 query: {out_dir / 'tile2_european_rugby_champions_cup_query.sql'}",
        f"- tile3 query: {out_dir / 'tile3_major_league_rugby_query.sql'}",
        f"- tile4 query: {out_dir / 'tile4_super_rugby_pacific_query.sql'}",
    ]
    (out_dir / "milestone6_dashboard_checklist.md").write_text("\n".join(checklist_md) + "\n", encoding="utf-8")

    print(out_dir)


if __name__ == "__main__":
    main()
