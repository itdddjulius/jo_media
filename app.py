from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import re
from urllib.parse import urlparse, quote

app = FastAPI(
    title="JOHTML Search / Media Gallery V4+",
    description="A powerful media gallery with search capabilities, YouTube integration, and customizable display options",
    version="4.0.0"
)

# Configure CORS for external API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (if needed for additional assets)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Templates (we'll use inline HTML for single-file solution)
templates = Jinja2Templates(directory="templates")

# Data models
class GalleryItem(BaseModel):
    src: str
    label: str
    type: str

class MediaItem(BaseModel):
    url: str
    title: Optional[str] = None
    media_type: Optional[str] = None

class YouTubeRequest(BaseModel):
    url: str
    volume: Optional[int] = 50

class Settings(BaseModel):
    galleryBgColor: str = "#000000"
    detailColor: str = "#00ff66"
    enlargeMode: str = "hover"

# In-memory storage for session data (in production, use a database)
session_data = {
    "items": [],
    "gallery": [],
    "settings": Settings()
}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main application page"""
    html_content = generate_html()
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "JOHTML Search / Media Gallery V4+",
        "version": "4.0.0"
    }

@app.post("/api/items/add")
async def add_item(item: MediaItem):
    """Add a new media item to the collection"""
    if not item.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    media_type = item.media_type or detect_media_type(item.url)
    
    new_item = {
        "src": item.url,
        "label": item.title or item.url,
        "type": media_type
    }
    
    session_data["items"].append(new_item)
    
    return JSONResponse({
        "success": True,
        "message": "Item added successfully",
        "item": new_item,
        "total": len(session_data["items"])
    })

@app.post("/api/gallery/generate")
async def generate_gallery(items: List[str]):
    """Generate gallery from provided items"""
    gallery_items = []
    
    for item_url in items:
        if item_url and item_url != "SELECT_ALL":
            media_type = detect_media_type(item_url)
            gallery_items.append({
                "src": item_url,
                "label": item_url,
                "type": media_type
            })
    
    session_data["gallery"] = gallery_items
    
    return JSONResponse({
        "success": True,
        "message": f"Gallery generated with {len(gallery_items)} items",
        "items": gallery_items
    })

@app.get("/api/gallery/items")
async def get_gallery_items():
    """Get current gallery items"""
    return JSONResponse({
        "success": True,
        "items": session_data["gallery"],
        "count": len(session_data["gallery"])
    })

@app.post("/api/youtube/extract")
async def extract_youtube_id(request: YouTubeRequest):
    """Extract YouTube video ID from URL"""
    video_id = extract_youtube_id_from_url(request.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    return JSONResponse({
        "success": True,
        "videoId": video_id,
        "embedUrl": f"https://www.youtube.com/embed/{video_id}",
        "thumbnailUrl": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    })

@app.post("/api/settings/update")
async def update_settings(settings: Settings):
    """Update application settings"""
    session_data["settings"] = settings
    
    return JSONResponse({
        "success": True,
        "message": "Settings updated successfully",
        "settings": settings.dict()
    })

@app.get("/api/settings/get")
async def get_settings():
    """Get current application settings"""
    return JSONResponse({
        "success": True,
        "settings": session_data["settings"].dict()
    })

@app.post("/api/search/google")
async def google_search(query: str):
    """Perform Google search and return results"""
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")
    
    encoded_query = quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    return JSONResponse({
        "success": True,
        "query": query,
        "searchUrl": search_url,
        "message": "Search URL generated successfully"
    })

@app.post("/api/clear/gallery")
async def clear_gallery():
    """Clear all gallery items"""
    session_data["gallery"] = []
    
    return JSONResponse({
        "success": True,
        "message": "Gallery cleared successfully"
    })

# Helper functions
def detect_media_type(url: str) -> str:
    """Detect media type from URL"""
    url_lower = url.lower()
    
    # Check for image extensions
    if re.search(r'\.(jpg|jpeg|png|gif|webp|bmp|svg)$', url_lower):
        return "image"
    
    # Check for audio extensions
    if re.search(r'\.(mp3|wav|ogg|m4a|flac|aac)$', url_lower):
        return "audio"
    
    # Check for video extensions
    if re.search(r'\.(mp4|webm|mov|avi|mkv|flv)$', url_lower):
        return "video"
    
    # Check for Google search
    if "google.com/search" in url_lower:
        return "google"
    
    # YouTube URLs
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    
    # Default to link
    return "link"

def extract_youtube_id_from_url(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    try:
        parsed = urlparse(url)
        
        # Handle youtu.be format
        if "youtu.be" in parsed.netloc:
            return parsed.path.strip("/")
        
        # Handle youtube.com formats
        if "youtube.com" in parsed.netloc:
            # Standard watch URL
            if "watch" in parsed.path:
                query_params = dict(pair.split("=") for pair in parsed.query.split("&") if "=" in pair)
                return query_params.get("v", "")
            
            # Embed URL
            if "/embed/" in parsed.path:
                return parsed.path.split("/embed/")[1].split("/")[0]
            
            # Shorts URL
            if "/shorts/" in parsed.path:
                return parsed.path.split("/shorts/")[1].split("/")[0]
        
        return ""
    except:
        return ""

def generate_html() -> str:
    """Generate the complete HTML content"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JOHTML Search / Media Gallery V4+</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://www.youtube.com/iframe_api"></script>

