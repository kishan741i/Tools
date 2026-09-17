"""
Local-only YouTube Video / Playlist / Channel Downloader
Backend: Flask + yt-dlp + (optional) aria2c + FFmpeg
Run:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
import re
import json
import queue
import shutil
import threading
import uuid
from urllib.parse import urlparse, parse_qs

from flask import Flask, request, jsonify, render_template, Response, stream_with_context

import yt_dlp
from yt_dlp.utils import DownloadError, DownloadCancelled, sanitize_filename

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Flask(__name__)

FFMPEG_PATH = shutil.which("ffmpeg")
FFMPEG_DIR = os.path.dirname(FFMPEG_PATH) if FFMPEG_PATH else None
ARIA2C_PATH = shutil.which("aria2c")

# Default OFF: with aria2c as the external downloader, yt-dlp often reports
# progress only once at the very end (jumps straight to 100%, no live size/
# speed/ETA) instead of updating continuously. yt-dlp's own native downloader
# reports smooth, real, per-second progress, so that's the default here.
# Set to True to use aria2c for extra download speed if you don't mind losing
# live progress detail.
USE_ARIA2C_IF_AVAILABLE = False

# ---- Cookies: fixes "Sign in to confirm you're not a bot" ------------------
# YouTube sometimes blocks requests that look automated. Fill in ONE of these
# to send your own browser's cookies (leave both as None/empty for no cookies):
#
#   COOKIES_FROM_BROWSER = "chrome"   # or "firefox", "edge", "brave", "opera"
#       Reads cookies straight from that browser's cookie store. Simplest
#       option, but the browser must be closed on Windows while it runs.
#
#   COOKIES_FILE = r"C:\Users\Kishan\cookies.txt"
#       A cookies.txt file exported with a browser extension (e.g. "Get
#       cookies.txt LOCALLY"), logged into youtube.com. Works even with the
#       browser open.
#
# If neither is set and you still hit the bot-check error, also try:
#   pip install -U yt-dlp
# since YouTube changes this check often and newer yt-dlp releases usually
# adapt to it.
COOKIES_FROM_BROWSER = None
COOKIES_FILE = None

QUALITY_FORMAT_MAP = {
    "best": "bv*+ba/b",
    "2160": "bv*[height<=2160]+ba/b[height<=2160]",
    "1440": "bv*[height<=1440]+ba/b[height<=1440]",
    "1080": "bv*[height<=1080]+ba/b[height<=1080]",
    "720": "bv*[height<=720]+ba/b[height<=720]",
    "480": "bv*[height<=480]+ba/b[height<=480]",
    "360": "bv*[height<=360]+ba/b[height<=360]",
}
VALID_AUDIO_FORMATS = {"mp3", "m4a", "wav", "opus"}
VALID_MODES = {"whole", "range", "select"}

# task_id -> task state dict
tasks = {}
tasks_lock = threading.Lock()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def clean_error(msg):
    """Strip yt-dlp's verbose error noise down to a single readable line."""
    msg = str(msg).strip()
    if msg.startswith("ERROR: "):
        msg = msg[7:]
    msg = msg.split("\n")[0].strip()
    if not msg:
        msg = "An unknown error occurred."
    return msg


def format_duration(seconds):
    if seconds is None:
        return None
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return None
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def best_thumbnail(info):
    thumbs = info.get("thumbnails") or []
    if thumbs:
        return thumbs[-1].get("url")
    return info.get("thumbnail")


def build_common_opts():
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    if FFMPEG_DIR:
        opts["ffmpeg_location"] = FFMPEG_DIR
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    elif COOKIES_FROM_BROWSER:
        opts["cookiesfrombrowser"] = (COOKIES_FROM_BROWSER,)
    return opts


# ---- URL classification (video / playlist / channel) ---------------------

CHANNEL_PATTERN = re.compile(r'youtube\.com/(channel/|c/|user/|@)', re.I)
TAB_SUFFIX_PATTERN = re.compile(r'/(videos|streams|shorts|playlists)(/|\?|$)', re.I)


def classify_url(url):
    """Returns 'playlist', 'channel', or 'video'."""
    try:
        qs = parse_qs(urlparse(url).query)
        if qs.get("list") and qs["list"][0]:
            return "playlist"
    except Exception:
        pass
    if CHANNEL_PATTERN.search(url):
        return "channel"
    return "video"


def normalize_channel_url(url):
    """Point a bare channel URL at its Videos tab so flat extraction lists uploads."""
    if TAB_SUFFIX_PATTERN.search(url):
        return url
    return url.rstrip("/") + "/videos"


# ---- Rough size estimate, broken down per quality option ------------------

