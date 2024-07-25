import requests

BACKEND_URL = "http://localhost:8081/api/v1"
API_KEY = "API_KEY"


class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {API_KEY}",
            }
        )

    def get(self, endpoint, params=None):
        url = f"{BACKEND_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{BACKEND_URL}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
