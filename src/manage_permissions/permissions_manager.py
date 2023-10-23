import json
import datameshmanager_client as dmm
from google.cloud import bigquery


class PermissionsManager:
    def __init__(self, dmm_client, bq_client):
        self._dmm_client = dmm_client
        self._bq_client = bq_client

    def process_event(self, event):
        # Initialize the DataMeshManagerEvent with the event
        dmm_event = dmm.DataMeshManagerEvent(event)

        # Authorize or deauthorize depending on the event type
        if dmm_event.type.endswith('DataUsageAgreementActivatedEvent'):
            self._authorize(dmm_event)
        elif dmm_event.type.endswith('DataUsageAgreementDeactivatedEvent'):
            self._deauthorize(dmm_event)

    def _get_dataset_and_view_id(self, event):
        # Get the data usage agreement from the event subject
        agreement = self._dmm_client.get_data_usage_agreement(event.subject)
    
        # Retrieve the provider and consumer data products from the agreement
        provider = self._dmm_client.get_data_product(agreement.get_provider_id())
        consumer = self._dmm_client.get_data_product(agreement.get_consumer_id())
    
        # Extract the source dataset ID and view ID from the respective data products
        source_dataset_id = provider.get_custom("gcp-table-id").rsplit('.', 1)[0]
        view_id = consumer.get_custom("gcp-table-id")
    
        return source_dataset_id, view_id
    
    def _authorize(self, event):
        source_dataset_id, view_id = self._get_dataset_and_view_id(event)
        # Authorize the view with source dataset ID and view ID
        self._authorize_view(source_dataset_id, view_id)
    
    def _deauthorize(self, event):
        source_dataset_id, view_id = self._get_dataset_and_view_id(event)
        # De-authorize the view with source dataset ID and view ID
        self._deauthorize_view(source_dataset_id, view_id)

    def _authorize_view(self, source_dataset_id: str, view_id: str):
        # Get the dataset and table from BigQuery
        dataset = self._bq_client.get_dataset(source_dataset_id)
        table = self._bq_client.get_table(view_id)
    
        # Check if the current access entry already exists, and if not, append it
        entries = dataset.access_entries
        new_entry = bigquery.AccessEntry(None, "view", table.reference.to_api_repr())
        
        entry_exists = any(entry.entity_id == new_entry.entity_id and entry.role == new_entry.role for entry in entries)
    
        if entry_exists:
            PermissionsManager._log_warning(f"Couldn't authorize view. Authorization for view {view_id} already exists.")
            return
    
        entries.append(new_entry)
        dataset.access_entries = entries
        self._bq_client.update_dataset(dataset, ["access_entries"])
        print("Authorized view: ", table.reference)
    
    def _deauthorize_view(self, source_dataset_id: str, view_id: str):
        # Get the dataset and table from BigQuery
        dataset = self._bq_client.get_dataset(source_dataset_id)
        table = self._bq_client.get_table(view_id)
    
        # Find the matching access entry and remove it from the entries
        entries = dataset.access_entries
        entry = PermissionsManager._find_entry(entries, table.reference.to_api_repr())
    
        if not entry:
            PermissionsManager._log_warning(f"Couldn't deauthorize view. No authorization for view {view_id} exists.")
            return
    
        entries.remove(entry)
        dataset.access_entries = entries
        self._bq_client.update_dataset(dataset, ["access_entries"])
        print("Deauthorized view: ", table.reference)

    @staticmethod
    def _log_warning(message):
        entry = dict(
            severity="WARNING",
            message=message
        )
        print(json.dumps(entry))

    @staticmethod
    def _find_entry(entries, api_repr):
        # Iterate over the entries to find the matching entry
        for entry in entries:
            if entry.role is None and entry.entity_type == "view" and entry.entity_id == api_repr:
                return entry
            return None
