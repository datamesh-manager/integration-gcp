import base64
import os
import json
import functions_framework
from permissions_manager import PermissionsManager
from google.cloud import bigquery


@functions_framework.cloud_event
def main(event):
    # Initialize the BigQuery and DataMeshManager clients
    dmm_client = dmm.DataMeshManagerClient(os.getenv("API_KEY"))
    bq_client = bigquery.Client()
    permissions_manager = PermissionsManager(dmm_client, bq_client)

    # Extract data from the event
    data = event.data["message"]["data"]
    if data:
        # Convert event to json and process it
        decoded_data = base64.b64decode(data).decode("utf-8")
        message = json.loads(decoded_data)
        permissions_manager.process_event(message)
    
    return "OK"
