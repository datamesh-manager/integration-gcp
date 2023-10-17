import os
import requests
import json
import functions_framework
import datameshmanager_client as dmm
from google.cloud import pubsub, secretmanager, firestore

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/project/project-id'
HEADERS = {'Metadata-Flavor': 'Google'}

def get_project_id():
    response = requests.get(METADATA_URL, headers=HEADERS)
    return response.text

secret = secretmanager.SecretManagerServiceClient()
publisher = pubsub.PublisherClient()
store = firestore.Client()
project_id = get_project_id()
topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=os.getenv("topic"),  # TODO: Use Environment
)
full_api_key_secret_name = 'projects/{project_id}/secrets/{secret}/versions/latest'.format(
    project_id=project_id,
    secret=os.getenv("secret"),  # TODO: Use Environment
)


def get_api_key() -> str:
    return secret.access_secret_version(name=full_api_key_secret_name).payload.data.decode("utf-8")


def get_last_event_id() -> str: 
    document = store.document("Test/last_event_id")
    value = document.get().get("id")
    return value


def set_last_event_id(last_id: str) -> None:
    document = store.document("Test/last_event_id")
    document.set({"id": last_id})


def publish_events(events):
    for event in events:
        data = json.dumps(event).encode('utf-8')
        publisher.publish(topic_name, data=data)
    pass


@functions_framework.http
def main(event):
    api_key = get_api_key()
    client = dmm.DataMeshManagerClient(api_key)

    last_id = get_last_event_id()

    data = client.get_events(last_id)

    if data:
        publish_events(data)
        last_id = data[-1]["id"]
        set_last_event_id(last_id)

    return "OK"