<style>
:root {
  --green:#00ff66;
  --green2:#39ff88;
  --black:#000;
  --dark:#050505;
  --gallery-bg:#000000;
}

body {
  background:#000;
  color:#fff;
  padding-bottom:150px;
}

a,h1,h2,h3,h4,h5,p,label,small {
  color:#fff!important;
}

.text-success,
nav a,
footer a {
  color:var(--green)!important;
}

.btn-green {
  background:var(--green);
  color:#000;
  font-weight:900;
  border:2px solid var(--green);
  box-shadow:0 0 14px var(--green);
}

.btn-green:hover {
  background:var(--green2);
  color:#000;
}

.form-control,
.form-select {
  background:#111!important;
  color:#fff!important;
  border:2px solid var(--green)!important;
}

.card,
.modal-content {
  background:var(--dark);
  border:2px solid var(--green);
  color:#fff;
}

.gallery-area {
  background:var(--gallery-bg);
  border:2px solid var(--green);
  border-radius:16px;
  padding:18px;
}

.gallery-strip {
  display:flex;
  gap:16px;
  overflow-x:auto;
  padding:16px 4px;
}

.gallery-item {
  min-width:270px;
  height:190px;
  border:2px solid var(--green);
  border-radius:14px;
  background:#111;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  cursor:pointer;
  overflow:hidden;
  padding:10px;
  transition:.25s ease;
}

body.hover-enlarge .gallery-item:hover {
  transform:scale(1.08);
  box-shadow:0 0 30px var(--green);
}

.gallery-item img,
.gallery-item video {
  width:100%;
  height:100%;
  object-fit:cover;
}

#mainDisplay {
  min-height:45vh;
  display:flex;
  justify-content:center;
  align-items:center;
  flex-direction:column;
  text-align:center;
  background:var(--gallery-bg);
  border-radius:16px;
  padding:20px;
}

#mainDisplay img,
#mainDisplay video {
  max-width:100%;
  max-height:60vh;
  border:2px solid var(--green);
  border-radius:12px;
}

.image-popup {
  display:none;
  position:fixed;
  inset:0;
  z-index:5000;
  background:rgba(0,0,0,.92);
  justify-content:center;
  align-items:center;
  flex-direction:column;
  padding:20px;
}

.image-popup-toolbar {
  position:fixed;
  top:20px;
  left:50%;
  transform:translateX(-50%);
  z-index:5100;
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  justify-content:center;
}

.image-popup-content {
  display:flex;
  justify-content:center;
  align-items:center;
  max-width:88vw;
  max-height:84vh;
}

.image-popup img,
.image-popup video {
  max-width:88vw;
  max-height:78vh;
  border:4px solid var(--green);
  border-radius:18px;
  box-shadow:0 0 45px var(--green);
  object-fit:contain;
}

