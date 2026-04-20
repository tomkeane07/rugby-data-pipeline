# Shared Component: Matplotlib Pipeline Runtime and Configuration

This page describes the shared runtime behavior used by all Matplotlib dashboard charts.

## Visual Overview

```mermaid
flowchart TD
    classDef source fill:#f3efe2,stroke:#7a5c2e,color:#2f2416,stroke-width:1px;
    classDef ingest fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:1px;
    classDef raw fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
    classDef transform fill:#fde7c8,stroke:#b7791f,color:#4a2b00,stroke-width:1px;
    classDef serve fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;

    A[BigQuery marts] --> D[generate_matplotlib_dashboard_charts.py]
    B[data/raw/team_stats/*.parquet] --> D
    C[data/raw/match_details/*.parquet] --> D
    D --> E[league_margin_categorical_matplotlib.png]
    D --> F[league_score_difference_timeseries_*.png]
    D --> G[matplotlib_dashboard_summary.json]

    class A,B,C source;
    class D ingest;
    class E,F,G serve;
```

## Purpose

The Matplotlib pipeline provides code-first, reproducible chart images without manual dashboard authoring.

It is intended for:

- report artifacts committed to the repository
- deterministic reruns across environments
- visual validation of mart outputs

## Runtime Entrypoint

Main script:

- `scripts/generate_matplotlib_dashboard_charts.py`

Make target:

- `make matplotlib-dashboard`

## Data Source Strategy

The runtime supports two source modes:

1. BigQuery views (`MPL_DATA_SOURCE=bigquery`)
2. Local parquet fallback (`MPL_DATA_SOURCE=local`)

Default mode is `auto`, which attempts BigQuery first and falls back to local parquet if needed.

## Environment Controls

- `MPL_DATA_SOURCE`: `auto`, `bigquery`, or `local`
- `MPL_MAX_TEAMS_PER_LEAGUE`: if unset/empty or <= 0, plot all teams; otherwise apply top-N cap
- `MPL_MAX_LEGEND_ENTRIES`: cap legend entries per chart
- `MPL_LEGEND_MAX_ROWS`: legend row cap used to compute multi-column layout
- `MATPLOTLIB_DASHBOARD_OUTPUT_DIR`: output directory for all generated artifacts

## Output Contracts

Charts are written to `docs/assets/matplotlib/` by default:

- one categorical chart image
- one time-series image per league
- one summary JSON with source metadata, row counts, and generated output paths

The summary file is:

- `docs/assets/matplotlib/matplotlib_dashboard_summary.json`

## Design Constraints

- Local fallback requires parquet extracts in `data/raw/team_stats` and `data/raw/match_details`.
- League naming uses explicit mapping logic in the script, so new competitions may require mapping updates.
- In containerized runs, dependency corruption can surface as import errors; reinstalling container packages restores runtime in those cases.
