# 📥 YouTube Downloader

Local-only YouTube video, playlist, और channel downloader — Flask + yt-dlp + FFmpeg पर आधारित।

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2024.12%2B-red)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

---

## ✨ Features

- 🎬 **Video / Playlist / Channel** — तीनों support
- 🎚 **Quality selection** — Best, 4K, 1440p, 1080p, 720p, 480p, 360p, Audio only
- 🎵 **Audio extraction** — MP3, M4A, WAV, OPUS
- 📋 **Hand-pick videos** — प्लेलिस्ट में से चुनिंदा videos
- 🔢 **Range download** — Start-End index से
- 🔀 **Reverse order** — प्लेलिस्ट उल्टे क्रम में
- ⏸ **Pause / Resume** — बीच में रोकें, बाद में जारी रखें
- 🔁 **Retry failed** — fail हुई video को दोबारा try करें
- 🔍 **Search filter** — प्लेलिस्ट में title से खोजें
- 📤 **Export CSV / TXT** — video list को save करें
- 📊 **Live progress** — size, speed, ETA, overall counter
- 💾 **Disk space check** — download से पहले warning
- 📁 **Custom save folder** — कहीं भी save करें
- 🌗 **Light / Dark theme** — toggle button
- 🔔 **Completion beep** — sound notification
- 📋 **Clipboard auto-paste** — link अपने आप paste
- 🔒 **100% local** — कोई cloud, कोई tracking नहीं

---

## 🚀 Quick Start

### 1. Prerequisites

| Tool | आवश्यक? | Install |
|------|---------|---------|
| **Python 3.8+** | ✅ हाँ | [python.org](https://python.org) |
| **FFmpeg** | ✅ हाँ | [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (Win) / `apt install ffmpeg` (Linux) |
| **aria2c** | ⬜ Optional | [aria2.github.io](https://aria2.github.io/) |

**PATH check:**
```bash
python --version
ffmpeg -version
aria2c --version   # optional
```

### 2. Install Python packages

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

### 4. Open browser

```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
youtube-downloader/
│
├── app.py                 # Flask backend (सारा logic)
├── requirements.txt       # Python packages
├── README.md              # This file
├── USER_GUIDE.md          # Detailed guide
├── guide.txt              # Original guide (reference)
│
├── templates/
│   └── index.html         # Main page
│
├── static/
│   ├── style.css          # Theme styling
│   └── app.js             # Frontend logic
│
└── downloads/             # Default output folder
    ├── My Video.mp4
    └── My Playlist Name/
        ├── 01 - First Video.mp4
        ├── 02 - Second Video.mp4
        └── 03 - Third Video.mp4
```

---

## 🎯 How to Use (Short Version)

1. **Paste URL** — video, playlist, या channel
2. **Fetch** — metadata load होगा
3. **Choose quality** — Best / 1080p / Audio only आदि
4. **Configure** — playlist हो तो range / select / order चुनें
5. **Download** — progress live दिखेगा
6. **Files** — `downloads/` folder में save होंगी

पूरी details के लिए [`USER_GUIDE.md`](USER_GUIDE.md) देखें।

---

## 🎬 Supported URLs

| Type | Example |
|------|---------|
| **Video** | `https://www.youtube.com/watch?v=VIDEO_ID` |
| **Playlist** | `https://www.youtube.com/playlist?list=PLAYLIST_ID` |
| **Channel** | `https://www.youtube.com/@ChannelName` |
| **Channel (old)** | `https://www.youtube.com/c/ChannelName` |
| **Channel (user)** | `https://www.youtube.com/user/Username` |

---

## ⚙️ Configuration

`app.py` में कुछ important settings:

### 1. aria2c (optional speed boost)

```python
USE_ARIA2C_IF_AVAILABLE = False   # True करें तो तेज़, लेकिन progress कम smooth
```

### 2. Bot-check fix (Cookies)

YouTube कभी-कभी "Sign in to confirm you're not a bot" error देता है। इसे fix करने के लिए:

```python
# Option A: Browser से direct cookies पढ़ें
COOKIES_FROM_BROWSER = "chrome"   # chrome, firefox, edge, brave, opera

# Option B: cookies.txt file use करें
COOKIES_FILE = r"C:\Users\YourName\cookies.txt"
```

फिर `app.py` restart करें।

---

## 📊 Progress Panel

**Single video:**
```
My Video Title.mp4
[██████████████░░░░░░]
72%   842 MB / 1.20 GB   18.4 MB/s   00:01:42
```

**Playlist:**
```
4 / 20 videos completed

✓  Video 1        Completed
✓  Video 2        Completed
↓  Video 3        63%
○  Video 4        Waiting
✕  Video 5        Failed    [Retry]
```

| Icon | Meaning |
|------|---------|
| ○ | Waiting |
| ↓ | Downloading |
| ✓ | Completed |
| ✕ | Failed (Retry available) |

---

## 🐛 Common Errors

| Error | Solution |
|-------|----------|
| **FFmpeg was not found** | FFmpeg install करें, PATH में add करें |
| **Sign in to confirm you're not a bot** | `COOKIES_FROM_BROWSER` set करें |
| **Invalid / unsupported URL** | YouTube link सही है क्या? |
| **Private video / unavailable** | Video removed या private है |
| **Folder path must be absolute** | पूरा path दें (e.g. `D:\Videos`) |
| **Network error** | Server चल रहा है? Internet OK? |

**Tip:** अगर downloads अचानक fail होने लगें:
```bash
pip install -U yt-dlp
```

---

## 🔒 Privacy

- ✅ सिर्फ़ **127.0.0.1** पर चलता है (local only)
- ✅ कोई login, database, cloud upload नहीं
- ✅ कोई analytics, tracking नहीं
- ✅ सिर्फ़ yt-dlp → YouTube traffic
- ✅ Theme/sound preferences browser localStorage में

---

## 🚀 Advanced

### Background में चलाना (Windows)

```bat
@echo off
start "" pythonw app.py
```

### Startup पर auto-run

1. `Win + R` → `shell:startup` → Enter
2. ऊपर वाला `.bat` file वहाँ रखें

### Standalone .exe

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

### Network access (अपने LAN में)

```python
# app.py में
app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
```

फिर `http://<your-ip>:5000` से access करें।

---

## 📋 Requirements Summary

| Component | Version | Mandatory |
|-----------|---------|-----------|
| Python | 3.8+ | ✅ |
| Flask | 3.0+ | ✅ |
| yt-dlp | 2024.12+ | ✅ |
| FFmpeg | Latest | ✅ |
| aria2c | Latest | ⬜ |

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Contributing

Bug report या feature request के लिए issue खोलें।

---

## ⭐ Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) — Web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube extraction
- [FFmpeg](https://ffmpeg.org/) — Media processing
- [aria2](https://aria2.github.io/) — Fast downloads (optional)

---

**Enjoy downloading! 📥**