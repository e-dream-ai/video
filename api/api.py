import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
session = requests.Session()
session.headers = {
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
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
        session.headers.update({"Authorization": f"Bearer {token}"})


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


def refresh_token_hook(r, *args, **kwargs):
    global session
    if r.status_code == 401:
        token = refresh_token_user()
        session.headers.update({"Authorization": f"Bearer {token}"})
        r.request.headers["Authorization"] = session.headers["Authorization"]
        return session.send(r.request, verify=False)


if __name__ == "__main__":
    load_api()
