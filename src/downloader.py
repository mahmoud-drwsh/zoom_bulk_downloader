"""Video download functionality."""

import requests
from pathlib import Path
from datetime import datetime
from .utils import debug


def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters."""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def get_download_directory():
    """Create and return the download directory path."""
    download_dir = Path.home() / "Videos" / "raw"
    download_dir.mkdir(parents=True, exist_ok=True)
    return download_dir


def download_video(video_info, download_dir, max_retries=3):
    """Download a single video file.
    
    Args:
        video_info: Dictionary with 'url', 'topic', 'date', 'file_id', etc.
        download_dir: Path to the download directory
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (success: bool, filepath: str or None, error: str or None)
    """
    url = video_info['url']
    topic = video_info.get('topic', 'Untitled')
    date = video_info.get('date', 'unknown_date')
    file_id = video_info.get('file_id', 'unknown')
    recording_type = video_info.get('recording_type', '')
    
    # Create filename: topic_date_[recording_type_]fileid.mp4
    # If multiple files exist for the same meeting, recording_type helps distinguish them
    safe_topic = sanitize_filename(topic)
    if recording_type:
        # Sanitize recording type and add to filename
        safe_recording_type = sanitize_filename(recording_type).replace('_', '-')
        filename = f"{safe_topic}_{date}_{safe_recording_type}_{file_id}.mp4"
    else:
        filename = f"{safe_topic}_{date}_{file_id}.mp4"
    filepath = download_dir / filename
    
    # Skip if file already exists
    if filepath.exists():
        return (True, str(filepath), None)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            file_size = video_info.get('file_size', 0)
            expected_size = file_size if file_size > 0 else total_size
            
            # Download with progress
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress for large files
                        if expected_size > 0 and downloaded % (10 * 1024 * 1024) == 0:
                            percent = (downloaded / expected_size) * 100
                            debug(f"Downloading {filename}: {percent:.1f}% ({downloaded}/{expected_size} bytes)")
            
            # Verify file was downloaded completely
            actual_size = filepath.stat().st_size
            if expected_size > 0 and actual_size < expected_size * 0.9:
                raise Exception(f"Download incomplete: {actual_size} < {expected_size}")
            
            return (True, str(filepath), None)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error on attempt {attempt + 1}/{max_retries}: {str(e)}"
            if attempt < max_retries - 1:
                debug(error_msg)
            else:
                return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Error downloading {filename}: {str(e)}"
            if filepath.exists():
                filepath.unlink()  # Remove incomplete file
            return (False, None, error_msg)
    
    return (False, None, "Max retries exceeded")


def download_all_videos(video_urls, max_workers=None):
    """Download all videos sequentially (one at a time), starting with the latest meeting.
    
    Args:
        video_urls: List of video info dictionaries
        max_workers: Deprecated parameter (kept for backward compatibility, ignored)
        
    Returns:
        Tuple of (successful_downloads, failed_downloads, download_dir)
    """
    if not video_urls:
        debug("No videos to download.")
        return ([], [], None)
    
    download_dir = get_download_directory()
    debug(f"Download directory: {download_dir}")
    
    # Sort videos by date (newest first) before downloading
    def get_sort_key(video):
        """Extract date for sorting, handling various date formats."""
        date_str = video.get('date', 'unknown_date')
        if date_str == 'unknown_date':
            # Put unknown dates at the end
            return datetime.min.date()
        try:
            # Parse date string in format YYYY-MM-DD
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # If date can't be parsed, put at the end
            return datetime.min.date()
    
    # Sort by date descending (newest first)
    sorted_videos = sorted(video_urls, key=get_sort_key, reverse=True)
    debug(f"Sorted {len(sorted_videos)} videos by date (newest first)")
    
    successful = []
    failed = []
    
    # Download videos sequentially (one at a time), starting with the latest
    for video in sorted_videos:
        try:
            success, filepath, error = download_video(video, download_dir)
            if success:
                successful.append((video, filepath))
                debug(f"✓ Downloaded: {video.get('topic', 'Unknown')} ({video.get('date', 'unknown')})")
            else:
                failed.append((video, error))
                debug(f"✗ Failed: {video.get('topic', 'Unknown')} - {error}")
        except Exception as exc:
            failed.append((video, str(exc)))
            debug(f"✗ Exception downloading {video.get('topic', 'Unknown')}: {exc}")
    
    return (successful, failed, download_dir)

