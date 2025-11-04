# Zoom Recording Downloader

A Python application that automatically discovers and downloads all Zoom recording videos from your Zoom account. It fetches recordings from all users across the past year and downloads them to your Downloads folder.

## Features

- 🔍 **Automatic Discovery**: Finds all Zoom recordings across all users in your account
- 📅 **Time Range**: Searches the past 12 months of recordings
- ⚡ **Parallel Processing**: Downloads multiple videos simultaneously for faster performance
- 🎥 **Multiple Files Per Meeting**: Handles meetings with multiple recording files (gallery view, speaker view, shared screen, etc.)
- 🔐 **Secure**: Uses environment variables for credentials (never hardcoded)
- 📁 **Organized**: Creates timestamped directories for each download session with descriptive filenames
- ✅ **Error Handling**: Retries failed downloads and provides detailed error reporting
- 📊 **Progress Tracking**: Shows download progress for large files

## Prerequisites

- Python 3.7 or higher
- A Zoom account with API access
- Zoom OAuth App credentials (Client ID, Client Secret, Account ID)

## Installation

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd zoom_downloader
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or if you're using `uv`:

```bash
uv pip install -r requirements.txt
```

## Configuration

### 1. Get Zoom API Credentials

1. Go to [Zoom Marketplace](https://marketplace.zoom.us/)
2. Create a Server-to-Server OAuth app
3. Note down your:
   - **Client ID**
   - **Client Secret**
   - **Account ID**

### 2. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
ZOOM_ACCOUNT_ID=your_account_id_here
```

**Important**: The `.env` file is already in `.gitignore` and will not be committed to version control.

## Usage

### Run the application

```bash
python main.py
```

Or if you're using `uv`:

```bash
uv run main.py
```

### What happens

1. **Authentication**: The app authenticates with Zoom using your credentials
2. **User Discovery**: Lists all users in your Zoom account
3. **Recording Discovery**: Fetches recordings for each user from the past 12 months
4. **URL Collection**: Collects all video download URLs
5. **Download**: Downloads all videos to `~/Downloads/zoom_downloads_{timestamp}/`

### Output

The application will:
- Display a list of all found videos with their metadata
- Save URLs to `urls.txt` (for reference)
- Download all videos to `~/Downloads/zoom_downloads_{timestamp}/`
- Show a summary of successful and failed downloads

Example output:
```
================================================================================
Total video URLs found: 38
================================================================================

URLs written to urls.txt

1. Team Meeting (2024-01-15)
   URL: https://...
   File ID: abc123, Size: 52428800 bytes, Duration: 45 minutes

...

================================================================================
Starting video downloads...
================================================================================

[DEBUG] Download directory: /Users/username/Downloads/zoom_downloads_20241104_090530
[DEBUG] ✓ Downloaded: Team Meeting (2024-01-15)
...

================================================================================
Download Summary
================================================================================
Successful downloads: 36
Failed downloads: 2
Download directory: /Users/username/Downloads/zoom_downloads_20241104_090530
================================================================================
```

## File Structure

```
zoom_downloader/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your credentials (not in git)
├── urls.txt               # Saved URLs (not in git)
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── auth.py            # Authentication handling
    ├── config.py          # Configuration management
    ├── api_client.py      # Zoom API client
    ├── video_urls.py      # Video URL extraction
    ├── downloader.py      # Download functionality
    ├── date_utils.py      # Date range utilities
    └── utils.py           # General utilities
```

## Configuration Options

### Download Settings

You can modify download behavior in `main.py`:

- **Parallel downloads**: Change `max_workers=5` in `download_all_videos()` call
- **User processing**: Change `max_workers=3` in the user processing executor

### Date Range

To change the time range of recordings, modify `get_month_ranges_for_past_year()` in `src/date_utils.py`. Currently set to the past 12 months.

### Multiple Files Per Meeting

Zoom meetings can have multiple recording files (e.g., gallery view, speaker view, shared screen with speaker view, etc.). The script automatically handles this by:

- Processing each file in the `recording_files` array separately
- Including the recording type in the filename (e.g., `Meeting_2024-01-15_gallery-view_abc123.mp4`)
- Using unique file IDs to ensure no conflicts between files from the same meeting

All MP4 video files from a meeting will be downloaded, with filenames that distinguish them by their recording type.

## Troubleshooting

### Error: Environment variable not set

**Solution**: Make sure your `.env` file exists and contains all three required variables:
- `ZOOM_CLIENT_ID`
- `ZOOM_CLIENT_SECRET`
- `ZOOM_ACCOUNT_ID`

### Error: Token request failed

**Possible causes**:
- Invalid credentials in `.env`
- Zoom API permissions not properly configured
- Network connectivity issues

**Solution**: Verify your credentials in the Zoom Marketplace and check your internet connection.

### Downloads fail with 401/403 errors

**Possible causes**:
- Access tokens expired
- Insufficient permissions on Zoom app
- Passcode-protected recordings

**Solution**: 
- Check Zoom app permissions in the Marketplace
- Ensure your app has access to recordings
- Some recordings may require manual download if they're protected

### Files not downloading

**Check**:
- Disk space in your Downloads folder
- File permissions
- Network connectivity
- Check the error messages in the output

### Slow downloads

**Optimization**:
- Increase `max_workers` in `download_all_videos()` (be careful not to overwhelm Zoom's servers)
- Check your internet connection speed
- Large files will take time to download

## Security Notes

- ✅ Credentials are stored in `.env` (not committed to git)
- ✅ `.env` file is in `.gitignore`
- ✅ `urls.txt` contains sensitive URLs and is also ignored
- ✅ No credentials are hardcoded in the source code

**Important**: If you've ever committed credentials to git, rotate them immediately in the Zoom Marketplace.

## Requirements

- `requests` - HTTP library for API calls and downloads
- `python-dateutil` - Date manipulation utilities
- `python-dotenv` - Environment variable management

## License

This project is provided as-is for personal or educational use.

## Contributing

Feel free to submit issues or pull requests for improvements.

## Support

For issues related to:
- **Zoom API**: Check [Zoom Developer Documentation](https://developers.zoom.us/)
- **Application bugs**: Open an issue in this repository
- **Configuration**: Review the Configuration section above

