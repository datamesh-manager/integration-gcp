# Creates the secret for the datamesh manager api key
resource "google_secret_manager_secret" "dmm_api_key" {
  secret_id = var.secret.name
  
  replication {
      auto {}
  }
}

# Stores the api key as a new version in the secret
# This version will automatically be deleted if there is a newer version
resource "google_secret_manager_secret_version" "dmm_api_key" {
    secret = google_secret_manager_secret.dmm_api_key.id
    secret_data = var.secret.datamesh_manager_api_key
    deletion_policy = "DELETE"    
}