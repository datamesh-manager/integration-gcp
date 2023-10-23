# Creates the function for polling events from the datamesh manager
resource "google_cloudfunctions2_function" "poll_feed" {

  name        = var.functions.polling_function
  location    = var.google.region
  description = "Polling events from datamesh manager"

  build_config {
    runtime     = "python311"
    entry_point = "main"

    # Source code of the function stored in a Google Cloud Storage bucket
    source {
      storage_source {
        bucket = google_storage_bucket.functions_bucket.name
        object = google_storage_bucket_object.poll_feed.name
      }
    }
  }

  # Let this function be triggered by the scheduler pubsub topic
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.scheduler.id
    retry_policy = "RETRY_POLICY_DO_NOT_RETRY"
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
    # Attach the service account to the function
    service_account_email = google_service_account.function_service_account.email

    environment_variables = {
      TOPIC              = google_pubsub_topic.events.id
      FIRESTORE_DOCUMENT = "${google_firestore_document.event_id.path}"
    }

    # Secret environment variables for securing sensitive data
    # so we don't have to manually access the api key from within the function
    secret_environment_variables {
      key        = "API_KEY"
      project_id = data.google_project.project.project_id
      secret     = google_secret_manager_secret.dmm_api_key.secret_id
      version    = "latest"
    }
  }

  # These dependencies are important because otherwise the function can't deploy
  # due to missing permissions to retrieve the secret
  depends_on = [ google_project_iam_member.editor, google_project_iam_member.secret, google_project_iam_member.big_query ]
}

# Creates the function for managing permissions based on events from the datamesh manager
resource "google_cloudfunctions2_function" "manage_permissions" {
  name        = var.functions.manage_function
  location    = var.google.region
  description = "Manages permissions based on events from the datamesh manager."

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_bucket.name
        object = google_storage_bucket_object.manage_permissions.name
      }
    }
  }

  # Let this function be triggered every event that put into the pubsub topic
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.events.id
    retry_policy = "RETRY_POLICY_RETRY"
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60

    # Attach the service account to the function
    service_account_email = google_service_account.function_service_account.email
    environment_variables = {
      SUBSCRIPTION = google_pubsub_topic.events.id
    }

    # Secret environment variables for securing sensitive data
    # so we don't have to manually access the api key from within the function
    secret_environment_variables {
      key        = "API_KEY"
      project_id = data.google_project.project.project_id
      secret     = google_secret_manager_secret.dmm_api_key.secret_id
      version    = "latest"
    }
  }

  # These dependencies are important because otherwise the function can't deploy
  # due to missing permissions to retrieve the secret
  depends_on = [ google_project_iam_member.editor, google_project_iam_member.secret, google_project_iam_member.big_query ]
}