.image-popup.minimized .image-popup-content img,
.image-popup.minimized .image-popup-content video {
  max-width:420px;
  max-height:320px;
}

.image-popup.maximized .image-popup-content img,
.image-popup.maximized .image-popup-content video {
  max-width:96vw;
  max-height:88vh;
}

iframe {
  width:100%;
  min-height:70vh;
  border:2px solid var(--green);
  border-radius:12px;
  background:#fff;
}

footer {
  position:fixed;
  bottom:0;
  width:100%;
  background:#000;
  border-top:2px solid var(--green);
  z-index:1050;
}

.modal-max {
  max-width:100vw!important;
  width:100vw!important;
  height:100vh!important;
  margin:0!important;
}

.modal-max .modal-content {
  height:100vh!important;
  border-radius:0;
}

.modal-min {
  max-width:420px!important;
}

.setup-control {
  border:1px solid var(--green);
  border-radius:14px;
  padding:16px;
  margin-bottom:16px;
  background:#080808;
}

input[type="color"] {
  width:100%;
  height:48px;
  border:2px solid var(--green);
  background:#111;
}

#youtubePlayer {
  width:100%;
  height:360px;
  border:2px solid var(--green);
  border-radius:12px;
  overflow:hidden;
  background:#000;
}
</style>
</head>

<body class="hover-enlarge">

<nav class="navbar navbar-expand-lg navbar-dark bg-black border-bottom border-success sticky-top">
  <div class="container">
    <a class="navbar-brand text-success fw-bold" href="#home">
      <i class="fa-solid fa-photo-film"></i> JOHTML Search / Media Gallery V4+
    </a>

    <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div id="navMenu" class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a href="#home" class="nav-link">HOME</a></li>
        <li class="nav-item"><a href="#input" class="nav-link">INPUT</a></li>
        <li class="nav-item"><a href="#google" class="nav-link">GOOGLE SEARCH</a></li>
        <li class="nav-item"><a href="#gallery" class="nav-link">GALLERY</a></li>

        <li class="nav-item">
          <button class="btn btn-green btn-sm ms-lg-2" data-bs-toggle="modal" data-bs-target="#galleryModal">
            GALLERY
          </button>
        </li>

        <li class="nav-item">
          <button class="btn btn-green btn-sm ms-lg-2" data-bs-toggle="modal" data-bs-target="#setupModal">
            SETTINGS
          </button>
        </li>

        <li class="nav-item">
          <button class="btn btn-green btn-sm ms-lg-2" data-bs-toggle="modal" data-bs-target="#contactModal">
            CONTACT
          </button>
        </li>
      </ul>
    </div>
  </div>
</nav>

<section id="home" class="container py-5 text-center">
  <h1 class="display-5 fw-bold text-success">
    <i class="fa-solid fa-magnifying-glass"></i> Search + Media Gallery V4+
  </h1>
  <p>Populate the gallery with images, audio, MP4 videos, YouTube playback, or Google Search result links.</p>
</section>

<section id="input" class="container py-4">
  <div class="card p-4">
    <h2 class="text-success">INPUT PANEL</h2>

    <label class="form-label mt-3">INPUT_TEXT</label>
    <textarea id="inputText" class="form-control" rows="4"
      placeholder="Enter multi-line text, image URLs, audio URLs, video URLs or search terms"></textarea>

    <label class="form-label mt-3">LOCAL_PATH</label>
    <input type="file" id="localInput" class="form-control" multiple
      accept=".jpg,.jpeg,.png,.mp4,.mp3,.wav,.ogg,.m4a">

    <label class="form-label mt-3">URL_PATH</label>
    <input id="urlInput" class="form-control"
      placeholder="https://example.com/file.jpg OR .mp3 OR .mp4">

    <div class="mt-3 d-flex flex-wrap gap-2">
      <button onclick="loadLocalFiles()" class="btn btn-green">
        <i class="fa-solid fa-folder-open"></i> Load Local Files
      </button>

      <button onclick="addUrlPath()" class="btn btn-green">
        <i class="fa-solid fa-plus"></i> Add URL_PATH
      </button>

      <button onclick="generateGallery()" class="btn btn-green">
        <i class="fa-solid fa-wand-magic-sparkles"></i> GENERATE
      </button>
    </div>

    <hr class="border-success my-4">

    <h3 class="text-success">SELECT_BOX</h3>
    <select id="selectBox" class="form-select" multiple size="8"></select>
    <textarea id="editableList" class="form-control mt-2" rows="5"></textarea>

    <div class="mt-3 d-flex flex-wrap gap-2">
      <button onclick="updateSelect()" class="btn btn-green">UPDATE LIST</button>
      <button onclick="selectAll()" class="btn btn-green">SELECT_ALL</button>
      <button onclick="displaySelected()" class="btn btn-green">DISPLAY SELECTED</button>
      <button onclick="clearGallery()" class="btn btn-green">CLEAR</button>
    </div>

    <div id="statusBox" class="mt-3 p-3 rounded" style="border:1px solid var(--green);background:#070707;">
      Ready.
    </div>
  </div>
