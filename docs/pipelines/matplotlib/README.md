# Matplotlib Dashboard Development Documentation

This directory documents the Matplotlib pipeline variant and mirrors the structure used for the Looker Studio pipeline docs.

## Illustration

```mermaid
flowchart TD
	classDef shared fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
	classDef mpl fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:1px;

	A[Shared marts or local parquet fallback] --> B[generate_matplotlib_dashboard_charts.py]
	B --> C[Categorical chart image]
	B --> D[Per-league timeseries images]
	B --> E[matplotlib_dashboard_summary.json]

	class A shared;
	class B,C,D,E mpl;
```

## Graph Documentation

- [League Margin Categorical Graph (Matplotlib)](./graphs/league_margin_categorical_matplotlib.md)
- [League Score Difference Timeseries Graph (Matplotlib)](./graphs/league_score_difference_timeseries_matplotlib.md)

## Shared Components

- [Matplotlib Pipeline Runtime and Configuration](./shared/matplotlib_pipeline_runtime_and_config.md)

## Recommended Reading Order

1. Read the shared component page first to understand data sources, runtime controls, and output conventions.
2. Read each graph page for chart-specific logic, behavior, and artifact naming.
