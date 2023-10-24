import unittest
from datameshmanager_client import DataMeshManagerEvent, DataUsageAgreement
from permissions_manager import PermissionsManager
from google.cloud import bigquery
from unittest.mock import patch, call, Mock, ANY


class TestPermissionsManager(unittest.TestCase):
    
    @patch.object(PermissionsManager, "_deauthorize")
    @patch.object(PermissionsManager, "_authorize")
    def test_process_event_with_activation_event(self, mock_authorize, mock_deauthorize):
        event = {"subject": "test", "type": "com.datamesh-manager.events.DataUsageAgreementActivatedEvent"}
        
        permission_manager = PermissionsManager("dmm_client", "bq_client")
        
        permission_manager.process_event(event)
        
        mock_authorize.assert_called_once()
        mock_deauthorize.assert_not_called()

    @patch.object(PermissionsManager, "_deauthorize")
    @patch.object(PermissionsManager, "_authorize")
    def test_process_event_with_activation_event(self, mock_authorize, mock_deauthorize):
        event = {"subject": "test", "type": "com.datamesh-manager.events.DataUsageAgreementDeactivatedEvent"}
        
        permission_manager = PermissionsManager("dmm_client", "bq_client")
        
        permission_manager.process_event(event)
        
        mock_authorize.assert_not_called()
        mock_deauthorize.assert_called_once()
    
    def test_get_dataset_and_view_id(self):

        mock_agreement = Mock()
        mock_agreement.get_provider_id.return_value = "provider_id"
        mock_agreement.get_consumer_id.return_value = "consumer_id"
        
        mock_product = Mock()
        mock_product.get_custom.return_value = "test.gcp-table-id"
        
        mock_dmm_client = Mock()
        mock_dmm_client.get_data_product.return_value = mock_product
        
        permissions_manager = PermissionsManager(mock_dmm_client, "bq_client")
        
        permissions_manager._get_dataset_and_view_id(mock_agreement)
        
        mock_dmm_client.get_data_product.assert_has_calls([call("provider_id"), call("consumer_id")])
        mock_agreement.get_provider_id.assert_called()
        mock_agreement.get_consumer_id.assert_called()
        assert mock_product.get_custom.call_count == 2
        
    @patch.object(PermissionsManager, "_get_dataset_and_view_id")
    @patch.object(PermissionsManager, "_authorize_view")
    def test_authorize(self, mock_authorize_view, mock_get_dataset_and_view_id):
        mock_dmm_client = Mock()
        permissions_manager = PermissionsManager(mock_dmm_client, "bq_client")
        mock_get_dataset_and_view_id.return_value = ("mock_dataset_id", "mock_view_id")

        event = DataMeshManagerEvent({"subject": "subject", "type": "type"})
        permissions_manager._authorize(event)
        
        mock_get_dataset_and_view_id.assert_called_once()
        mock_dmm_client.get_data_usage_agreement.assert_called_once()
        mock_authorize_view.assert_called_with("mock_dataset_id", "mock_view_id")    
        mock_dmm_client.put_data_usage_agreement.assert_called_with(ANY,{'tags': ['gcp-integration', 'gcp-integration-active']})

    @patch.object(PermissionsManager, "_get_dataset_and_view_id")
    @patch.object(PermissionsManager, "_deauthorize_view")
    def test_deauthorize(self, mock_deauthorize_view, mock_get_dataset_and_view_id):
        mock_dmm_client = Mock()
        permissions_manager = PermissionsManager(mock_dmm_client, "bq_client")
        mock_get_dataset_and_view_id.return_value = ("mock_dataset_id", "mock_view_id")
        
        event = DataMeshManagerEvent({"subject": "subject", "type": "type"})
        permissions_manager._deauthorize(event)
        
        mock_get_dataset_and_view_id.assert_called_once()
        mock_dmm_client.get_data_usage_agreement.assert_called_once()
        mock_deauthorize_view.assert_called_with("mock_dataset_id", "mock_view_id")
        mock_dmm_client.put_data_usage_agreement.assert_called_with(ANY,{'tags': ['gcp-integration', 'gcp-integration-inactive']})
        
    def test_authorize_view_no_entry(self):
        mock_bq_client = Mock()
        
        # Replace with the actual return values
        mock_dataset = Mock()
        mock_dataset.access_entries = []
        mock_bq_client.get_dataset.return_value = mock_dataset

        mock_table = Mock()
        mock_table.reference.to_api_repr.return_value = {"existing": "entry"}
        mock_bq_client.get_table.return_value = mock_table

        # Initialize a Permissions Manager instance
        permissions_manager = PermissionsManager("dmm_client", mock_bq_client)

        # Call the method we are testing
        permissions_manager._authorize_view("source_dataset_id", "view_id")

        # Assert that methods have been called
        mock_bq_client.get_dataset.assert_called_with("source_dataset_id")
        mock_bq_client.get_table.assert_called_with("view_id")
        mock_bq_client.update_dataset.assert_called_with(mock_dataset, ["access_entries"])
     
    def test_authorize_view_contains_entry(self):
        mock_bq_client = Mock()
        
        new_entry = bigquery.AccessEntry(None, "view", {"test": "test"})
        
        # Replace with the actual return values
        mock_dataset = Mock()
        mock_dataset.access_entries = [new_entry]
        mock_bq_client.get_dataset.return_value = mock_dataset

        mock_table = Mock()
        mock_table.reference.to_api_repr.return_value = {"test": "test"}
        mock_bq_client.get_table.return_value = mock_table

        # Initialize a Permissions Manager instance
        permissions_manager = PermissionsManager("dmm_client", mock_bq_client)

        # Call the method we are testing
        permissions_manager._authorize_view("source_dataset_id", "view_id")

        # Assert that methods have been called
        mock_bq_client.get_dataset.assert_called_with("source_dataset_id")
        mock_bq_client.get_table.assert_called_with("view_id")
        mock_bq_client.update_dataset.assert_not_called()       
 
    def test_deauthorize_view_no_entry(self):
        mock_bq_client = Mock()
        
        # Replace with the actual return values
        mock_dataset = Mock()
        mock_dataset.access_entries = []
        mock_bq_client.get_dataset.return_value = mock_dataset

        mock_table = Mock()
        mock_table.reference.to_api_repr.return_value = {"existing": "entry"}
        mock_bq_client.get_table.return_value = mock_table

        # Initialize a Permissions Manager instance
        permissions_manager = PermissionsManager("dmm_client", mock_bq_client)

        # Call the method we are testing
        permissions_manager._deauthorize_view("source_dataset_id", "view_id")

        # Assert that methods have been called
        mock_bq_client.get_dataset.assert_called_with("source_dataset_id")
        mock_bq_client.get_table.assert_called_with("view_id")
        mock_bq_client.update_dataset.assert_not_called()
     
    def test_deauthorize_view_contains_entry(self):
        mock_bq_client = Mock()
        
        new_entry = bigquery.AccessEntry(None, "view", {"test": "test"})
        
        # Replace with the actual return values
        mock_dataset = Mock()
        mock_dataset.access_entries = [new_entry]
        mock_bq_client.get_dataset.return_value = mock_dataset

        mock_table = Mock()
        mock_table.reference.to_api_repr.return_value = {"test": "test"}
        mock_bq_client.get_table.return_value = mock_table

        # Initialize a Permissions Manager instance
        permissions_manager = PermissionsManager("dmm_client", mock_bq_client)

        # Call the method we are testing
        permissions_manager._deauthorize_view("source_dataset_id", "view_id")

        # Assert that methods have been called
        mock_bq_client.get_dataset.assert_called_with("source_dataset_id")
        mock_bq_client.get_table.assert_called_with("view_id")
        mock_bq_client.update_dataset.assert_called_with(mock_dataset, ["access_entries"])
