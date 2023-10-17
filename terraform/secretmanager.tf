resource "google_secret_manager_secret" "dmm_api_key" {
  secret_id = var.secret.name
  
  replication {
      auto {}
  }
}

resource "google_secret_manager_secret_version" "dmm_api_key" {
    secret = google_secret_manager_secret.dmm_api_key.id
    secret_data = var.secret.datamesh_manager_api_key
    deletion_policy = "DELETE"    
}