# Creates the pubsub topic for the scheduler
resource "google_pubsub_topic" "scheduler" {
    name = var.pubsub.scheduler_topic
}

# Creates the scheduler that triggers the polling cloud function once every minute
# by placing a message in the pubsub topic
resource "google_cloud_scheduler_job" "poll_trigger" {
    name = var.functions.scheduler_job
    description ="trigger the cloud function that polls the datamesh manager"
    schedule = "* * * * *" # Every minute
    
    pubsub_target {
      topic_name = google_pubsub_topic.scheduler.id
      data = base64encode("{}") # no need for data
    }
}
