resource "google_pubsub_topic" "scheduler" {
    name = var.pubsub.scheduler_topic
}

resource "google_cloud_scheduler_job" "poll_trigger" {
    name = var.functions.scheduler_job
    description ="trigger the cloud function that polls the datamesh manager"
    schedule = "* * * * *" # Every minute
    
    pubsub_target {
      topic_name = google_pubsub_topic.scheduler.id
      data = base64encode("{}") # no need for data
    }
}
