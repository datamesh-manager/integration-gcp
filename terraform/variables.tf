variable "google" {
  type = object({
    project = string
    region  = string
  })
  description = "Contains the project name and region for this module."
}

variable "secret" {
  type = object({
    name                     = string
    datamesh_manager_api_key = string
  })
  sensitive = true
  description = "Used to create a secret in secretsmanager."
}

variable "functions" {
  type = object({
    source_bucket    = string
    polling_function = string
    manage_function  = string
    scheduler_job    = string
  })
  description = "Contains all information needed for the two cloud functions. Code storage, names of the functions and name of the scheduler job that triggers the polling."
}

variable "pubsub" {
  type = object({
    event_topic     = string
    scheduler_topic = string
  })
  description = "Names of the event topic and scheduler topic"
}
variable "firestore_collection_name" {
  type = string
}
