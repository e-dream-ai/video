import requests
from typing import Optional, Any, Dict

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

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{BACKEND_URL}{endpoint}"
        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("DELETE", endpoint, data=data)
