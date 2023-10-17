resource "google_cloudfunctions2_function" "poll_feed" {
  name        = "poll_feed"
  location    = var.region
  description = "Polling events from Datamesh-Manager"

  build_config {
    runtime = "python311"
    entry_point = "main"    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_bucket.name
        object = google_storage_bucket_object.poll_feed.name
      }
    }
  }
   
  event_trigger {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.scheduler.id
    retry_policy = "RETRY_POLICY_DO_NOT_RETRY" # This is triggered every minute anyhow
  }
  
  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_cloudfunctions2_function" "manage_permissions" {
  name        = "manage_permissions"
  location    = var.region
  description = "Manages permissions based on events from the datamesh manager."

  build_config {
    runtime = "python311"
    entry_point = "main"    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_bucket.name
        object = google_storage_bucket_object.manage_permissions.name
      }
    }
  }
   
  event_trigger {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.events.id
    retry_policy = "RETRY_POLICY_RETRY"
  }
  
  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}
