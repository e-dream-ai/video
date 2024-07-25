import requests
from client.api_client import ApiClient

client = ApiClient()


def get_playlist():
    try:
        data = client.get("/playlist")
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
