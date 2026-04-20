# Pipeline Documentation Index

This directory separates documentation for the two pipeline presentation tracks used in the project.

## Illustration

```mermaid
flowchart TD
	classDef shared fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
	classDef looker fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;
	classDef mpl fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:1px;

	A[Shared ingestion, load, dbt marts] --> B[Looker Studio pipeline docs]
	A --> C[Matplotlib pipeline docs]

	D[docs/pipelines/shared] --> A
	E[docs/pipelines/looker-studio] --> B
	F[docs/pipelines/matplotlib] --> C

	class A,D shared;
	class B,E looker;
	class C,F mpl;
```

## Pipeline Variants

- [Looker Studio Pipeline Documentation](./looker-studio/README.md)
- [Matplotlib Pipeline Documentation](./matplotlib/README.md)

## Shared Components

- [Shared Pipeline Components](./shared/README.md)

## How To Use This Structure

1. Use the Looker Studio track for BI dashboard configuration and graph semantics in the hosted report tool.
2. Use the Matplotlib track for code-first chart rendering, artifact generation, and reproducible image outputs.
3. Use both when comparing parity between dashboard and code-rendered outputs.
4. Use the shared section for ingestion, loading, and transformation components common to both variants.
