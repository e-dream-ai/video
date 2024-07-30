import requests
from typing import Optional, Any, Dict

# BACKEND URL TO TARGET
BACKEND_URL = "http://localhost:8081/api/v1"
# USER API KEY TO AUTHORIZE BACKEND REQUESTS
API_KEY = "API_KEY"


class ApiClient:
    """
    A client for making HTTP requests to a backend API
    """

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
        try:
            url = f"{BACKEND_URL}{endpoint}"
            filtered_data = {k: v for k, v in (data or {}).items() if v is not None}
            response = self.session.request(
                method, url, params=params, json=filtered_data
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 4xx, 5xx status codes)
            error_message = f"HTTP error occurred: {http_err}"
            error_response = (
                response.json() if response.content else "No response content"
            )
            print(error_message)
            print(f"Error details: {error_response}")
            raise

        except requests.exceptions.RequestException as req_err:
            # Handle other types of request exceptions
            print(f"Request error occurred: {req_err}")
            raise

        except ValueError as val_err:
            # Handle issues with decoding JSON
            print(f"Value error occurred: {val_err}")
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("DELETE", endpoint, data=data)
