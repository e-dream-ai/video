from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


# Decorator to verify apikey
def api_key_required(f):
    def decorator(*args, **kwargs):
        # get apikey from headers
        auth_header = request.headers.get("Authorization")

        # verify if header is present and follows `Bearer <token>` format
        if auth_header and auth_header.startswith("Api-Key "):
            apikey = auth_header[len("Api-Key ") :]

            # compare request apikey with env API_KEY
            if apikey == API_KEY:
                return f(*args, **kwargs)

        # if authentication fails returns error
        return jsonify({"error": "Unauthorized"}), 401

    return decorator
