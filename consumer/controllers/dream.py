import json
from requests import RequestException

# from typing import Optional
from client.api_client import ApiClient
from models.api_types import ApiResponse
from models.dream_types import Dream

from typing import Generic, Optional, TypeVar, Type, Dict, Any

# Generic type variable
T = TypeVar("T")

client = ApiClient()


def parse_response(data: dict, data_type: Type[T], nested_key: str) -> ApiResponse[T]:
    try:
        # Parse the nested object within the 'data' field using the provided nested_key
        if "data" in data and data["data"] is not None and nested_key in data["data"]:
            parsed_data = data_type(**data["data"][nested_key])
        else:
            parsed_data = None

        # Create ApiResponse with parsed data
        api_response = ApiResponse[T](
            success=data.get("success"), message=data.get("message"), data=parsed_data
        )
        return api_response
    except (TypeError, KeyError) as e:
        print(f"Error parsing response: {e}")
        return ApiResponse[T](success=False, message="Failed to parse response")


def get_dream(uuid: str) -> Optional[ApiResponse[Dream]]:
    try:
        response_data = client.get(f"/dream/{uuid}")
        print(response_data)
        api_response = parse_response(response_data, Dream, "dream")
        print(api_response)
        dream = api_response.data
        return api_response

    except RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
    except TypeError as e:
        print(f"Failed to parse response data: {e}")
