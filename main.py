"""Main entry point for Zoom recording URL listing and downloading."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from src.auth import get_access_token
from src.api_client import list_users
from src.video_urls import list_video_urls_for_user
from src.downloader import download_all_videos
from src.utils import debug


def main():
    """Main function to list all video URLs for all users."""
    access_token = get_access_token()
    users = list_users(access_token)
    
    all_video_urls = []
    # Process users in parallel (each user's months are already parallelized)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_user = {
            executor.submit(list_video_urls_for_user, access_token, user): user
            for user in users
        }
        
        for future in as_completed(future_to_user):
            user = future_to_user[future]
            try:
                video_urls = future.result()
                all_video_urls.extend(video_urls)
                debug(f"Completed processing for {user['email']}: {len(video_urls)} videos found")
            except Exception as exc:
                debug(f"Error processing user {user.get('email', 'unknown')}: {exc}")
    
    # Print all video URLs
    print("\n" + "="*80)
    print(f"Total video URLs found: {len(all_video_urls)}")
    print("="*80 + "\n")
    
    # Write URLs to file
    with open("urls.txt", "w") as f:
        for video in all_video_urls:
            f.write(f"{video['url']}\n")
    
    print(f"URLs written to urls.txt\n")
    
    for idx, video in enumerate(all_video_urls, 1):
        recording_type = video.get('recording_type', '')
        type_info = f" ({recording_type})" if recording_type else ""
        print(f"{idx}. {video['topic']} ({video['date']}){type_info}")
        print(f"   URL: {video['url']}")
        print(f"   File ID: {video['file_id']}, Size: {video['file_size']} bytes, Duration: {video['duration']} minutes")
        print()
    
    # Download all videos
    if all_video_urls:
        print("\n" + "="*80)
        print("Starting video downloads...")
        print("="*80 + "\n")
        
        successful, failed, download_dir = download_all_videos(all_video_urls, max_workers=5)
        
        print("\n" + "="*80)
        print("Download Summary")
        print("="*80)
        print(f"Successful downloads: {len(successful)}")
        print(f"Failed downloads: {len(failed)}")
        print(f"Download directory: {download_dir}")
        print("="*80 + "\n")
        
        if failed:
            print("Failed downloads:")
            for video, error in failed:
                print(f"  - {video.get('topic', 'Unknown')} ({video.get('date', 'unknown')}): {error}")
            print()
    else:
        print("No videos to download.\n")


if __name__ == "__main__":
    main()

