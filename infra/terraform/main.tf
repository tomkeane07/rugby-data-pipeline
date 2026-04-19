provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "data_lake" {
  name                        = var.bucket_name
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  labels = {
    project     = "rugby-pipeline"
    environment = var.environment
    layer       = "lake"
  }
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = var.dataset_raw
  location   = var.region

  labels = {
    project     = "rugby-pipeline"
    environment = var.environment
    layer       = "raw"
  }
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id = var.dataset_analytics
  location   = var.region

  labels = {
    project     = "rugby-pipeline"
    environment = var.environment
    layer       = "analytics"
  }
}
