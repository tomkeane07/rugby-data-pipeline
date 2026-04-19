output "bucket_name" {
  value       = google_storage_bucket.data_lake.name
  description = "Provisioned data lake bucket name"
}

output "raw_dataset" {
  value       = google_bigquery_dataset.raw.dataset_id
  description = "Raw BigQuery dataset"
}

output "analytics_dataset" {
  value       = google_bigquery_dataset.analytics.dataset_id
  description = "Analytics BigQuery dataset"
}
