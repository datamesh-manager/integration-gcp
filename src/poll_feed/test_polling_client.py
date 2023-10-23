import unittest
import json
import os
from unittest.mock import patch, call, MagicMock
from polling_client import PollingClient


class TestPollingClient(unittest.TestCase):
    def test_get_last_event_id(self):
        store = MagicMock()
        document = MagicMock()
        document_field = MagicMock()
        
        document.get.return_value = document_field
        document_field.get.return_value = "test_id"
        store.document.return_value = document
        value = PollingClient._get_last_event_id(store, "name")
        
        assert value == "test_id"
        
    def test_set_last_event_id(self):
        store = MagicMock()
        document = MagicMock()
       
        store.document.return_value = document
        value = PollingClient._set_last_event_id(store, "name", "test_id")

        document.set.assert_called_with({"id": "test_id"})

        
    def test_publish_events(self):
        publisher = MagicMock()
        
        events = [
            {
                "id": 1
            },
            {
                "id": 2
            },
        ]
        
        PollingClient._publish_events(publisher, "topic", events)        
        
        expected_data1 = json.dumps(events[0]).encode('utf-8')
        expected_data2 = json.dumps(events[1]).encode('utf-8')
            
        publisher.publish.assert_has_calls([call("topic", data=expected_data1), call("topic", data=expected_data2)])
    
    
    @patch("polling_client.PollingClient._publish_events")
    @patch("polling_client.PollingClient._set_last_event_id")
    @patch("polling_client.PollingClient._get_last_event_id")
    @patch("os.getenv")
    def test_poll_feed(self, mock_getenv, mock_get_last_event_id, mock_set_last_event_id, mock_publish_events):
        mock_getenv.return_value = "topic"
        datamesh_client = MagicMock()
        
        datamesh_client.get_events.return_value = [
            {
                "id": 1
            }
        ]
        
        PollingClient.poll_feed(datamesh_client, "store", "document_name", "publisher")
        
        mock_getenv.assert_called_with("TOPIC")
        mock_get_last_event_id.assert_called_with("store", "document_name")
        mock_set_last_event_id.assert_called_with("store", "document_name", 1)
        mock_publish_events.assert_called_with("publisher", "topic", [{"id": 1}])
        

if __name__ == '__main__':
    unittest.main()