# Mirrors the height caps used in QUALITY_FORMAT_MAP so the estimate matches
# what will actually be downloaded for each quality choice.
QUALITY_HEIGHT_CAPS = [
    ("best", None),
    ("2160", 2160),
    ("1440", 1440),
    ("1080", 1080),
    ("720", 720),
    ("480", 480),
    ("360", 360),
]


def sizes_by_quality(formats, duration=None):
    """Given a video's format list, return {quality_key: estimated_bytes}
    for every quality option the frontend can select (video qualities +
    "audio"), picking the same best-format-under-cap that the real
    download would use. Falls back to bitrate x duration when a format
    doesn't report filesize/filesize_approx (common for YouTube's DASH
    streams), so the estimate is available far more often."""
    formats = formats or []

    def fsize(f):
        size = f.get("filesize") or f.get("filesize_approx")
        if size:
            return size
        tbr = f.get("tbr")  # average bitrate in kbps
        if tbr and duration:
            return int(tbr * 1000 / 8 * duration)
        return 0

    video_formats = [f for f in formats if f.get("vcodec") not in (None, "none")]
    audio_formats = [f for f in formats if f.get("acodec") not in (None, "none")
                      and f.get("vcodec") in (None, "none")]
    best_a = max(audio_formats, key=lambda f: (f.get("abr") or 0, fsize(f)), default=None)
    a_size = fsize(best_a) if best_a else 0

    result = {}
    for key, cap in QUALITY_HEIGHT_CAPS:
        candidates = [f for f in video_formats if cap is None or (f.get("height") or 0) <= cap]
        best_v = max(candidates, key=lambda f: (f.get("height") or 0, fsize(f)), default=None)
        v_size = fsize(best_v) if best_v else 0
        per_video = (v_size + a_size) or None
        if per_video:
            result[key] = int(per_video)

    if a_size:
        result["audio"] = int(a_size)

    return result


def estimate_playlist_sizes(sample_video_id):
    """Best-effort estimate: fully inspect ONE sample video's formats and
    return its {quality_key: per_video_bytes} map. The frontend multiplies
    this by however many videos are currently selected and for whichever
    quality is chosen, so the estimate stays accurate as those change.
    Returns {} if it can't be determined."""
    if not sample_video_id:
        return {}
    try:
        opts = build_common_opts()
        opts.update({"skip_download": True, "noplaylist": True})
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={sample_video_id}", download=False)
        if not info:
            return {}
        return sizes_by_quality(info.get("formats"), info.get("duration"))
    except Exception:
        return {}


# ---- Custom download folder resolution -------------------------------------

def resolve_download_dir(custom_dir):
    """Validate/create a user-supplied absolute folder path. Returns
    (resolved_path, error_message)."""
    custom_dir = (custom_dir or "").strip()
    if not custom_dir:
        return DOWNLOAD_DIR, None
    if not os.path.isabs(custom_dir):
        return None, "Folder path must be an absolute path (e.g. C:\\Videos or /home/you/Videos)."
    if not os.path.isdir(custom_dir):
        try:
            os.makedirs(custom_dir, exist_ok=True)
        except Exception:
            return None, "Could not create that folder. Check the path and permissions."
    if not os.access(custom_dir, os.W_OK):
        return None, "That folder is not writable."
    return custom_dir, None


# ---- Locating an already-downloaded playlist folder (for resume/retry) ----

def _normalize_name(s):
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())


def find_playlist_folder(base_dir, playlist_title):
    if not playlist_title:
        return None
    guess = sanitize_filename(playlist_title, restricted=False)
    candidate = os.path.join(base_dir, guess)
    if os.path.isdir(candidate):
        return candidate
    try:
        target_norm = _normalize_name(playlist_title)
        if not target_norm:
            return None
        for name in os.listdir(base_dir):
            full = os.path.join(base_dir, name)
            if os.path.isdir(full) and _normalize_name(name) == target_norm:
                return full
    except Exception:
        pass
    return None


def existing_playlist_indices(base_dir, playlist_title):
    """Best-effort scan for videos already fully downloaded in a prior run
    (used so Resume/re-run doesn't re-flag completed videos as failed)."""
    folder = find_playlist_folder(base_dir, playlist_title)
    if not folder:
        return set()
    done = set()
    try:
        for fname in os.listdir(folder):
            if fname.endswith((".part", ".ytdl", ".temp", ".tmp")):
                continue
            m = re.match(r'^0*(\d+)\s*-\s', fname)
            if m:
                done.add(int(m.group(1)))
    except Exception:
        pass
    return done


# ---- Download item selection (whole playlist / range / hand-picked) -------

