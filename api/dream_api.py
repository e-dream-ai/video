import requests
from api.api import get_session, get_backend_url, load_api

load_api()
BACKEND_URL = get_backend_url()


def set_dream_processing(uuid):
    session = get_session()
    try:
        session.post(
            "{}/dream/{}/status/processing".format(BACKEND_URL, uuid),
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def set_dream_processed(uuid):
    session = get_session()
    print(session.headers)
    try:
        session.post(
            "{}/dream/{}/status/processed".format(BACKEND_URL, uuid),
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def set_dream_failed(uuid):
    session = get_session()
    print(session.headers)
    try:
        session.post(
            "{}/dream/{}/status/failed".format(BACKEND_URL, uuid),
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
