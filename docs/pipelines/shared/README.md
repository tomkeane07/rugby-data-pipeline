# Shared Pipeline Components

This directory documents components shared by both pipeline variants:

- Looker Studio pipeline (`docs/pipelines/looker-studio`)
- Matplotlib pipeline (`docs/pipelines/matplotlib`)

## Illustration

```mermaid
flowchart LR
  classDef source fill:#f3efe2,stroke:#7a5c2e,color:#2f2416,stroke-width:1px;
  classDef shared fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
  classDef looker fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;
  classDef mpl fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:1px;

  A[rugbypy API] --> B[Kestra flow]
  B --> C[Raw parquet + BigQuery raw]
  C --> D[dbt marts]
  D --> E[Looker Studio outputs]
  D --> F[Matplotlib artifacts]

  class A source;
  class B,C,D shared;
  class E looker;
  class F mpl;
```

## Shared Components

- Ingestion and orchestration flow: `flows/rugby_pipeline_daily.yml`
- Fetch scripts: `scripts/fetch_teams.py`, `scripts/fetch_team_stats.py`, `scripts/fetch_match_details.py`
- Warehouse load: `scripts/load_to_bigquery.py`
- Transformations and tests: `scripts/run_dbt.py`, `dbt/rugby_stats/`
- Core marts consumed by both variants:
  - `vw_league_margin_categorical`
  - `vw_league_score_difference_timeseries`

## Why This Exists

Both variants diverge at presentation/output only (Looker Studio dashboards vs Matplotlib artifacts). Upstream ingestion, modeling, and quality controls are shared.
