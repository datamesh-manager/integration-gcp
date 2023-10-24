from requests import get, put


class DataUsageAgreement:
    def __init__(self, json):
        self.json = json

    def get_id(self):
        return self.json["info"]["id"]

    def get_provider_id(self):
        return self.json["provider"]["dataProductId"]

    def get_consumer_id(self):
        return self.json["consumer"]["dataProductId"]


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

    def get_data_usage_agreement(self, id) -> DataUsageAgreement:
        url = f"{self._base_url}{self._data_usage_agreements}/{id}"
        headers = {
            'accept': "application/json",
            'x-api-key': self._api_key
        }
        r = get(url, headers=headers)
        return DataUsageAgreement(r.json())

    def put_data_usage_agreement(self, data_usage_agreement: DataUsageAgreement, tags: dict):
        url = f"{self._base_url}{self._data_usage_agreements}/{data_usage_agreement.get_id()}"
        headers = {
            'accept': "application/json",
            'x-api-key': self._api_key
        }
        r = put(url, headers=headers, json={**data_usage_agreement.json, **tags})

    def get_data_product(self, id) -> DataProduct:
        url = f"{self._base_url}{self._data_products}/{id}"
        headers = {
            'accept': "application/json",
            'x-api-key': self._api_key
        }
        r = get(url, headers=headers)
        return DataProduct(r.json())
