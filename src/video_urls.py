"""Video URL extraction and listing functionality."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from .api_client import list_all_recordings
from .date_utils import get_month_ranges_for_past_year
from .utils import debug


def _fetch_recordings_for_month(access_token, user_id, user_email, from_date, to_date):
    """Fetch recordings for a specific month range."""
    debug(f"Checking {user_email}: {from_date} to {to_date}")
    return list_all_recordings(access_token, user_id, from_date, to_date)


def list_video_urls_for_user(access_token, user, max_workers=6):
    """List all video download URLs for a user across the past year.
    
    Args:
        access_token: Zoom API access token
        user: User dictionary with email and id
        max_workers: Number of parallel threads for fetching recordings
    """
    user_email = user["email"]
    user_id = user["id"]
    month_ranges = get_month_ranges_for_past_year()
    
    all_recordings = []
    # Fetch recordings for all months in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_range = {
            executor.submit(
                _fetch_recordings_for_month,
                access_token,
                user_id,
                user_email,
                from_date,
                to_date
            ): (from_date, to_date)
            for from_date, to_date in month_ranges
        }
        
        for future in as_completed(future_to_range):
            from_date, to_date = future_to_range[future]
            try:
                recordings = future.result()
                all_recordings.extend(recordings)
            except Exception as exc:
                debug(f"Error fetching recordings for {user_email} ({from_date} to {to_date}): {exc}")
    
    debug(f"{user_email}: {len(all_recordings)} total recordings found.")
    
    video_urls = []
    for rec in all_recordings:
        topic = rec.get("topic", "Untitled")
        date = rec.get("start_time", "unknown_date").split("T")[0]
        # Check for passcode in various possible field names
        passcode = rec.get("recording_play_passcode") or rec.get("password") or rec.get("passcode") or ""
        
        for f in rec.get("recording_files", []):
            file_type = f.get("file_type", "").lower()
            if file_type != "mp4":  # only keep video
                continue
            
            download_url = f.get("download_url")
            if not download_url:
                continue
            
            # Append access token and passcode to the download URL
            parsed_url = urlparse(download_url)
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            
            # Add access token (required for authentication)
            query_params["access_token"] = [access_token]
            
            # Add passcode if available
            if passcode:
                query_params["passcode"] = [passcode]
            
            # Reconstruct URL with access token and passcode
            new_query = urlencode(query_params, doseq=True)
            authenticated_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            video_urls.append({
                "url": authenticated_url,
                "topic": topic,
                "date": date,
                "file_id": f.get("id", "unknown"),
                "file_size": f.get("file_size", 0),
                "duration": rec.get("duration", 0)
            })
    
    return video_urls