</section>

<section id="google" class="container py-4">
  <div class="card p-4">
    <h2 class="text-success"><i class="fa-brands fa-google"></i> Google Search</h2>

    <label class="form-label mt-3">INPUT_TEXT</label>
    <textarea id="googleInputText" class="form-control" rows="5"
      placeholder="Enter one Google search query per line"></textarea>

    <button onclick="loadGoogleSearch()" class="btn btn-green mt-3">
      <i class="fa-solid fa-magnifying-glass"></i> Load Google Search
    </button>
  </div>
</section>

<section id="gallery" class="container py-5">
  <h2 class="text-success">Horizontal Selectable Gallery</h2>

  <div class="gallery-area">
    <div class="mb-3 text-end">
      <button class="btn btn-green" data-bs-toggle="modal" data-bs-target="#setupModal">
        <i class="fa-solid fa-gear"></i> SETTINGS
      </button>
    </div>

    <div id="pageGalleryStrip" class="gallery-strip"></div>
  </div>
</section>

<div id="imagePopup" class="image-popup">
  <div class="image-popup-toolbar">
    <button onclick="popupPrev(event)" class="btn btn-green btn-sm">PREV</button>
    <button onclick="popupNext(event)" class="btn btn-green btn-sm">NEXT</button>
    <button onclick="popupMin(event)" class="btn btn-green btn-sm">MIN</button>
    <button onclick="popupMax(event)" class="btn btn-green btn-sm">MAX</button>
    <button onclick="closeImagePopup(event)" class="btn btn-green btn-sm">CLOSE</button>
  </div>

  <div id="imagePopupContent" class="image-popup-content"></div>
</div>

<div class="modal fade" id="galleryModal" tabindex="-1">
  <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
    <div class="modal-content">

      <div class="modal-header border-success">
        <h5 class="text-success">Scrollable Editable Gallery</h5>

        <div class="d-flex gap-2">
          <button class="btn btn-green btn-sm" data-bs-toggle="modal" data-bs-target="#setupModal">
            <i class="fa-solid fa-gear"></i> SETTINGS
          </button>

          <button onclick="minModal()" class="btn btn-green btn-sm">MIN</button>
          <button onclick="maxModal()" class="btn btn-green btn-sm">MAX</button>
          <button class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
      </div>

      <div class="modal-body gallery-area">
        <textarea class="form-control mb-3" rows="3">Editable notes: gallery populated from images, audio, MP4, YouTube or Google Search results.</textarea>

        <div class="text-center mb-3">
          <button onclick="prev()" class="btn btn-green">PREV</button>
          <button onclick="next()" class="btn btn-green">NEXT</button>
        </div>

        <div id="mainDisplay">
          <p class="text-warning">Generate or display selected items first.</p>
        </div>

        <div id="modalGalleryStrip" class="gallery-strip mt-3"></div>
      </div>

    </div>
  </div>
</div>

