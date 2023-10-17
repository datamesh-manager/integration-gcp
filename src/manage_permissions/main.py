import base64
import os
import json
import functions_framework
import datameshmanager_client as dmm
from google.cloud import bigquery

# Initialize the BigQuery and DataMeshManager clients
bq_client = bigquery.Client()


def get_dataset_and_view_id(event):
    # Get the data usage agreement from the event subject
    agreement = dmm_client.get_data_usage_agreement(event.subject)

    # Retrieve the provider and consumer data products from the agreement
    provider = dmm_client.get_data_product(agreement.get_provider_id())
    consumer = dmm_client.get_data_product(agreement.get_consumer_id())
    
    # Extract the source dataset ID and view ID from the respective data products
    source_dataset_id = provider.get_custom("gcp-table-id").rsplit('.', 1)[0]
    view_id = consumer.get_custom("gcp-table-id")
    
    return source_dataset_id, view_id


def authorize(event):
    source_dataset_id, view_id = get_dataset_and_view_id(event)
    # Authorize the view with source dataset ID and view ID
    authorize_view(source_dataset_id, view_id)


def deauthorize(event):
    source_dataset_id, view_id = get_dataset_and_view_id(event)
    # De-authorize the view with source dataset ID and view ID
    deauthorize_view(source_dataset_id, view_id)


def process_event(event):
    # Initialize the DataMeshManagerEvent with the event
    dmm_event = dmm.DataMeshManagerEvent(event)

    # Authorize or deauthorize depending on the event type
    if dmm_event.type.endswith('DataUsageAgreementActivatedEvent'):
        authorize(dmm_event)
    elif dmm_event.type.endswith('DataUsageAgreementDeactivatedEvent'):
        deauthorize(dmm_event)


def authorize_view(source_dataset_id: str, view_id: str):
    # Get the dataset and table from BigQuery
    dataset = bq_client.get_dataset(source_dataset_id)
    table = bq_client.get_table(view_id)

    # Check if the current access entry already exists, and if not, append it
    entries = dataset.access_entries
    new_entry = bigquery.AccessEntry(None, "view", table.reference.to_api_repr())
    entry_exists = any(entry.entity_id == new_entry.entity_id and entry.role == new_entry.role for entry in entries)
    
    if entry_exists:
        return
    
    entries.append(new_entry)
    dataset.access_entries = entries
    bq_client.update_dataset(dataset, ["access_entries"])
    print("Authorized view: ", table.reference)


def find_entry(entries, api_repr):
    # Iterate over the entries to find the matching entry
    for entry in entries:
        if entry.role is None and entry.entity_type == "view" and entry.entity_id == api_repr:
            return entry
    return None
   

def deauthorize_view(source_dataset_id: str, view_id: str):
    # Get the dataset and table from BigQuery
    dataset = bq_client.get_dataset(source_dataset_id)
    table = bq_client.get_table(view_id)

    # Find the matching access entry and remove it from the entries
    entries = dataset.access_entries
    entry = find_entry(entries, table.reference.to_api_repr())
    
    if not entry:
        return
    
    entries.remove(entry)
    dataset.access_entries = entries
    bq_client.update_dataset(dataset, ["access_entries"])
    print("Deauthorized view: ", table.reference)

    
dmm_client = dmm.DataMeshManagerClient(os.getenv("API_KEY"))


@functions_framework.cloud_event
def main(event):
    data = event.data["message"]["data"]
    if data:
        decoded_data = base64.b64decode(data).decode("utf-8")
        message = json.loads(decoded_data)
        print(json.dumps(message))
        process_event(message)
    
    return "OK"
