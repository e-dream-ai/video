import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

session = requests.Session()
session.headers = {
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ADMIN_API_KEY}",
}
refresh_token = None


def load_api():
    global session
    login_user()
    session.hooks["response"].append(refresh_token_hook)


def get_session():
    global session
    return session


def get_backend_url():
    return BACKEND_URL


def set_token(token):
    global session
    if token:
        session.headers["Authorization"] = "Bearer " + token


def set_refresh_token(token):
    global refresh_token
    refresh_token = token


def get_refresh_token():
    global refresh_token
    return refresh_token


def login_user():
    global session

    try:
        res = session.post(
            "{}/auth/login".format(BACKEND_URL),
            json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        )
        json_response = res.json()
        access_token = json_response["data"]["token"]["AccessToken"]
        refresh_token = json_response["data"]["token"]["RefreshToken"]
        set_refresh_token(refresh_token)
        set_token(access_token)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def refresh_token_user():
    global session
    token = get_refresh_token()
    session.headers["Authorization"] = None

    try:
        res = session.post(
            "{}/auth/refresh".format(BACKEND_URL),
            json={"refreshToken": token},
        )
        json_response = res.json()
        access_token = json_response["data"]["AccessToken"]
        return access_token
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def refresh_token_hook(response, *args, **kwargs):
    global session
    if response.status_code == 401:
        new_access_token = refresh_token_user()
        original_request = response.request
        original_request.headers["Authorization"] = "Bearer " + new_access_token

        # Reissue the modified request
        new_response = session.send(original_request)

        # Set token to session
        set_token(new_access_token)

        # Return the new response
        return new_response

    # If the response doesn't require token refresh, return it as is
    return response


# if __name__ == "__main__":
#     load_api()
