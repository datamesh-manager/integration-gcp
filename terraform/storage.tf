resource "google_firestore_document" "event_id" {
  collection  = var.firestore_collection_name
  document_id = "${var.firestore_collection_name}_id"
  fields = jsonencode({
    id = {
      stringValue = ""
    }
  })
}

resource "google_pubsub_topic" "events" {
  name = var.pubsub.event_topic
}
