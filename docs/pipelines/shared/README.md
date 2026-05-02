# Shared Pipeline Components

This directory documents components shared by both pipeline variants:

- Looker Studio pipeline (`docs/pipelines/looker-studio`)
- Matplotlib pipeline (`docs/pipelines/matplotlib`)

## Illustration

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 30, "rankSpacing": 60, "diagramPadding": 8}, "themeVariables": {"fontSize": "18px", "lineColor": "#b22222", "titleColor": "#1a1a1a"}} }%%
flowchart LR
  classDef source fill:#f3efe2,stroke:#7a5c2e,color:#2f2416,stroke-width:2px;
  classDef host fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:2px;
  classDef cloud fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:2px;
  classDef serve fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:2px;
  classDef phase fill:#fff7e6,stroke:#8a6d3b,color:#4a2b00,stroke-dasharray: 4 2;

  subgraph INTERNET["🌐 External Source"]
    A[rugbypy API]
  end

  subgraph HOST["🖥️ Host Machine"]
    H1([Acquire and Land])
    B[Kestra flow]
    C[Raw parquet]
  end

  subgraph GCP["☁️ Google Cloud"]
    G1([Model and Serve])
    D[BigQuery raw plus dbt marts]
    E[Looker Studio outputs]
  end

  A --> B --> C
  C -. load to cloud .-> D
  D --> E
  D -. export .-> F[Matplotlib artifacts]

  H1 --> B
  H1 --> C
  G1 --> D
  G1 --> E

  class A source;
  class B,C,F host;
  class D cloud;
  class E serve;
  class H1,G1 phase;

  linkStyle default stroke:#b22222,stroke-width:2.5px,opacity:1;

  style INTERNET fill:#fff8ec,stroke:#7a5c2e,stroke-width:2px
  style HOST fill:#eff9ef,stroke:#4f7a52,stroke-width:2px
  style GCP fill:#eef5ff,stroke:#4f6b8a,stroke-width:2px
```

## Detailed Architecture

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 18, "rankSpacing": 60, "diagramPadding": 2}, "themeVariables": {"fontSize": "18px", "lineColor": "#b22222", "titleColor": "#1a1a1a"}} }%%
flowchart TB
  classDef external fill:#f3efe2,stroke:#7a5c2e,color:#2f2416,stroke-width:2px;
  classDef host fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:2px;
  classDef cloud fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:2px;
  classDef model fill:#fde7c8,stroke:#b7791f,color:#4a2b00,stroke-width:2px;
  classDef serve fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:2px;
  classDef phase fill:#fff7e6,stroke:#8a6d3b,color:#4a2b00,stroke-dasharray: 4 2;
  classDef spacer fill:none,stroke:none,color:none;

  subgraph INTERNET["🌐 External Source"]
    direction TB
    SRC[rugbypy API]
  end

  subgraph HOST["🖥️ Host Machine"]
    direction TB
    H1([Acquire])
    K0[Schedule or manual trigger]
    K1[fetch_teams]
    K2[fetch_team_stats]
    K3[fetch_match_details]

    H2([Land])
    L1[teams parquet snapshot]
    L2[team_stats parquet history]
    L3[match_details parquet snapshot]

    H3([Publish to Cloud])
    K4[load_to_bigquery]

    H4([Local Delivery])
    C2[Matplotlib PNG artifacts]
    C3[docs assets and evidence]
  end

  subgraph GCP["☁️ Google Cloud"]
    direction TB
    G1([Warehouse Raw])
    R1[raw.teams latest snapshot]
    R2[raw.team_stats partition by game_date]
    R3[raw.team_stats cluster by team_id]
    R4[raw.match_details latest snapshot]

    G2([Model and Quality])
    K5[run_dbt]
    D1[staging models]
    D2[intermediate models]
    D3[fct_team_performance]
    D4[vw_league_margin_categorical]
    D5[vw_league_score_difference_timeseries]
    D6[custom test score symmetry]

    G3([BI Delivery])
    C1[Looker Studio report tiles]
  end

  SRC --> K0
  K0 --> K1
  K0 --> K2
  K0 --> K3

  K1 --> L1
  K2 --> L2
  K3 --> L3

  L1 --> K4
  L2 --> K4
  L3 --> K4

  K4 -. load to cloud .-> R1
  K4 -. load to cloud .-> R2
  K4 -. load to cloud .-> R4
  R2 --> R3

  R1 --> K5
  R2 --> K5
  R4 --> K5
  K5 --> D1 --> D2 --> D3
  D3 --> D4
  D3 --> D5
  D3 --> D6

  D4 --> C1
  D5 --> C1
  D4 -. export .-> C2
  D5 -. export .-> C2
  D6 --> C3
  C1 --> C3
  C2 --> C3

  H1 --> K0
  H1 --> H2 --> H3 --> H4
  H2 --> L1
  H3 --> K4
  H4 --> C2
  G1 --> G2 --> G3
  G1 --> R1
  G2 --> K5
  G3 --> C1

  class SRC external;
  class K0,K1,K2,K3,K4,L1,L2,L3,C2,C3 host;
  class R1,R2,R3,R4,K5 cloud;
  class D1,D2,D3,D4,D5,D6 model;
  class C1 serve;
  class H1,H2,H3,H4,G1,G2,G3 phase;

  linkStyle default stroke:#b22222,stroke-width:2.5px,opacity:1;

  style INTERNET fill:#fff8ec,stroke:#7a5c2e,stroke-width:2px
  style HOST fill:#eff9ef,stroke:#4f7a52,stroke-width:2px
  style GCP fill:#eef5ff,stroke:#4f6b8a,stroke-width:2px
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
