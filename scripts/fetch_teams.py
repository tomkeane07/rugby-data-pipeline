import json
from datetime import datetime
from pathlib import Path

from rugbypy.team import fetch_all_teams


def main() -> None:
    run_date = datetime.utcnow().strftime("%Y%m%d")
    output_root = Path("data/raw")
    teams_path = output_root / "teams" / f"teams_{run_date}.parquet"
    summary_path = output_root / "run_summaries" / f"fetch_teams_summary_{run_date}.json"

    teams_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    print("[fetch_teams] Fetching teams from rugbypy")
    teams_df = fetch_all_teams()
    teams_df.to_parquet(teams_path, index=False)

    summary = {
        "run_date": run_date,
        "teams_rows": int(len(teams_df)),
        "teams_path": str(teams_path),
    }

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[fetch_teams] Wrote teams file: {teams_path}")
    print(f"[fetch_teams] teams_rows={len(teams_df)}")
    print(f"[fetch_teams] Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