def compute_playlist_items(mode, start_index, end_index, selected_indices):
    if mode == "range":
        return f"{start_index}-{end_index}"
    if mode == "select":
        return ",".join(str(i) for i in sorted(set(selected_indices)))
    return None  # whole playlist


def compute_expected_indices(mode, start_index, end_index, selected_indices, total_videos):
    if mode == "range":
        return set(range(start_index, end_index + 1))
    if mode == "select":
        return set(selected_indices)
    if total_videos:
        return set(range(1, int(total_videos) + 1))
    return None


# --------------------------------------------------------------------------
# /fetch  -- metadata only, no media download
# --------------------------------------------------------------------------

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify(success=False, error="Please paste a YouTube video, playlist, or channel URL."), 400

    try:
        kind = classify_url(url)

        if kind in ("playlist", "channel"):
            fetch_url = normalize_channel_url(url) if kind == "channel" else url

            opts = build_common_opts()
            opts.update({
                "skip_download": True,
                "extract_flat": True,
                "ignoreerrors": True,
                "noplaylist": False,
            })
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(fetch_url, download=False)

            if not info:
                return jsonify(success=False, error="Could not fetch playlist/channel information."), 400

            entries = [e for e in (info.get("entries") or []) if e]
            if not entries:
                return jsonify(success=False, error="This playlist/channel is empty, private, or unavailable."), 400

            videos = []
            for idx, e in enumerate(entries, start=1):
                vid_id = e.get("id")
                videos.append({
                    "index": idx,
                    "id": vid_id,
                    "title": e.get("title") or "Untitled video",
                    "thumbnail": e.get("thumbnail") or best_thumbnail(e)
                                 or (f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg" if vid_id else None),
                    "duration": format_duration(e.get("duration")),
                })

            per_video_bytes_by_quality = estimate_playlist_sizes(videos[0]["id"] if videos else None)

            result = {
                "type": "playlist",
                "source": kind,  # "playlist" or "channel"
                "title": info.get("title") or "Untitled playlist",
                "uploader": info.get("uploader") or info.get("channel") or "Unknown",
                "thumbnail": best_thumbnail(info) or (videos[0]["thumbnail"] if videos else None),
                "video_count": len(videos),
                "videos": videos,
                # per-video estimated bytes for each quality option, e.g.
                # {"best": 123456, "1080": 98765, "720": 54321, "audio": 4321}
                # so the frontend can recompute the total live as the user
                # changes quality or how many videos are selected.
                "estimated_per_video_bytes_by_quality": per_video_bytes_by_quality,
                "original_url": fetch_url,
            }
            return jsonify(success=True, data=result)

        else:
            opts = build_common_opts()
            opts.update({
                "skip_download": True,
                "noplaylist": True,
            })
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if not info:
                return jsonify(success=False, error="Could not fetch video information."), 400

            heights = sorted(
                {f.get("height") for f in (info.get("formats") or []) if f.get("height")},
                reverse=True,
            )

            result = {
                "type": "video",
                "id": info.get("id"),
                "title": info.get("title") or "Untitled video",
                "uploader": info.get("uploader") or info.get("channel") or "Unknown",
                "duration": format_duration(info.get("duration")),
                "thumbnail": best_thumbnail(info),
                "available_qualities": heights,
                # estimated bytes for each quality option, e.g.
                # {"best": 123456, "1080": 98765, "720": 54321, "audio": 4321}
                "estimated_bytes_by_quality": sizes_by_quality(info.get("formats"), info.get("duration")),
                "original_url": url,
            }
            return jsonify(success=True, data=result)

    except DownloadError as e:
        return jsonify(success=False, error=clean_error(e)), 400
    except Exception as e:
        app.logger.exception("Unexpected error in /fetch")
        return jsonify(success=False, error=f"Unexpected error: {e}"), 500


# --------------------------------------------------------------------------
# /download -- starts a background download task
# --------------------------------------------------------------------------

def progress_hook(task, d):
    if task["cancel_event"].is_set():
        raise DownloadCancelled("Cancelled by user")

    info = d.get("info_dict") or {}
    playlist_index = info.get("playlist_index") or 1
    title = info.get("title") or os.path.basename(d.get("filename") or "") or "Unknown"
    status = d.get("status")
    downloaded = d.get("downloaded_bytes") or 0
    total = d.get("total_bytes") or d.get("total_bytes_estimate")
    speed = d.get("speed")
    eta = d.get("eta")
    percent = round((downloaded / total) * 100, 1) if total else None

    # Best quality often downloads video and audio as two separate files
    # before FFmpeg merges them. Tell the frontend which one this is so it
    # can show "Video stream" / "Audio stream" instead of looking like the
    # same video restarting from 0%.
    vcodec = info.get("vcodec")
    acodec = info.get("acodec")
    has_video = bool(vcodec and vcodec != "none")
    has_audio = bool(acodec and acodec != "none")
    if has_video and not has_audio:
        stream = "video"
    elif has_audio and not has_video:
        stream = "audio"
    else:
        stream = "combined"

    event = {
        "type": "progress",
        "status": status,
        "title": title,
        "playlist_index": playlist_index,
        "downloaded_bytes": downloaded,
        "total_bytes": total,
        "speed": speed,
        "eta": eta,
        "percent": percent,
        "filename": os.path.basename(d.get("filename")) if d.get("filename") else None,
        "stream": stream,
    }
    task["queue"].put(event)


def postprocessor_hook(task, d):
    info = d.get("info_dict") or {}
    playlist_index = info.get("playlist_index") or 1
    title = info.get("title") or "Unknown"
    status = d.get("status")
    pp_name = d.get("postprocessor") or ""
    if status == "started":
        task["queue"].put({
            "type": "postprocessing",
            "title": title,
            "playlist_index": playlist_index,
            "postprocessor": pp_name,
        })
    elif status == "finished":
        task["completed_indices"].add(playlist_index)
        task["queue"].put({
            "type": "video_complete",
            "title": title,
            "playlist_index": playlist_index,
        })


def build_download_opts(task, quality, audio_format, is_playlist, download_dir,
                         order_reverse, playlist_items_str):
    if is_playlist:
        outtmpl = os.path.join(download_dir, "%(playlist_title)s", "%(playlist_index)02d - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(download_dir, "%(title)s.%(ext)s")

    opts = build_common_opts()
    opts.update({
        "outtmpl": outtmpl,
        "noplaylist": not is_playlist,
        "ignoreerrors": True if is_playlist else False,
        "windowsfilenames": True,
        "nooverwrites": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 8,
        "progress_hooks": [lambda d: progress_hook(task, d)],
        "postprocessor_hooks": [lambda d: postprocessor_hook(task, d)],
    })

    if is_playlist:
        opts["playlistreverse"] = bool(order_reverse)
        if playlist_items_str:
            opts["playlist_items"] = playlist_items_str

    if ARIA2C_PATH and USE_ARIA2C_IF_AVAILABLE:
        opts["external_downloader"] = {"default": "aria2c"}
        opts["external_downloader_args"] = {
            "aria2c": ["-x", "16", "-s", "16", "-k", "1M", "--summary-interval=1"]
        }

    if quality == "audio":
        codec = audio_format if audio_format in VALID_AUDIO_FORMATS else "mp3"
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": codec,
            "preferredquality": "192",
        }]
    else:
        opts["format"] = QUALITY_FORMAT_MAP.get(quality, QUALITY_FORMAT_MAP["best"])

    return opts