<div class="modal fade" id="setupModal" tabindex="-1">
  <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
    <div class="modal-content">

      <div class="modal-header border-success">
        <h5 class="text-success">
          <i class="fa-solid fa-sliders"></i> SETUP
        </h5>
        <button class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body scroll-box">

        <div class="setup-control">
          <h4 class="text-success">Background Music MP3</h4>

          <input id="musicInput" type="file" class="form-control mb-3"
            accept=".mp3,audio/mp3,audio/mpeg">

          <audio id="bgMusic" controls class="w-100 mb-3"></audio>

          <div class="d-flex flex-wrap gap-2">
            <button onclick="playMusic()" class="btn btn-green">PLAY</button>
            <button onclick="pauseMusic()" class="btn btn-green">PAUSE</button>
            <button onclick="fastForwardMusic()" class="btn btn-green">FAST-FWD</button>
            <button onclick="fastRewindMusic()" class="btn btn-green">FAST-RWD</button>
            <button onclick="volumeUp()" class="btn btn-green">VOLUME+</button>
            <button onclick="volumeDown()" class="btn btn-green">VOLUME-</button>
          </div>
        </div>

        <div class="setup-control">
          <h4 class="text-success">
            <i class="fa-brands fa-youtube"></i> YouTube
          </h4>

          <label class="form-label">YouTube URL</label>
          <input id="youtubeUrlInput" class="form-control mb-3"
            placeholder="https://www.youtube.com/watch?v=VIDEO_ID">

          <button onclick="loadYouTubeVideo()" class="btn btn-green mb-3">
            LOAD YOUTUBE
          </button>

          <div id="youtubePlayer"></div>

          <div class="d-flex flex-wrap gap-2 mt-3">
            <button onclick="youtubePlay()" class="btn btn-green">PLAY</button>
            <button onclick="youtubePause()" class="btn btn-green">PAUSE</button>
            <button onclick="youtubeRewind()" class="btn btn-green">RWD</button>
            <button onclick="youtubeForward()" class="btn btn-green">FWD</button>
            <button onclick="youtubeVolumeUp()" class="btn btn-green">VOL+</button>
            <button onclick="youtubeVolumeDown()" class="btn btn-green">VOL-</button>
          </div>
        </div>

        <div class="setup-control">
          <h4 class="text-success">Gallery Background Colour</h4>
          <input id="galleryBgColor" type="color" value="#000000"
            onchange="changeGalleryBackground(this.value)">
        </div>

        <div class="setup-control">
          <h4 class="text-success">Image Enlarge Mode</h4>

          <select id="enlargeMode" class="form-select"
            onchange="changeEnlargeMode(this.value)">
            <option value="hover">Mouse Over Enlarge Image</option>
            <option value="click">Mouse Click Enlarge Image</option>
          </select>

          <p class="mt-2">
            Hover mode opens the enlarged popup on mouse-over.
            Click mode opens the enlarged popup only when clicked.
          </p>
        </div>

        <div class="setup-control">
          <h4 class="text-success">Gallery Detail Colour</h4>
          <input id="detailColor" type="color" value="#00ff66"
            onchange="changeDetailColour(this.value)">
        </div>

      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="contactModal" tabindex="-1">
  <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header border-success">
        <h5 class="text-success">Contact</h5>
        <button class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body">
        <textarea class="form-control mb-3" rows="3">Editable notes: Contact modal loads https://raiiarcomio.com/contact2 below.</textarea>
        <iframe src="https://raiiarcomio.com/contact2"></iframe>
      </div>
    </div>
  </div>
</div>

<footer class="text-center py-3">
  <div class="mb-2 d-flex flex-wrap justify-content-center gap-3">
    <a href="#home">HOME</a>
    <a href="#input">INPUT</a>
    <a href="#google">GOOGLE SEARCH</a>
    <a href="#gallery">GALLERY</a>

    <button class="btn btn-green btn-sm" data-bs-toggle="modal" data-bs-target="#galleryModal">
      GALLERY
    </button>

    <button class="btn btn-green btn-sm" data-bs-toggle="modal" data-bs-target="#setupModal">
      SETTINGS
    </button>

    <button class="btn btn-green btn-sm" data-bs-toggle="modal" data-bs-target="#contactModal">
      CONTACT
    </button>
  </div>

  <a href="https://raiiarcomio.com" target="_blank" class="fw-bold">
    Another Website by Julius Olatokubo
  </a>
