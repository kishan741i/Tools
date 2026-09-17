# 📖 YouTube Downloader — User Guide

पूरी guide — installation, usage, features, और troubleshooting।

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [First Run](#-first-run)
3. [Step-by-Step Usage](#-step-by-step-usage)
4. [Quality Options](#-quality-options)
5. [Playlist Options](#-playlist-options)
6. [Progress Panel](#-progress-panel)
7. [Pause / Resume / Retry](#-pause--resume--retry)
8. [Custom Save Folder](#-custom-save-folder)
9. [Export Video List](#-export-video-list)
10. [Theme & Sound](#-theme--sound)
11. [Troubleshooting](#-troubleshooting)
12. [Advanced Usage](#-advanced-usage)
13. [FAQ](#-faq)

---

## 🛠 Installation

### Step 1: Python

- Python 3.8+ डाउनलोड करें: https://python.org
- Install करते समय **"Add Python to PATH"** ✅ करें

### Step 2: FFmpeg (ज़रूरी)

**Windows:**
1. https://www.gyan.dev/ffmpeg/builds/ से download करें
2. Extract करें `C:\ffmpeg\` में
3. PATH में add करें: `C:\ffmpeg\bin`
4. Verify: `ffmpeg -version`

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Step 3: aria2c (optional)

तेज़ download के लिए (ज़रूरी नहीं):

**Windows:** https://github.com/aria2/aria2/releases
**Linux:** `sudo apt install aria2`
**macOS:** `brew install aria2`

### Step 4: Python packages

```bash
pip install -r requirements.txt
```

### Step 5: Verify

```bash
python --version       # Python 3.8+
ffmpeg -version        # FFmpeg OK
aria2c --version       # optional
```

---

## 🚀 First Run

### Server start करें

```bash
python app.py
```

Output:
```
Starting server at http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

### Browser में खोलें

```
http://127.0.0.1:5000
```

### Server बंद करें

Terminal में `Ctrl + C`

---

## 🎯 Step-by-Step Usage

### STEP 1 — URL paste करें

- YouTube video / playlist / channel link paste करें
- Clipboard auto-paste: page load पर link अपने आप आ जाता है
- **Fetch** दबाएं या **Enter**

App खुद detect करेगा:
- **Video** — single video
- **Playlist** — playlist
- **Channel** — channel के uploads

### STEP 2 — Info check करें

**Video के लिए:**
- Thumbnail, title, channel, duration
- Available qualities

**Playlist/Channel के लिए:**
- Thumbnail, title, channel
- Total video count
- Estimated total size (rough)
- Search box + Export buttons
- पूरी video list

### STEP 3 — Quality चुनें

Quality dropdown:
```
Best Quality
2160p / 4K
1440p
1080p
720p
480p
360p
Audio Only
```

**Audio Only** चुनने पर — MP3 / M4A / WAV / OPUS dropdown आएगा।

### STEP 4 — Playlist options (playlist हो तो)

**Download order:**
- Playlist order (default)
- Reverse order

**Download mode:**
- **Whole playlist** — सब कुछ
- **Specific range** — Start / End index
- **Hand-pick videos** — checkbox से चुनें

### STEP 5 — Save folder (optional)

Default: `downloads/` folder (app.py के साथ)

Custom path के लिए पूरा **absolute path** paste करें:
- Windows: `D:\Videos`
- Linux/Mac: `/home/you/Videos`

**Note:** Browser native folder dialog नहीं खोल सकता local server के लिए — यह browser security है। इसलिए path manually paste करें।

### STEP 6 — Download

**Download** button दबाएं।

अगर estimated size > free space → warning dialog आएगा।

Progress panel नीचे दिखेगा।

---

## 🎚 Quality Options

| Option | Format | Notes |
|--------|--------|-------|
| **Best Quality** | `bv*+ba/b` | Best video + best audio |
| **2160p / 4K** | `height<=2160` | 4K तक |
| **1440p** | `height<=1440` | 2K |
| **1080p** | `height<=1080` | Full HD |
| **720p** | `height<=720` | HD |
| **480p** | `height<=480` | SD |
| **360p** | `height<=360` | Low |
| **Audio Only** | `bestaudio` | MP3/M4A/WAV/OPUS |

**Note:** 1080p+ के लिए FFmpeg ज़रूरी है (video + audio merge के लिए)।

---

## 📋 Playlist Options

### Whole Playlist

पूरी playlist download होगी।

### Specific Range

Start और End index दें:
- Start: 1
- End: 20

→ Videos 1 से 20 तक download होंगी।

### Hand-pick Videos

- Playlist में checkboxes आएंगे
- जो videos चाहिए उन्हें tick करें
- **Select All** / **Select None** buttons
- Selected count नीचे दिखेगा

### Reverse Order

Playlist उल्टे क्रम में download होगी (आखिरी video पहले)।

---

## 📊 Progress Panel

### Single Video

```
My Video Title.mp4
Merging video & audio...
[██████████████░░░░░░]
72%   842 MB / 1.20 GB   18.4 MB/s   00:01:42
```

Stats:
- **Percent** — कितना हो गया
- **Size** — downloaded / total
- **Speed** — MB/s
- **ETA** — कितना time बचा

### Playlist

```
4 / 20 videos completed

✓  Video 1        Completed
✓  Video 2        Completed
✓  Video 3        Completed
↓  Video 4        63%
○  Video 5        Waiting
○  Video 6        Waiting
✕  Video 7        Failed          [Retry]
↓  Video 8        Downloading audio...
```

### Status Icons

| Icon | Meaning |
|------|---------|
| ○ | Waiting (pending) |
| ↓ | Downloading |
| ✓ | Completed |
| ✕ | Failed |

### Stream Labels

Best quality में video और audio अलग download होते हैं:
- **Downloading video stream...** — video
- **Downloading audio stream...** — audio
- **Merging video & audio...** — FFmpeg merge
- **Converting audio...** — audio format convert

---

## ⏸ Pause / Resume / Retry

### Pause

- Download के दौरान **Pause** दबाएं
- Current file clean तरीके से रुकेगी
- **Resume** button आएगा

### Resume

- **Resume** दबाएं
- Partially-downloaded file जहाँ रुकी थी वहीं से शुरू होगी
- पूरी हो चुकी videos skip होंगी
- Status counter बना रहेगा

### Retry (Failed Video)

- Failed video पर **Retry** button
- सिर्फ़ वो video दोबारा download होगी
- बाकी playlist पर कोई असर नहीं

### Cancel

- **Cancel Download** — पूरा task रुक जाएगा
- अगर paused है — सिर्फ़ panel बंद होगा

---

## 💾 Custom Save Folder

### Default

`downloads/` folder (app.py के साथ)

```
downloads/
├── My Video.mp4
└── My Playlist Name/
    ├── 01 - First.mp4
    ├── 02 - Second.mp4
    └── 03 - Third.mp4
```

### Custom Path

"Save to folder" field में **absolute path** paste करें:

**Windows:**
```
D:\Videos
C:\Users\YourName\Downloads\YouTube
```

**Linux/Mac:**
```
/home/yourname/Videos
/Users/yourname/Movies/YouTube
```

**Rules:**
- ✅ Absolute path ज़रूरी (`C:\...` या `/...`)
- ✅ Folder नहीं है तो app बना देगा
- ✅ Write permission ज़रूरी
- ❌ Relative path (`./videos`) काम नहीं करेगा

---

## 📤 Export Video List

Playlist fetch करने के बाद 2 buttons:

### Export CSV

```
Index,Title,Duration,Video URL
1,"First Video","3:45","https://www.youtube.com/watch?v=abc123"
2,"Second Video","5:12","https://www.youtube.com/watch?v=def456"
```

Excel/Google Sheets में खोल सकते हैं।

### Export TXT

```
1. First Video (3:45) - https://www.youtube.com/watch?v=abc123
2. Second Video (5:12) - https://www.youtube.com/watch?v=def456
```

Simple text format।

---

## 🌗 Theme & Sound

### Theme Toggle (☀️ / 🌙)

- Header में top-right
- Light ↔ Dark switch
- Preference localStorage में save

### Sound Toggle (🔔 / 🔕)

- **🔔** — beep ON (download complete पर sound)
- **🔕** — beep OFF (muted)
- Preference localStorage में save

---

## 🐛 Troubleshooting

### ❌ FFmpeg was not found

**Solution:**
1. FFmpeg install करें
2. PATH में add करें
3. Terminal restart करें
4. `app.py` restart करें
5. Verify: `ffmpeg -version`

### ❌ Sign in to confirm you're not a bot

YouTube का bot-check. Fix:

**Option A — Browser cookies:**
```python
# app.py में
COOKIES_FROM_BROWSER = "chrome"   # या "firefox", "edge", "brave"
```
⚠️ Windows पर browser बंद करना पड़ेगा।

**Option B — cookies.txt file:**
1. Browser extension install करें: **"Get cookies.txt LOCALLY"**
2. YouTube पर login करें
3. Extension से cookies export करें → `cookies.txt`
4. `app.py` में:
```python
COOKIES_FILE = r"C:\Users\YourName\cookies.txt"
```

**Option C — yt-dlp update:**
```bash
pip install -U yt-dlp
```

### ❌ Invalid / unsupported URL

YouTube link सही है क्या? Supported formats:
- `youtube.com/watch?v=...`
- `youtu.be/...`
- `youtube.com/playlist?list=...`
- `youtube.com/@ChannelName`

### ❌ Private video / Video unavailable

Video removed, private, या region-locked है। Cookies से कभी-कभी काम करता है।

### ❌ Folder path must be absolute

**गलत:** `videos`, `./downloads`, `..\Videos`
**सही:** `D:\Videos`, `/home/user/Videos`

### ❌ That folder is not writable

- Path typo check करें
- Windows: Administrator से run करें
- Linux: `chmod` permission check करें

### ❌ Network error

- Server चल रहा है? (`python app.py`)
- Browser `http://127.0.0.1:5000` पर है?
- Terminal में error देखें

### ❌ Download बहुत धीमा

- aria2c install करें (तेज़ होगा)
- `USE_ARIA2C_IF_AVAILABLE = True` करें
- Network check करें

### ❌ Progress 100% पर jump कर रहा है

aria2c external downloader की वजह से। Fix:
```python
USE_ARIA2C_IF_AVAILABLE = False
```
yt-dlp native downloader smooth progress देता है।

### ❌ Stop button काम नहीं कर रहा

1-2 second wait करें — yt-dlp current fragment finish कर रहा है।

---

## 🚀 Advanced Usage

### 1. Startup पर auto-run

**Windows:**
1. `Win + R` → `shell:startup` → Enter
2. `start.bat` बनाएं:
```bat
@echo off
start "" pythonw "C:\path\to\app.py"
```
3. उस folder में रखें

### 2. Background में चलाना

```bash
pythonw app.py
```
`pythonw` = console window नहीं

### 3. Standalone .exe

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```
`dist/app.exe` मिलेगा

### 4. LAN access

`app.py` में:
```python
app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
```
अब `http://<your-ip>:5000` से access करें।

⚠️ **Warning:** Public network पर expose न करें — कोई authentication नहीं है।

### 5. Custom port

```python
app.run(host="127.0.0.1", port=8080, debug=False, threaded=True)
```

### 6. Different downloads folder

`app.py` में:
```python
DOWNLOAD_DIR = r"D:\YouTubeDownloads"
```

### 7. Speed tuning

```python
USE_ARIA2C_IF_AVAILABLE = True   # तेज़, लेकिन progress jumpy
```

aria2c connections:
```python
"external_downloader_args": {
    "aria2c": ["-x", "16", "-s", "16", "-k", "1M"]
}
```
- `-x 16` = 16 connections per server
- `-s 16` = 16 splits
- `-k 1M` = 1MB chunks

---

## ❓ FAQ

### Q1: Files कहाँ save होती हैं?

Default: `downloads/` folder (app.py के साथ)
Custom: जो path आपने "Save to folder" में दिया

### Q2: Data कहीं भेजा जाता है?

नहीं। 100% local। सिर्फ़ yt-dlp → YouTube traffic।

### Q3: Login ज़रूरी है?

नहीं, general videos के लिए। Age-restricted या private के लिए cookies ज़रूरी।

### Q4: कितनी videos download कर सकते हैं?

कोई limit नहीं (YouTube की rate limits तक)।

### Q5: Duplicate downloads रुकते हैं?

हाँ। `nooverwrites` और `continuedl` settings हैं। Existing files skip होती हैं।

### Q6: Quality check कैसे करें?

fetch के बाद "Available qualities" दिखता है।

### Q7: 4K download होगा?

हाँ, अगर YouTube पर 4K available है और आपने "2160p" चुना।

### Q8: Playlist का estimated size सही है?

Rough estimate है — एक sample video के basis पर। Actual size अलग हो सकता है।

### Q9: Server crash हो गया, downloads रुक गईं?

Server restart करें, फिर वही playlist/URL दोबारा download करें। Existing files skip होंगी।

### Q10: Mac/Linux पर चलेगा?

हाँ। FFmpeg/aria2c के paths अलग होंगे, बाकी सब same।

### Q11: Mobile पर?

Flask server LAN पर expose करके mobile browser से access कर सकते हैं। लेकिन UI desktop के लिए optimized है।

### Q12: Multiple instances चला सकते हैं?

नहीं, port 5000 conflict करेगा। Port बदलें।

---

## 📊 Performance Tips

| Tip | फ़ायदा |
|-----|--------|
| aria2c install करें | 2-5x तेज़ |
| Single video चुनें | Playlist से तेज़ |
| Range mode use करें | पूरी playlist से तेज़ |
| 720p चुनें | 1080p से आधा size |
| Audio Only | सबसे तेज़ |
| Custom folder = SSD | HDD से तेज़ |

---

## 📞 Support

- 🐛 Bug report → GitHub Issues
- 💡 Feature request → GitHub Issues
- 📖 yt-dlp issues → https://github.com/yt-dlp/yt-dlp

---

## 📜 License

MIT License — free to use, modify, distribute.

---

**Happy downloading! 📥**