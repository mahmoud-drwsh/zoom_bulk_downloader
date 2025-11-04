"""Authentication and token management."""

import base64
import requests
from .config import CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID


def get_access_token():
    """Generate OAuth access token."""
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(url, headers={"Authorization": f"Basic {auth_header}"})
    if resp.status_code != 200:
        raise Exception(f"Token request failed: {resp.status_code} - {resp.text}")
    return resp.json()["access_token"]