</footer>

<script>
let items = [];
let gallery = [];
let index = 0;
let popupIndex = 0;
let enlargeMode = "hover";

let youtubePlayer = null;
let youtubeVolume = 50;

const selectBox = document.getElementById("selectBox");
const editableList = document.getElementById("editableList");
const statusBox = document.getElementById("statusBox");
const pageGalleryStrip = document.getElementById("pageGalleryStrip");
const modalGalleryStrip = document.getElementById("modalGalleryStrip");
const mainDisplay = document.getElementById("mainDisplay");
const imagePopup = document.getElementById("imagePopup");
const imagePopupContent = document.getElementById("imagePopupContent");
const bgMusic = document.getElementById("bgMusic");

const defaultItems = [
  "SELECT_ALL",
  "https://raiiarcomio.com/m&j/"
];

function status(msg) {
  statusBox.innerHTML = msg;
}

function getType(src) {
  const clean = src.split("?")[0].toLowerCase();

  if (clean.match(/\\.(jpg|jpeg|png|gif|webp)$/)) return "image";
  if (clean.match(/\\.(mp3|wav|ogg|m4a)$/)) return "audio";
  if (clean.match(/\\.(mp4|webm|mov)$/)) return "video";
  if (src.startsWith("https://www.google.com/search")) return "google";
  if (src.startsWith("blob:")) return "local";
  if (src.includes("youtube.com") || src.includes("youtu.be")) return "youtube";

  return "link";
}

function makeItem(src, label = null, type = null) {
  return {
    src,
    label: label || src,
    type: type || getType(src)
  };
}

function refresh() {
  const unique = [];
  const seen = new Set();

  items.forEach(item => {
    if (!seen.has(item.src)) {
      seen.add(item.src);
      unique.push(item);
    }
  });

  items = unique;
  selectBox.innerHTML = "";

  items.forEach((item, i) => {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = item.label;
    selectBox.appendChild(opt);
  });

  editableList.value = items.map(x => x.src).join("\\n");
}

function updateSelect() {
  const lines = editableList.value
    .split("\\n")
    .map(x => x.trim())
    .filter(Boolean);

  items = lines.map(line => {
    if (line === "SELECT_ALL") {
      return makeItem("SELECT_ALL", "SELECT_ALL", "control");
    }
    return makeItem(line);
  });

  if (!items.some(x => x.src === "SELECT_ALL")) {
    items.unshift(makeItem("SELECT_ALL", "SELECT_ALL", "control"));
  }

  refresh();
  status("? SELECT_BOX updated.");
}

function selectAll() {
  [...selectBox.options].forEach(o => o.selected = true);
  status("? SELECT_ALL applied.");
}

selectBox.addEventListener("change", () => {
  const selected = [...selectBox.selectedOptions].map(o => items[Number(o.value)]?.src);

  if (selected.includes("SELECT_ALL")) {
    selectAll();
  }
});

function selectedItems() {
  return [...selectBox.selectedOptions]
    .map(o => items[Number(o.value)])
    .filter(x => x && x.src !== "SELECT_ALL");
}

function loadLocalFiles() {
  const files = [...document.getElementById("localInput").files];
  let added = 0;

  files.forEach(file => {
    const src = URL.createObjectURL(file);
    const type =
      file.type.startsWith("image/") ? "image" :
      file.type.startsWith("audio/") ? "audio" :
      file.type.startsWith("video/") ? "video" :
      "link";

    items.push(
      makeItem(src, "LOCAL: " + file.name, type)
    );

    added++;
  });

  refresh();
  status(`? Loaded ${added} local file(s).`);
}

function addUrlPath() {
  const url = document.getElementById("urlInput").value.trim();

  if (!url) {
    status("? Enter URL_PATH first.");
    return;
  }

  items.push(makeItem(url));
  refresh();
  status("? URL_PATH added to SELECT_BOX.");
}

