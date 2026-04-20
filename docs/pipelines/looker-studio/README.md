# Looker Studio Pipeline Documentation

This directory documents the Looker Studio version of the analytics pipeline.

## Illustration

```mermaid
flowchart TD
	classDef shared fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
	classDef looker fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;

	A[Shared pipeline marts] --> B[League Margin Categorical Graph]
	A --> C[League Score Difference Timeseries Graph]
	B --> D[Looker Studio tile config]
	C --> D

	class A shared;
	class B,C,D looker;
```

## Graph Documentation

- [League Margin Categorical Graph](./graphs/league_margin_categorical.md)
- [League Score Difference Timeseries Graph](./graphs/league_score_difference_timeseries.md)

## Shared Components

- [Pipeline Orchestration and Loading](../shared/pipeline_orchestration_and_loading.md)
- [Fact Model and Data Quality Guards](../shared/fact_model_and_quality_guards.md)
- [Inspecting fct_team_performance Schema](../shared/fct_team_performance_schema_inspection.md)
- [Ruck Data Availability Profile](../shared/ruck_data_availability_profile.md)

## Recommended Reading Order

1. Read the shared component pages first to understand ingestion, loading, transformation, and quality controls.
2. Read each graph page for graph-specific mart logic, business meaning, and Looker Studio usage.
