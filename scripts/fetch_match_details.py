import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from rugbypy.match import fetch_match_details


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _extract_match_details_row(df: pd.DataFrame) -> dict[str, str | int]:
    row = df.iloc[0]
    return {
        "match_id": str(row.get("match_id", "")),
        "game_date": str(row.get("date", "")),
        "season": int(row.get("season", 0)) if pd.notna(row.get("season")) else None,
        "competition_id": str(row.get("competition_id", "")),
        "competition_name": str(row.get("competition", "")),
    }


def main() -> None:
    run_date = datetime.utcnow().strftime("%Y%m%d")
    limit_matches = _as_int("INGEST_MAX_MATCHES", 0)

    team_stats_files = sorted(Path("data/raw/team_stats").glob("*.parquet"))
    if not team_stats_files:
        raise FileNotFoundError("No team_stats parquet files found in data/raw/team_stats")

    team_stats_df = pd.concat((pd.read_parquet(f) for f in team_stats_files), ignore_index=True)
    if "match_id" not in team_stats_df.columns:
        raise KeyError("match_id column missing from team_stats parquet files")

    all_match_ids = sorted(team_stats_df["match_id"].dropna().astype(str).unique().tolist())

    output_dir = Path("data/raw/match_details")
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_files = sorted(output_dir.glob("match_details_*.parquet"))
    existing_df = (
        pd.concat((pd.read_parquet(f) for f in existing_files), ignore_index=True)
        if existing_files
        else pd.DataFrame(columns=["match_id", "game_date", "season", "competition_id", "competition_name"])
    )
    existing_df = existing_df.drop_duplicates(subset=["match_id"])
    existing_ids = set(existing_df["match_id"].dropna().astype(str).tolist())

    match_ids = [m for m in all_match_ids if m not in existing_ids]
    if limit_matches > 0:
        match_ids = match_ids[:limit_matches]
        print(f"[fetch_match_details] Limiting to first {len(match_ids)} missing matches")

    print(
        f"[fetch_match_details] total_match_ids={len(all_match_ids)} "
        f"existing={len(existing_ids)} to_fetch={len(match_ids)}"
    )

    rows: list[dict[str, str | int]] = []
    failures: list[dict[str, str]] = []

    for idx, match_id in enumerate(match_ids, start=1):
        try:
            print(f"[fetch_match_details] ({idx}/{len(match_ids)}) match_id={match_id}")
            details_df = fetch_match_details(match_id=match_id)
            if details_df is None or details_df.empty:
                failures.append({"match_id": match_id, "error": "no rows returned"})
                continue
            rows.append(_extract_match_details_row(details_df))
        except Exception as exc:  # noqa: BLE001
            failures.append({"match_id": match_id, "error": str(exc)})
            print(f"[fetch_match_details] ERROR match_id={match_id}: {exc}")

    new_df = pd.DataFrame(rows)
    match_details_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=["match_id"])
    output_file = output_dir / f"match_details_{run_date}.parquet"
    match_details_df.to_parquet(output_file, index=False)

    summary = {
        "run_date": run_date,
        "match_ids_total": len(all_match_ids),
        "match_ids_fetched_this_run": len(match_ids),
        "match_ids_preexisting": len(existing_ids),
        "match_details_rows": int(len(match_details_df)),
        "output_file": str(output_file),
        "failures_count": len(failures),
        "failures": failures[:200],
    }

    summary_path = Path("data/raw/run_summaries") / f"fetch_match_details_summary_{run_date}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[fetch_match_details] Wrote {output_file} rows={len(match_details_df)}")
    print(f"[fetch_match_details] Failures={len(failures)}")
    print(f"[fetch_match_details] Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