def run_download(task_id, url, quality, audio_format, is_playlist, download_dir,
                  order_reverse, playlist_items_str, playlist_title):
    task = tasks[task_id]
    try:
        # Best-effort: if this playlist/channel was partly downloaded before
        # (previous run, or a Pause), report already-complete videos right
        # away instead of waiting for the whole task to finish.
        if is_playlist and playlist_title:
            for idx in existing_playlist_indices(download_dir, playlist_title):
                if task["expected_indices"] is None or idx in task["expected_indices"]:
                    if idx not in task["completed_indices"]:
                        task["completed_indices"].add(idx)
                        task["queue"].put({"type": "video_complete", "title": None, "playlist_index": idx})

        opts = build_download_opts(task, quality, audio_format, is_playlist, download_dir,
                                    order_reverse, playlist_items_str)
        task["status"] = "downloading"
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        failed = []
        if is_playlist and task["expected_indices"] is not None:
            failed = sorted(task["expected_indices"] - task["completed_indices"])

        task["status"] = "completed"
        task["queue"].put({"type": "done", "failed_indices": failed})
    except DownloadCancelled:
        task["status"] = "cancelled"
        task["queue"].put({"type": "cancelled"})
    except DownloadError as e:
        task["status"] = "error"
        msg = clean_error(e)
        task["error"] = msg
        task["queue"].put({"type": "error", "message": msg})
    except Exception as e:
        app.logger.exception("Unexpected error during download")
        task["status"] = "error"
        task["error"] = str(e)
        task["queue"].put({"type": "error", "message": f"Unexpected error: {e}"})


