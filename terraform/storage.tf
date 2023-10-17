# resource "google_firestore_database" "event_id" {
#   name = "(default)"
#   location_id = "eur3"
#   type = "FIRESTORE_NATIVE"
# }

resource "google_firestore_document" "event_id" {
    collection = "last_event"
    document_id = "last_event_id"
    fields = jsonencode({
        id = {
            stringValue = ""
        }
    })
}


