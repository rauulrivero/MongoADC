import requests
import config as TSD

class ApiQueryService:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.base_url = "https://www.thesportsdb.com/api/v1/json/"

    
    def _make_url(self, endpoint):
        return self.base_url + self.apiKey + endpoint


    def make_request(self, endpoint, **kwargs):
        params = kwargs
        URL = self._make_url(endpoint)
        response = requests.get(URL, params=params)
        return response.json()
