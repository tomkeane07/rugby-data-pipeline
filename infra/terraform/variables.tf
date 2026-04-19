variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for regional resources"
  type        = string
  default     = "europe-west2"
}

variable "bucket_name" {
  description = "Unique GCS bucket name for rugby data lake"
  type        = string
}

variable "dataset_raw" {
  description = "BigQuery raw dataset name"
  type        = string
  default     = "raw"
}

variable "dataset_analytics" {
  description = "BigQuery analytics dataset name"
  type        = string
  default     = "analytics"
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "dev"
}
