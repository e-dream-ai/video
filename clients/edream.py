import os
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

edream_client = create_edream_client(backend_url=BACKEND_URL, api_key=BACKEND_API_KEY)
print(f"eDream client initialized (backend: {BACKEND_URL})")