async function loadGoogleSearch() {
  const text = document.getElementById("googleInputText").value.trim();

  if (!text) {
    status("? Enter Google Search INPUT_TEXT first.");
    return;
  }

  const queries = text
    .split("\\n")
    .map(x => x.trim())
    .filter(Boolean);

  let added = 0;

  for (const q of queries) {
    const response = await fetch(`/api/search/google?query=${encodeURIComponent(q)}`);
    const data = await response.json();
    
    if (data.success) {
      items.push(
        makeItem(data.searchUrl, "GOOGLE RESULT: " + q, "google")
      );
      added++;
    }
  }

  refresh();
  status(`? Loaded ${added} Google item(s) into SELECT_BOX.`);
}

async function generateGallery() {
  gallery = [];

  const selected = selectedItems();
  gallery.push(...selected);

  const text = document.getElementById("inputText").value.trim();

  if (text) {
    const queries = text
      .split("\\n")
      .map(x => x.trim())
      .filter(Boolean);

    for (const q of queries) {
      if (getType(q) !== "link") {
        gallery.push(makeItem(q));
      } else {
        const response = await fetch(`/api/search/google?query=${encodeURIComponent(q)}`);
        const data = await response.json();
        
        if (data.success) {
          gallery.push(
            makeItem(data.searchUrl, "GOOGLE RESULT: " + q, "google")
          );
        }
      }
    }
  }

  renderGallery();

  if (gallery.length) {
    show(0);
    status(`? Gallery generated with ${gallery.length} item(s).`);
  } else {
    status("? No gallery items found.");
  }
}

function displaySelected() {
  gallery = selectedItems();
  renderGallery();

  if (gallery.length) {
    show(0);
    status(`? Displaying ${gallery.length} selected item(s).`);
  } else {
    status("? No selected items.");
  }
}

function renderGallery() {
  [pageGalleryStrip, modalGalleryStrip].forEach(strip => {
    strip.innerHTML = "";

    gallery.forEach((item, i) => {
      const div = document.createElement("div");
      div.className = "gallery-item";

      div.onclick = () => {
        if (enlargeMode === "click" && ["image", "video", "local", "youtube"].includes(item.type)) {
          openImagePopup(item, i);
        } else {
          show(i);
        }
      };

      div.onmouseenter = () => {
        if (enlargeMode === "hover" && ["image", "video", "local", "youtube"].includes(item.type)) {
          openImagePopup(item, i);
        }
      };

      if (item.type === "image" || item.type === "local") {
        div.innerHTML = `<img src="${item.src}" alt="${item.label}">`;
      } else if (item.type === "audio") {
        div.innerHTML = `
          <i class="fa-solid fa-music fa-3x text-success"></i>
          <small class="mt-2">${item.label}</small>
          <audio src="${item.src}" controls class="w-100 mt-2"></audio>
        `;
      } else if (item.type === "video") {
        div.innerHTML = `<video src="${item.src}" muted></video>`;
      } else if (item.type === "youtube") {
        div.innerHTML = `
          <i class="fa-brands fa-youtube fa-3x text-success"></i>
          <small class="mt-2 text-center">YouTube Video</small>
        `;
      } else if (item.type === "google") {
        div.innerHTML = `
          <i class="fa-brands fa-google fa-3x text-success"></i>
          <small class="mt-2 text-center">${item.label}</small>
        `;
      } else {
        div.innerHTML = `
          <i class="fa-solid fa-link fa-3x text-success"></i>
          <small class="mt-2 text-center">${item.label}</small>
        `;
      }

      strip.appendChild(div);
    });
  });
}

async function show(i) {
  if (!gallery.length) return;

  index = i;
  const item = gallery[i];

  if (item.type === "image" || item.type === "local") {
    mainDisplay.innerHTML = `
      <img src="${item.src}">
      <p class="mt-2">${item.label}</p>
    `;
  } else if (item.type === "audio") {
    mainDisplay.innerHTML = `
      <i class="fa-solid fa-file-audio fa-5x text-success mb-3"></i>
      <h4>${item.label}</h4>
      <audio src="${item.src}" controls aut