@app.route("/download", methods=["POST"])
def download():
    if not FFMPEG_PATH:
        return jsonify(success=False, error="FFmpeg was not found on this system. Install FFmpeg and make sure it is on PATH."), 400

    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    quality = data.get("quality", "best")
    audio_format = data.get("audio_format", "mp3")
    is_playlist = bool(data.get("is_playlist"))
    playlist_title = data.get("playlist_title")
    mode = data.get("mode", "whole")
    total_videos = data.get("total_videos")
    start_index = data.get("start_index")
    end_index = data.get("end_index")
    selected_indices = data.get("selected_indices") or []
    order_reverse = data.get("order") == "reverse"
    download_dir_input = data.get("download_dir", "")

    if not url:
        return jsonify(success=False, error="Missing URL."), 400

    if mode not in VALID_MODES:
        mode = "whole"

    download_dir, dir_err = resolve_download_dir(download_dir_input)
    if dir_err:
        return jsonify(success=False, error=dir_err), 400

    if is_playlist and mode == "range":
        try:
            start_index = int(start_index)
            end_index = int(end_index)
        except (TypeError, ValueError):
            return jsonify(success=False, error="Range indices must be numbers."), 400
        if start_index < 1:
            return jsonify(success=False, error="Starting index must be at least 1."), 400
        if end_index < start_index:
            return jsonify(success=False, error="Ending index must be greater than or equal to starting index."), 400
        if total_videos and end_index > int(total_videos):
            return jsonify(success=False, error=f"Ending index cannot exceed the playlist size ({total_videos})."), 400

    if is_playlist and mode == "select":
        try:
            selected_indices = sorted({int(i) for i in selected_indices})
        except (TypeError, ValueError):
            return jsonify(success=False, error="Selected video indices must be numbers."), 400
        if not selected_indices:
            return jsonify(success=False, error="Please select at least one video."), 400

    playlist_items_str = compute_playlist_items(mode, start_index, end_index, selected_indices) if is_playlist else None
    expected_indices = compute_expected_indices(mode, start_index, end_index, selected_indices, total_videos) if is_playlist else None

    task_id = uuid.uuid4().hex
    task = {
        "id": task_id,
        "status": "starting",
        "queue": queue.Queue(),
        "cancel_event": threading.Event(),
        "error": None,
        "completed_indices": set(),
        "expected_indices": expected_indices,
    }
    with tasks_lock:
        tasks[task_id] = task

    thread = threading.Thread(
        target=run_download,
        args=(task_id, url, quality, audio_format, is_playlist, download_dir,
              order_reverse, playlist_items_str, playlist_title),
        daemon=True,
    )
    thread.start()

    return jsonify(success=True, task_id=task_id)


# --------------------------------------------------------------------------
# /progress/<task_id> -- Server-Sent Events stream
# --------------------------------------------------------------------------

@app.route("/progress/<task_id>")
def progress(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify(success=False, error="Unknown task id."), 404

    def generate():
        q = task["queue"]
        yield "retry: 2000\n\n"
        while True:
            try:
                event = q.get(timeout=15)
            except queue.Empty:
                yield ": heartbeat\n\n"
                continue
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") in ("done", "error", "cancelled"):
                break

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --------------------------------------------------------------------------
# /cancel/<task_id>   (also used to implement Pause: same clean stop, the
# frontend decides whether that means "Cancelled" or "Paused")
# --------------------------------------------------------------------------

@app.route("/cancel/<task_id>", methods=["POST"])
def cancel(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify(success=False, error="Unknown task id."), 404
    task["cancel_event"].set()
    return jsonify(success=True)


# --------------------------------------------------------------------------
# /diskspace -- free space on the (default or custom) download volume
# --------------------------------------------------------------------------

@app.route("/diskspace")
def diskspace():
    custom_dir = request.args.get("dir", "")
    resolved, err = resolve_download_dir(custom_dir)
    if err:
        return jsonify(success=False, error=err), 400
    try:
        usage = shutil.disk_usage(resolved)
        return jsonify(success=True, free_bytes=usage.free, total_bytes=usage.total)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


# --------------------------------------------------------------------------
# /deps -- report which required executables were found
# --------------------------------------------------------------------------

@app.route("/deps")
def deps():
    return jsonify({
        "ffmpeg": bool(FFMPEG_PATH),
        "aria2c": bool(ARIA2C_PATH),
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    missing = []
    if not FFMPEG_PATH:
        missing.append("ffmpeg")
    if missing:
        print(f"WARNING: could not find on PATH: {', '.join(missing)}. Merging/audio conversion will fail until this is fixed.")
    if not ARIA2C_PATH:
        print("NOTE: aria2c not found on PATH — falling back to yt-dlp's native downloader.")

    print("Starting server at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
