import requests

class ApiHandler:
    def __init__(self, base_url):
        self.base_url = base_url

    def post_request(self, endpoint, payload):
        response = requests.post(f"{self.base_url}/{endpoint}", json=payload)
        return response
    
    def get_request(self, endpoint):
        response = requests.get(f"{self.base_url}/{endpoint}")
        return response