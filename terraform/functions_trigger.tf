resource "google_pubsub_topic" "scheduler" {
    name = "polling_scheduler"
}

resource "google_cloud_scheduler_job" "poll_trigger" {
    name = "poll-trigger"
    description ="trigger the cloud function that polls the datamesh manager"
    schedule = "* * * * *" # Every minute
    
    pubsub_target {
      topic_name = google_pubsub_topic.scheduler.id
      data = base64encode("{}") # no need for data
    }
}
