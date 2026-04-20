import json
import os
import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _optional_int(name: str) -> int | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    parsed = int(value)
    return None if parsed <= 0 else parsed


def _query_dataframe(client, query: str) -> pd.DataFrame:
    return client.query(query).to_dataframe()


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", value.lower())
    return value.strip("_")


def _map_league_name(competition_id: str, competition_name: str) -> str | None:
    comp_id = str(competition_id or "")
    comp_name = str(competition_name or "").lower()
    if comp_id == "83d92007":
        return "European Rugby Challenge Cup"
    if comp_id == "ee0c6883":
        return "European Rugby Champions Cup"
    if comp_name == "major league rugby":
        return "Major League Rugby"
    if comp_name in ("super rugby pacific", "super rugby") or comp_id in ("877aa127", "bc5d9ec5"):
        return "Super Rugby Pacific"
    return None


def _load_from_local_parquet(team_stats_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = sorted(team_stats_dir.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {team_stats_dir}")

    base = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    if base.empty:
        raise ValueError("Local team_stats parquet data is empty")

    # Normalize local source column names to match modeled naming.
    if "team_name" not in base.columns and "team" in base.columns:
        base["team_name"] = base["team"]
    if "opponent_team_name" not in base.columns and "team_vs" in base.columns:
        base["opponent_team_name"] = base["team_vs"]

    if "score_difference" not in base.columns and {"score", "team_vs_score"}.issubset(base.columns):
        base["score_difference"] = pd.to_numeric(base["score"], errors="coerce") - pd.to_numeric(
            base["team_vs_score"], errors="coerce"
        )

    if "match_id" not in base.columns:
        if "game_id" in base.columns:
            base["match_id"] = base["game_id"].astype(str)
        else:
            base["match_id"] = (
                base.get("game_date", "").astype(str)
                + "|"
                + base.get("team_name", "").astype(str)
                + "|"
                + base.get("opponent_team_name", "").astype(str)
            )

    if "game_date" not in base.columns:
        base["game_date"] = pd.NaT
    if "score_difference" not in base.columns:
        base["score_difference"] = np.nan
    if "competition_id" not in base.columns or "competition_name" not in base.columns:
        details_files = sorted(Path("data/raw/match_details").glob("*.parquet"))
        if details_files:
            match_details = pd.concat((pd.read_parquet(f) for f in details_files), ignore_index=True)
            if "match_id" in match_details.columns:
                keep_cols = [c for c in ["match_id", "competition_id", "competition_name"] if c in match_details.columns]
                if keep_cols:
                    match_details = match_details[keep_cols].drop_duplicates(subset=["match_id"])
                    base = base.merge(match_details, on="match_id", how="left", suffixes=("", "_detail"))
                    if "competition_id" not in base.columns and "competition_id_detail" in base.columns:
                        base["competition_id"] = base["competition_id_detail"]
                    if "competition_name" not in base.columns and "competition_name_detail" in base.columns:
                        base["competition_name"] = base["competition_name_detail"]

    if "competition_id" not in base.columns:
        base["competition_id"] = ""
    if "competition_name" not in base.columns:
        base["competition_name"] = ""

    base["game_date"] = pd.to_datetime(base["game_date"], errors="coerce")
    base["score_difference"] = pd.to_numeric(base["score_difference"], errors="coerce")
    base["competition_id"] = base["competition_id"].astype(str)
    base["competition_name"] = base["competition_name"].astype(str)

    base["league_name"] = base.apply(
        lambda r: _map_league_name(r.get("competition_id"), r.get("competition_name")),
        axis=1,
    )

    work = base.dropna(subset=["game_date", "score_difference", "league_name", "team_name"]).copy()
    if work.empty:
        raise ValueError("No usable rows found in local parquet after cleaning")

    labels = (
        work.groupby("match_id")["team_name"]
        .agg(lambda s: " vs ".join(sorted(set(map(str, s.dropna().tolist())))[:2]))
        .to_dict()
    )
    work["match_label"] = work.apply(
        lambda r: f"{r['game_date'].date()} | {labels.get(r['match_id'], '')}".strip(),
        axis=1,
    )

    categorical_df = (
        work.groupby("league_name", as_index=False)
        .agg(
            matches=("match_id", "nunique"),
            avg_match_margin=("score_difference", lambda s: float(np.abs(s).mean())),
            median_match_margin=("score_difference", lambda s: float(np.abs(s).median())),
        )
        .sort_values("avg_match_margin", ascending=False)
    )

    timeseries_df = work[
        [
            "match_id",
            "match_label",
            "game_date",
            "team_name",
            "opponent_team_name",
            "score_difference",
            "league_name",
        ]
    ].copy()

    return categorical_df, timeseries_df


def _plot_league_margin_categorical(df: pd.DataFrame, output_path: Path) -> None:
    if df.empty:
        raise ValueError("Categorical dataset is empty")

    df = df.sort_values("avg_match_margin", ascending=False).reset_index(drop=True)
    x = np.arange(len(df))
    width = 0.36

    fig, ax = plt.subplots(figsize=(11, 6))
    bars_avg = ax.bar(
        x - width / 2,
        df["avg_match_margin"],
        width,
        label="Average margin",
        color="#1f77b4",
    )
    bars_med = ax.bar(
        x + width / 2,
        df["median_match_margin"],
        width,
        label="Median margin",
        color="#ff7f0e",
    )

    ax.set_title("League Match Margin Comparison", fontsize=13, pad=12)
    ax.set_ylabel("Score margin", fontsize=11)
    ax.set_xlabel("League", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(df["league_name"], rotation=18, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)

    for i, matches in enumerate(df["matches"]):
        ymax = max(df.loc[i, "avg_match_margin"], df.loc[i, "median_match_margin"])
        ax.text(i, ymax + 0.15, f"n={int(matches)}", ha="center", va="bottom", fontsize=9)

    for bars in (bars_avg, bars_med):
        for rect in bars:
            height = rect.get_height()
            ax.annotate(
                f"{height:.1f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def _plot_league_score_difference_timeseries(
    df: pd.DataFrame,
    output_dir: Path,
    max_teams_per_league: int | None,
) -> tuple[dict[str, list[str]], dict[str, str]]:
    if df.empty:
        raise ValueError("Timeseries dataset is empty")

    work = df.copy()
    work["game_date"] = pd.to_datetime(work["game_date"], errors="coerce")
    work = work.dropna(subset=["game_date", "team_name", "league_name", "score_difference"])

    leagues = sorted(work["league_name"].dropna().unique().tolist())
    if not leagues:
        raise ValueError("No leagues found after cleaning timeseries dataset")

    selected_teams_by_league: dict[str, list[str]] = {}
    chart_paths_by_league: dict[str, str] = {}
    league_plot_frames: dict[str, pd.DataFrame] = {}
    legend_max_entries = _as_int("MPL_MAX_LEGEND_ENTRIES", 16)
    legend_max_rows = _as_int("MPL_LEGEND_MAX_ROWS", 3)
    if legend_max_entries < 1:
        legend_max_entries = 1
    if legend_max_rows < 1:
        legend_max_rows = 1

    for league in leagues:
        league_df = work[work["league_name"] == league].copy()

        team_counts = league_df.groupby("team_name")["match_id"].count().sort_values(ascending=False)
        if max_teams_per_league is None:
            selected_teams = team_counts.index.tolist()
        else:
            selected_teams = team_counts.head(max_teams_per_league).index.tolist()
        selected_teams_by_league[league] = selected_teams

        plot_df = league_df[league_df["team_name"].isin(selected_teams)]
        league_plot_frames[league] = plot_df.sort_values(["team_name", "game_date"])

    combined_plot_df = pd.concat(league_plot_frames.values(), ignore_index=True)
    y_min = float(combined_plot_df["score_difference"].min())
    y_max = float(combined_plot_df["score_difference"].max())
    span = y_max - y_min
    pad = 1.0 if span == 0 else span * 0.08
    y_limits = (min(y_min - pad, -pad), max(y_max + pad, pad))

    for league in leagues:
        selected_teams = selected_teams_by_league[league]
        plot_df = league_plot_frames[league]
        fig, ax = plt.subplots(figsize=(14, 6))

        legend_handles = []
        legend_labels = []

        for team_name in selected_teams:
            team_df = plot_df[plot_df["team_name"] == team_name]
            if team_df.empty:
                continue

            (line,) = ax.plot(
                team_df["game_date"],
                team_df["score_difference"],
                marker="o",
                markersize=3,
                linewidth=1.4,
                alpha=0.8,
                label=team_name,
            )
            legend_handles.append(line)
            legend_labels.append(team_name)

        ax.axhline(0, linestyle="--", linewidth=1, color="#555555", alpha=0.7)
        if max_teams_per_league is None:
            title_suffix = f"all teams ({len(selected_teams)})"
        else:
            title_suffix = f"top {len(selected_teams)} teams"
        ax.set_title(f"{league} ({title_suffix})", fontsize=11)
        ax.set_xlabel("Game date", fontsize=10)
        ax.set_ylabel("Score difference", fontsize=10)
        ax.set_ylim(y_limits)
        ax.grid(alpha=0.22)
        ax.tick_params(axis="x", rotation=20)

        if legend_handles:
            displayed_handles = legend_handles
            displayed_labels = legend_labels
            hidden_count = 0

            if len(legend_handles) > legend_max_entries:
                displayed_handles = legend_handles[:legend_max_entries]
                displayed_labels = legend_labels[:legend_max_entries]
                hidden_count = len(legend_handles) - legend_max_entries

            ncol = int(np.ceil(len(displayed_labels) / legend_max_rows))
            ncol = max(1, ncol)

            if hidden_count > 0:
                displayed_labels[-1] = f"{displayed_labels[-1]} (+{hidden_count} more)"

            ax.legend(
                displayed_handles,
                displayed_labels,
                loc="upper left",
                ncol=ncol,
                fontsize=6.5,
                frameon=False,
                handlelength=1.2,
                columnspacing=0.8,
                borderaxespad=0.3,
                labelspacing=0.3,
            )

        fig.tight_layout()
        league_slug = _slugify(league)
        chart_path = output_dir / f"league_score_difference_timeseries_{league_slug}.png"
        fig.savefig(chart_path, dpi=160)
        plt.close(fig)
        chart_paths_by_league[league] = str(chart_path)

    return selected_teams_by_league, chart_paths_by_league


def main() -> None:
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET_RAW", "raw")
    source_mode = os.getenv("MPL_DATA_SOURCE", "auto").strip().lower()
    if source_mode not in {"auto", "bigquery", "local"}:
        raise ValueError("MPL_DATA_SOURCE must be one of: auto, bigquery, local")

    output_dir = Path(os.getenv("MATPLOTLIB_DASHBOARD_OUTPUT_DIR", "docs/assets/matplotlib"))
    output_dir.mkdir(parents=True, exist_ok=True)

    max_teams_per_league = _optional_int("MPL_MAX_TEAMS_PER_LEAGUE")

    actual_source = "local"
    categorical_df: pd.DataFrame
    timeseries_df: pd.DataFrame

    if source_mode in {"auto", "bigquery"}:
        if not project_id:
            if source_mode == "bigquery":
                raise EnvironmentError("GCP_PROJECT_ID is required when MPL_DATA_SOURCE=bigquery")
        else:
            try:
                from google.cloud import bigquery  # Imported lazily to avoid hard failure in local mode.

                client = bigquery.Client(project=project_id)
                categorical_query = f"""
                    select
                      league_name,
                      matches,
                      avg_match_margin,
                      median_match_margin
                    from `{project_id}.{dataset}.vw_league_margin_categorical`
                    order by avg_match_margin desc
                """

                timeseries_query = f"""
                    select
                      match_id,
                      match_label,
                      game_date,
                      team_name,
                      opponent_team_name,
                      score_difference,
                      league_name
                    from `{project_id}.{dataset}.vw_league_score_difference_timeseries`
                    order by game_date, team_name
                """

                categorical_df = _query_dataframe(client, categorical_query)
                timeseries_df = _query_dataframe(client, timeseries_query)
                actual_source = "bigquery"
            except Exception:
                if source_mode == "bigquery":
                    raise
                categorical_df, timeseries_df = _load_from_local_parquet(Path("data/raw/team_stats"))
                actual_source = "local"
    else:
        categorical_df, timeseries_df = _load_from_local_parquet(Path("data/raw/team_stats"))
        actual_source = "local"

    categorical_png = output_dir / "league_margin_categorical_matplotlib.png"
    _plot_league_margin_categorical(categorical_df, categorical_png)
    selected_teams_by_league, chart_paths_by_league = _plot_league_score_difference_timeseries(
        timeseries_df,
        output_dir,
        max_teams_per_league=max_teams_per_league,
    )

    summary = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "project_id": project_id,
        "dataset": dataset,
        "data_source": actual_source,
        "inputs": {
            "categorical_view": (
                f"{project_id}.{dataset}.vw_league_margin_categorical" if actual_source == "bigquery" else None
            ),
            "timeseries_view": (
                f"{project_id}.{dataset}.vw_league_score_difference_timeseries"
                if actual_source == "bigquery"
                else None
            ),
            "local_team_stats_dir": "data/raw/team_stats" if actual_source == "local" else None,
            "max_teams_per_league": max_teams_per_league,
            "teams_selection": "all" if max_teams_per_league is None else "top_n",
        },
        "outputs": {
            "categorical_chart": str(categorical_png),
            "timeseries_charts_by_league": chart_paths_by_league,
        },
        "row_counts": {
            "categorical_rows": int(len(categorical_df)),
            "timeseries_rows": int(len(timeseries_df)),
        },
        "teams_rendered_by_league": selected_teams_by_league,
    }

    summary_path = output_dir / "matplotlib_dashboard_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[matplotlib] Wrote categorical chart: {categorical_png}")
    for league_name, chart_path in chart_paths_by_league.items():
        print(f"[matplotlib] Wrote timeseries chart ({league_name}): {chart_path}")
    print(f"[matplotlib] Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()