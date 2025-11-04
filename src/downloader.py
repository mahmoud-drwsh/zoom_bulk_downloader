"""Video download functionality."""

import requests
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    downloads_dir = Path.home() / "Downloads"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_dir = downloads_dir / f"zoom_downloads_{timestamp}"
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
    
    # Create filename: topic_date_fileid.mp4
    safe_topic = sanitize_filename(topic)
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


def download_all_videos(video_urls, max_workers=5):
    """Download all videos in parallel.
    
    Args:
        video_urls: List of video info dictionaries
        max_workers: Number of parallel download threads
        
    Returns:
        Tuple of (successful_downloads, failed_downloads, download_dir)
    """
    if not video_urls:
        debug("No videos to download.")
        return ([], [], None)
    
    download_dir = get_download_directory()
    debug(f"Download directory: {download_dir}")
    
    successful = []
    failed = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_video = {
            executor.submit(download_video, video, download_dir): video
            for video in video_urls
        }
        
        for future in as_completed(future_to_video):
            video = future_to_video[future]
            try:
                success, filepath, error = future.result()
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

