import os
import requests
from typing import Optional

# DOWNLOAD_CHUNCK_SIZE = 20 MB
DOWNLOAD_CHUNCK_SIZE = 20 * 1024 * 1024


def download_file_fixed(url: str, file_path: Optional[str] = None) -> bool:
    """
    Downloads a file from a url to a path with better error handling
    This is a patched version that handles Cloudflare R2 signed URLs better
    """
    if file_path is None:
        # Default to basename of URL if no path is provided
        file_path = os.path.basename(url)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        print(f"Attempting to download from URL: {url}")
        
        # Skip HEAD request for now and go directly to GET
        # Some signed URLs (like Cloudflare R2) may not support HEAD requests properly
        
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        print(f"GET request status code: {response.status_code}")
        
        # Raise an error for bad status codes
        response.raise_for_status()

        # Try to get file size from response headers
        file_size = int(response.headers.get("content-length", 0))
        print(f"Expected file size: {file_size} bytes")

        # In progress bytes downloaded
        bytes_downloaded = 0

        # Write the content to a file
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNCK_SIZE):
                if chunk:
                    file.write(chunk)
                    bytes_downloaded += len(chunk)

                if file_size > 0:
                    progress_percentage = (bytes_downloaded / file_size) * 100
                    print(f"Download progress: {progress_percentage:.2f}%")

        print(f"Download completed successfully. Total bytes: {bytes_downloaded}")
        
        # Verify the file was created and has content
        if os.path.exists(file_path):
            actual_size = os.path.getsize(file_path)
            print(f"File saved with size: {actual_size} bytes")
            if actual_size > 0:
                return True
            else:
                print("ERROR: Downloaded file is empty")
                return False
        else:
            print("ERROR: File was not created")
            return False

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response status code: {http_err.response.status_code}")
        print(f"Response headers: {dict(http_err.response.headers)}")
        if http_err.response.content:
            print(f"Response content: {http_err.response.content[:500]}")
        return False
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return False
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return False
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return False
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return False
