JOHTML-PYTHON Search / Media Gallery V4+
A powerful, feature-rich web application that combines media gallery management with search capabilities, YouTube integration, and customizable display options. Built with FastAPI backend and modern frontend technologies.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Backend Functions](#backend-functions)
- [Frontend Functions](#frontend-functions)
- [API Endpoints](#api-endpoints)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Testing](#testing)
- [Support](#support)
- [Overview](#overview)




JOHTML Search/Media Gallery V4+ is a comprehensive media management system that allows users to:

Upload and manage images, audio, and video files
Search and display Google search results
Integrate YouTube video playback
Customize gallery appearance and behavior
Manage media items through an intuitive interface
Features
Core Features
Multi-format Media Support: Images, audio files, video files, YouTube videos
Google Search Integration: Convert search queries to clickable result links
Local File Upload: Support for uploading local media files
Dual Gallery Display: Main page gallery and modal gallery view
Customizable UI: Change colors, enlarge modes, and display settings
Media Types Supported
Type	Formats
Images	JPG, JPEG, PNG, GIF, WEBP
Audio	MP3, WAV, OGG, M4A
Video	MP4, WEBM, MOV
External	YouTube, Google Search, Direct Links
Architecture
Technology Stack
Backend: FastAPI (Python) Frontend: HTML5, CSS3, JavaScript Libraries: Bootstrap 5, TailwindCSS, Font Awesome, YouTube IFrame API Server: Uvicorn (ASGI)

text

Project Structure
johtml-media-gallery/ +-- app.py # Single-file FastAPI application +-- requirements.txt # Python dependencies +-- README.md # Documentation

text

Installation
Prerequisites
Python 3.8 or higher
pip package manager
Step-by-Step Installation
Clone or create the project directory
mkdir johtml-media-gallery
cd johtml-media-gallery
Create the application file

bash
# Create app.py with the provided code
touch app.py
Install dependencies

bash
pip install fastapi uvicorn
Run the application

bash
python app.py
# OR
uvicorn app:app --reload --host 0.0.0.0 --port 8000
Access the application
Open your browser and navigate to: http://localhost:8000


## backend-functions
Core FastAPI Functions
root(request: Request) -> HTMLResponse
Purpose: Main entry point that serves the complete HTML application
Returns: Complete HTML document as HTMLResponse
Endpoint: GET /

python
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serves the main media gallery interface"""
    html_content = generate_html()
    return HTMLResponse(content=html_content)
health_check() -> JSONResponse
Purpose: Health monitoring endpoint for the application
Returns: Status, service name, and version information
Endpoint: GET /health

python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JOHTML Search / Media Gallery V4+",
        "version": "4.0.0"
    }
add_item(item: MediaItem) -> JSONResponse
Purpose: Adds a new media item to the collection
Parameters:

item: MediaItem object containing URL, title, and type
Returns: Success status, added item, and total count
Endpoint: POST /api/items/add

python
@app.post("/api/items/add")
async def add_item(item: MediaItem):
    """Adds single or multiple media items to the gallery"""
generate_gallery(items: List[str]) -> JSONResponse
Purpose: Creates a gallery from a list of item URLs
Parameters:

items: List of URL strings
Returns: Generated gallery items with success message
Endpoint: POST /api/gallery/generate

python
@app.post("/api/gallery/generate")
async def generate_gallery(items: List[str]):
    """Processes URLs and generates gallery structure"""
get_gallery_items() -> JSONResponse
Purpose: Retrieves all current gallery items
Returns: List of gallery items with count
Endpoint: GET /api/gallery/items

python
@app.get("/api/gallery/items")
async def get_gallery_items():
    """Returns all items currently in the gallery"""
extract_youtube_id(request: YouTubeRequest) -> JSONResponse
Purpose: Extracts video ID from YouTube URLs
Parameters:

request: Contains YouTube URL and volume preference
Returns: Video ID, embed URL, and thumbnail URL
Endpoint: POST /api/youtube/extract

python
@app.post("/api/youtube/extract")
async def extract_youtube_id(request: YouTubeRequest):
    """Parses various YouTube URL formats"""
update_settings(settings: Settings) -> JSONResponse
Purpose: Updates application-wide settings
Parameters:

settings: Settings object with colors and mode preferences
Returns: Updated settings confirmation
Endpoint: POST /api/settings/update

python
@app.post("/api/settings/update")
async def update_settings(settings: Settings):
    """Saves user preferences for gallery display"""
get_settings() -> JSONResponse
Purpose: Retrieves current application settings
Returns: Current settings configuration
Endpoint: GET /api/settings/get

python
@app.get("/api/settings/get")
async def get_settings():
    """Returns current gallery configuration"""
google_search(query: str) -> JSONResponse
Purpose: Creates Google search URL from query string
Parameters:

query: Search query string
Returns: Encoded search URL
Endpoint: POST /api/search/google

python
@app.post("/api/search/google")
async def google_search(query: str):
    """Generates Google search URL for the given query"""
clear_gallery() -> JSONResponse
Purpose: Removes all items from the gallery
Returns: Confirmation of gallery clearance
Endpoint: POST /api/clear/gallery

python
@app.post("/api/clear/gallery")
async def clear_gallery():
    """Empties the current gallery collection"""
Helper Functions
detect_media_type(url: str) -> str
Purpose: Identifies media type from URL extension or pattern
Returns: String: 'image', 'audio', 'video', 'google', 'youtube', or 'link'

python
def detect_media_type(url: str) -> str:
    """Uses regex patterns to detect file types and special URLs"""
Detection Patterns:

Images: \.(jpg|jpeg|png|gif|webp|bmp|svg)$

Audio: \.(mp3|wav|ogg|m4a|flac|aac)$

Video: \.(mp4|webm|mov|avi|mkv|flv)$

YouTube: Contains 'youtube.com' or 'youtu.be'

Google: Contains 'google.com/search'

extract_youtube_id_from_url(url: str) -> str
Purpose: Parses various YouTube URL formats to extract video ID
Returns: Video ID string or empty string if invalid

python
def extract_youtube_id_from_url(url: str) -> str:
    """Handles youtu.be, youtube.com/watch, /embed/, and /shorts/ formats"""
Supported URL Formats:

https://youtu.be/VIDEO_ID

https://www.youtube.com/watch?v=VIDEO_ID

https://www.youtube.com/embed/VIDEO_ID

https://www.youtube.com/shorts/VIDEO_ID

generate_html() -> str
Purpose: Creates complete HTML document as string
Returns: Full HTML page with embedded CSS, JavaScript, and structure

python
def generate_html() -> str:
    """Returns the complete frontend application code"""

## Frontend Functions
Gallery Management Functions
generateGallery() -> void
Purpose: Creates gallery from selected items and input text
Process:

Collects selected items from SELECT_BOX

Processes input text for additional items

Generates gallery structure

Renders display

displaySelected() -> void
Purpose: Displays only currently selected items
Process:

Gets selected items from SELECT_BOX

Sets gallery to selected items only

Renders updated display

renderGallery() -> void
Purpose: Renders gallery items in both main and modal displays
Process:

Clears existing gallery strips

Creates gallery items with appropriate media players

Attaches event handlers for click/hover

Applies current enlarge mode settings

Media Type Handlers
getType(src: str) -> str
Purpose: Determines media type from URL
Returns: Media type classification

javascript
function getType(src) {
    // Checks file extensions and URL patterns
    // Returns: 'image', 'audio', 'video', 'google', 'local', 'youtube', or 'link'
}
show(i: int) -> void
Purpose: Displays specific gallery item in main display
Parameters:

i: Index of item to display
Features:

Renders appropriate player for media type

Handles images, audio players, video players

Creates links for external content

openImagePopup(item: object, i: int) -> void
Purpose: Opens enlarged view of image/video in popup
Parameters:

item: Gallery item object

i: Index position
Features:

Supports images and videos

Maintains aspect ratio

Includes navigation controls

Navigation Functions
next() -> void
Purpose: Navigates to next gallery item
Process: Cycles forward through gallery items (wrap-around)

prev() -> void
Purpose: Navigates to previous gallery item
Process: Cycles backward through gallery items (wrap-around)

popupNext(event) -> void
Purpose: Navigates to next item in popup view
Parameters:

event: Mouse event for propagation control

popupPrev(event) -> void
Purpose: Navigates to previous item in popup view
Parameters:

event: Mouse event for propagation control

List Management Functions
refresh() -> void
Purpose: Updates SELECT_BOX and editable list from items array
Process:

Removes duplicate items

Rebuilds SELECT_BOX options

Updates editable textarea

Maintains SELECT_ALL control

updateSelect() -> void
Purpose: Synchronizes SELECT_BOX with editable list content
Process:

Parses textarea content

Creates items array

Ensures SELECT_ALL presence

Refreshes display

selectAll() -> void
Purpose: Selects all items in SELECT_BOX
Effect: Highlights all options in the multi-select box

selectedItems() -> array
Purpose: Returns array of currently selected items
Returns: Filtered items excluding SELECT_ALL control

javascript
function selectedItems() {
    return [...selectBox.selectedOptions]
        .map(o => items[Number(o.value)])
        .filter(x => x && x.src !== "SELECT_ALL");
}
Input Handlers
loadLocalFiles() -> void
Purpose: Loads locally selected files into gallery
Process:

Reads files from file input

Creates object URLs

Detects media types

Adds to items array

Refreshes display

addUrlPath() -> void
Purpose: Adds single URL to items list
Process:

Gets URL from input field

Creates media item

Adds to items array

Refreshes display

loadGoogleSearch() -> void
Purpose: Processes Google search queries
Process:

Reads search queries from textarea

Calls backend API for each query

Adds search result links to items

Updates display

Audio Controls
playMusic() -> void
Purpose: Plays background music audio
Effect: Starts playback of loaded audio file

pauseMusic() -> void
Purpose: Pauses background music
Effect: Stops current audio playback

fastForwardMusic() -> void
Purpose: Skips forward 10 seconds in audio
Effect: Advances current playback position by 10 seconds

fastRewindMusic() -> void
Purpose: Skips backward 10 seconds in audio
Effect: Rewinds playback position by 10 seconds

volumeUp() -> void
Purpose: Increases audio volume
Effect: Increments volume by 0.1 (max 1.0)

volumeDown() -> void
Purpose: Decreases audio volume
Effect: Decrements volume by 0.1 (min 0.0)

YouTube Controls
loadYouTubeVideo() -> void
Purpose: Loads YouTube video from URL
Process:

Extracts video ID from URL

Initializes or updates YouTube player

Sets volume level

Starts video playback

youtubePlay() -> void
Purpose: Plays loaded YouTube video
Effect: Resumes video playback

youtubePause() -> void
Purpose: Pauses YouTube video
Effect: Stops current video playback

youtubeRewind() -> void
Purpose: Rewinds YouTube video by 10 seconds
Effect: Decreases current time position

youtubeForward() -> void
Purpose: Fast forwards YouTube video by 10 seconds
Effect: Increases current time position

youtubeVolumeUp() -> void
Purpose: Increases YouTube volume by 10%
Effect: Increments volume level (max 100)

youtubeVolumeDown() -> void
Purpose: Decreases YouTube volume by 10%
Effect: Decrements volume level (min 0)

UI Control Functions
changeGalleryBackground(colour: string) -> void
Purpose: Changes gallery background color
Parameters:

colour: Hex color code (e.g., '#000000')
Effect: Updates CSS custom property --gallery-bg

changeEnlargeMode(mode: string) -> void
Purpose: Changes image enlarge behavior
Parameters:

mode: 'hover' or 'click'
Effect:

Hover: Enlarges on mouse-over

Click: Enlarges only on click

Toggles body class 'hover-enlarge'

changeDetailColour(colour: string) -> void
Purpose: Changes accent color throughout interface
Parameters:

colour: Hex color code
Effect: Updates CSS variables --green and --green2

maxModal() -> void
Purpose: Maximizes gallery modal to full screen
Effect: Adds 'modal-max' class to dialog

minModal() -> void
Purpose: Minimizes gallery modal to small size
Effect: Removes 'modal-max', adds 'modal-min'

clearGallery() -> void
Purpose: Clears all items from gallery display
Process:

Empties gallery array

Clears gallery strips

Resets main display

Shows clearance message

Popup Control Functions
popupMin(event) -> void
Purpose: Minimizes image popup window
Effect: Adds 'minimized' class, removes 'maximized'

popupMax(event) -> void
Purpose: Maximizes image popup window
Effect: Adds 'maximized' class, removes 'minimized'

closeImagePopup(event) -> void
Purpose: Closes the image popup overlay
Effect: Hides popup and clears content

## API Endpoints
Method	Endpoint	Description	Request Body	Response
GET	/	Main application page	None	HTML Document
GET	/health	Health check	None	Status object
POST	/api/items/add	Add media item	{url, title, type}	Success status
POST	/api/gallery/generate	Generate gallery	["url1", "url2"]	Gallery items
GET	/api/gallery/items	Get gallery items	None	Item list
POST	/api/youtube/extract	Extract YouTube ID	{url, volume}	Video metadata
POST	/api/settings/update	Update settings	{settings object}	Updated config
GET	/api/settings/get	Get settings	None	Current config
POST	/api/search/google	Google search	query string	Search URL
POST	/api/clear/gallery	Clear gallery	None	Confirmation

## Usage Guide
Quick Start Tutorial
Adding Media Items

javascript
// Method 1: URL Input
- Enter URL in URL_PATH field
- Click "Add URL_PATH"

// Method 2: Text Input
- Enter URLs in INPUT_TEXT (one per line)
- Click "GENERATE"

// Method 3: Local Files
- Select files using LOCAL_PATH input
- Click "Load Local Files"
Managing Gallery Items

text
- Use SELECT_BOX to choose items
- Click SELECT_ALL for all items
- Use editable list to bulk edit URLs
- Click UPDATE LIST to apply changes
Google Search Integration

text
- Enter search queries in Google Search section
- One query per line
- Click "Load Google Search"
- Results appear as clickable links
YouTube Integration

text
- Open SETTINGS modal
- Paste YouTube URL
- Click "LOAD YOUTUBE"
- Use playback controls
Customizing Display

text
- Open SETTINGS modal
- Change gallery background color
- Adjust detail (accent) color
- Switch between hover/click enlarge modes
Example Workflows
Creating a Media Presentation:

markdown
1. Load 5 images from local files
2. Add 3 YouTube video URLs
3. Add background music MP3
4. Generate gallery
5. Use PREV/NEXT to present
6. Enable hover mode for quick previews
Building a Search Results Gallery:

markdown
1. Enter 4 search queries in Google Search section
2. Click "Load Google Search"
3. Select all results
4. Click "DISPLAY SELECTED"
5. Save gallery as editable list


## Configuration
Settings Object Structure
javascript
{
    galleryBgColor: "#000000",  // Background color (hex)
    detailColor: "#00ff66",     // Accent color (hex)
    enlargeMode: "hover"        // Display mode: 'hover' or 'click'
}
CSS Custom Properties
css
:root {
    --green: #00ff66;      /* Primary accent color */
    --green2: #39ff88;     /* Secondary accent color */
    --black: #000;         /* Background color */
    --dark: #050505;       /* Dark surface color */
    --gallery-bg: #000000; /* Gallery background */
}


## Troubleshooting
Common Issues and Solutions
Issue	Possible Cause	Solution
Gallery not displaying	No items selected	Select items or generate gallery first
YouTube videos not loading	Invalid URL format	Use standard YouTube URL format
Local files not showing	Browser security	Allow file access permissions
Audio not playing	Autoplay blocked	User must initiate playback
Colors not changing	CSS variable scope	Refresh page after changes
Google Search failing	Network issue	Check internet connection
Popup not enlarging	CSS class conflict	Clear browser cache
Debug Mode
Enable debug logging in browser console:

javascript
localStorage.setItem('debug', 'true');
location.reload();
Performance Optimization
Limit gallery to 50 items for optimal performance

Use compressed images (< 2MB each)

Clear gallery periodically to free memory

Use local files instead of external URLs when possible

## Development
Extending the Application
Adding New Media Types:

Update detect_media_type() function

Add type pattern in getType()

Add rendering case in renderGallery()

Add display case in show()

Creating Custom Themes:

css
/* Add new theme variables */
:root {
    --theme-primary: #your-color;
    --theme-secondary: #your-color;
}
Adding Keyboard Shortcuts:

javascript
document.addEventListener('keydown', (e) => {
    if(e.key === 'ArrowRight') next();
    if(e.key === 'ArrowLeft') prev();
    if(e.key === 'Escape') closeImagePopup();
});
API Extension Example
python
@app.post("/api/export/gallery")
async def export_gallery():
    """Export gallery as JSON file"""
    return JSONResponse({
        "gallery": session_data["gallery"],
        "settings": session_data["settings"]
    })

## Testing
bash
# Test health endpoint
curl http://localhost:8000/health

# Test gallery generation
curl -X POST http://localhost:8000/api/gallery/generate \
  -H "Content-Type: application/json" \
  -d '["https://example.com/image.jpg"]'
Security Considerations
All file processing occurs client-side

No file storage on server

CORS configured for external API access

Input sanitization for URL inputs

HTTPS recommended for production

License
This project is open source and available for personal and commercial use.

## Support
For issues or questions:

Check the troubleshooting guide

Enable debug mode for detailed logs

Contact: https://raiiarcomio.com

Version History
V4.0.0 (Current): FastAPI backend, improved performance

V3.0.0: Added YouTube integration

V2.0.0: Added Google Search support

V1.0.0: Initial release with basic gallery

Created by Julius Olatokunbo | Another Website

text

This comprehensive README provides complete documentation for all functions in 
the JOHTML-PYTHON Search/Media Gallery V4+ application, 
including backend API endpoints, frontend JavaScript functions, usage examples, 
and troubleshooting guides.
