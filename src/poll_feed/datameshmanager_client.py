import requests


class DataUsageAgreement:
    def __init__(self, json):
        self._json = json

    def get_provider_id(self):
        return self._json["provider"]["dataProductId"]

    def get_consumer_id(self):
        return self._json["consumer"]["dataProductId"]


class DataMeshManagerEvent:
    def __init__(self, json):
        self._json = json
        self.type = json["type"]
        self.subject = json["subject"]


class DataProduct:
    def __init__(self, json):
        self._json = json
        
    def get_custom(self, name):
        return self._json["custom"][name]


class DataMeshManagerClient:
    _data_products = "dataproducts"
    _data_usage_agreements = "datausageagreements"
    _events = "events"
    
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.datamesh-manager.com/api/"

    def get_events(self, last_event_id):
        if last_event_id:
            url = f"{self._base_url}{self._events}?lastEventId={last_event_id}"
        else:
            url = f"{self._base_url}{self._events}"
            
        headers = {
            'accept': "application/cloudevents-batch+json",
            'x-api-key': self._api_key
        }
        r = requests.get(url, headers=headers)
        return r.json()
