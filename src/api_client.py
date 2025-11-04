"""Zoom API client for fetching users and recordings."""

import requests
from .utils import debug


def list_users(access_token):
    """List all users in the Zoom account."""
    resp = requests.get(
        "https://api.zoom.us/v2/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    users = resp.json().get("users", [])
    debug(f"Found {len(users)} users.")
    return users


def list_all_recordings(access_token, user_id, from_date, to_date):
    """List all recordings for a user within a date range."""
    url = f"https://api.zoom.us/v2/users/{user_id}/recordings"
    headers = {"Authorization": f"Bearer {access_token}"}
    recordings = []
    next_page_token = None

    while True:
        params = {"page_size": 100, "from": from_date, "to": to_date}
        if next_page_token:
            params["next_page_token"] = next_page_token
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            debug(f"Failed to get recordings for {user_id} ({from_date} to {to_date}): {resp.text}")
            break
        data = resp.json()
        recordings.extend(data.get("meetings", []))
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
    return recordings

