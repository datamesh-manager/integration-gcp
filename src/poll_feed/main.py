import os
import functions_framework
import datameshmanager_client as dmm
from polling_client import PollingClient
from google.cloud import pubsub, firestore


@functions_framework.cloud_event
def main(event):
    datamesh_client = dmm.DataMeshManagerClient(os.getenv("API_KEY"))
    publisher = pubsub.PublisherClient()
    store = firestore.Client()
    firestore_document_name = os.getenv("FIRESTORE_DOCUMENT")

    PollingClient.poll_feed(datamesh_client, store, firestore_document_name, publisher)

    return "OK"
