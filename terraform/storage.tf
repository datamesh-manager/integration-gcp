# Creates a firestore collection within the default database with a document only containing
# an empty 'id' field to store the latest id of polled events
resource "google_firestore_document" "event_id" {
  collection  = var.firestore_collection_name
  document_id = "${var.firestore_collection_name}_id"
  fields = jsonencode({
    id = {
      stringValue = ""
    }
  })
}

# Creates the pubsub topic that holds the events polled from the datamesh manager
resource "google_pubsub_topic" "events" {
  name = var.pubsub.event_topic
}
