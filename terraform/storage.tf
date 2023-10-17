resource "google_firestore_document" "event_id" {
  collection  = "last_event"
  document_id = "last_event_id"
  fields = jsonencode({
    id = {
      stringValue = ""
    }
  })
}

resource "google_pubsub_topic" "events" {
  name = "dmm_events"

}

