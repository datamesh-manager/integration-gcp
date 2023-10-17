variable "google" {
  type = object({
    project = string
    region  = string
  })
}

variable "secret" {
  type = object({
    name                     = string
    datamesh_manager_api_key = string
  })
  sensitive = true
}

variable "functions" {
  type = object({
    source_bucket    = string
    polling_function = string
    manage_function  = string
    scheduler_job    = string
  })
}

variable "pubsub" {
  type = object({
    event_topic     = string
    scheduler_topic = string
  })
}
variable "firestore_collection_name" {
  type = string
}
