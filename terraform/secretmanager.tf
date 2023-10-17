resource "google_secret_manager_secret" "dmm_api_key" {
  secret_id = "DMM_ApiKey"
  
  replication {
      auto {}
  }
}

resource "google_secret_manager_secret_version" "dmm_api_key" {
    secret = google_secret_manager_secret.dmm_api_key.id
    secret_data = var.dmm_api_key
    deletion_policy = "DELETE"    
}