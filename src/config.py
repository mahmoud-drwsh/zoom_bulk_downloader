"""Zoom API configuration and credentials."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Zoom App Credentials (from marketplace.zoom.us) ===
# These should be set in your .env file or environment variables
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")

# Validate that all required credentials are set
if not CLIENT_ID:
    raise ValueError("ZOOM_CLIENT_ID environment variable is not set")
if not CLIENT_SECRET:
    raise ValueError("ZOOM_CLIENT_SECRET environment variable is not set")
if not ACCOUNT_ID:
    raise ValueError("ZOOM_ACCOUNT_ID environment variable is not set")

