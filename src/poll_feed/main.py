import os
import json
import functions_framework
import datameshmanager_client as dmm
from google.cloud import pubsub, firestore

publisher = pubsub.PublisherClient()
store = firestore.Client()


def get_last_event_id(document_name) -> str:
    document = store.document(document_name)
    value = document.get().get("id")
    return value


def set_last_event_id(document_name, last_id: str) -> None:
    document = store.document(document_name)
    document.set({"id": last_id})


def publish_events(topic_name, events):
    for event in events:
        data = json.dumps(event).encode('utf-8')
        publisher.publish(topic_name, data=data)
    pass


@functions_framework.cloud_event
def main(event):
    client = dmm.DataMeshManagerClient(os.getenv("API_KEY"))

    firestore_document_name = os.getenv("FIRESTORE_DOCUMENT")
    last_id = get_last_event_id(firestore_document_name)

    data = client.get_events(last_id)
    topic_name = os.getenv("TOPIC")
    if data:
        publish_events(topic_name, data)
        last_id = data[-1]["id"]
        set_last_event_id(firestore_document_name, last_id)

    return "OK"
