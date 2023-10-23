import json
import os


class PollingClient:
    def __init__(self):
        pass

    @staticmethod
    def poll_feed(datamesh_client, store, firestore_document_name, publisher) -> None:
        last_id = PollingClient._get_last_event_id(store, firestore_document_name)

        data = datamesh_client.get_events(last_id)
        topic_name = os.getenv("TOPIC")
        if data:
            PollingClient._publish_events(publisher, topic_name, data)
            last_id = data[-1]["id"]
            PollingClient._set_last_event_id(store, firestore_document_name, last_id)

    @staticmethod
    def _get_last_event_id(store, document_name) -> str:
        document = store.document(document_name)
        value = document.get().get("id")
        return value

    @staticmethod
    def _set_last_event_id(store, document_name, last_id: str) -> None:
        document = store.document(document_name)
        document.set({"id": last_id})

    @staticmethod
    def _publish_events(publisher, topic_name, events) -> None:
        for event in events:
            data = json.dumps(event).encode('utf-8')
            publisher.publish(topic_name, data=data)
