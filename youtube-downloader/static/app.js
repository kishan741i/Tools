(() => {
  "use strict";

  // ---------- DOM ----------
  const urlInput = document.getElementById("urlInput");
  const fetchBtn = document.getElementById("fetchBtn");
  const fetchLoading = document.getElementById("fetchLoading");
  const errorBox = document.getElementById("errorBox");
  const depsWarning = document.getElementById("depsWarning");
  const themeToggle = document.getElementById("themeToggle");
  const soundToggle = document.getElementById("soundToggle");

  const infoSection = document.getElementById("infoSection");
  const videoInfo = document.getElementById("videoInfo");
  const videoThumb = document.getElementById("videoThumb");
  const videoTitle = document.getElementById("videoTitle");
  const videoUploader = document.getElementById("videoUploader");
  const videoDuration = document.getElementById("videoDuration");
  const videoQualities = document.getElementById("videoQualities");
  const videoEstRow = document.getElementById("videoEstRow");
  const videoEstSize = document.getElementById("videoEstSize");

  const playlistInfo = document.getElementById("playlistInfo");
  const playlistThumb = document.getElementById("playlistThumb");
  const playlistTitle = document.getElementById("playlistTitle");
  const playlistUploader = document.getElementById("playlistUploader");
  const playlistCount = document.getElementById("playlistCount");
  const playlistChannelTag = document.getElementById("playlistChannelTag");
  const playlistEstRow = document.getElementById("playlistEstRow");
  const playlistEstSize = document.getElementById("playlistEstSize");
  const playlistToolsRow = document.getElementById("playlistToolsRow");
  const playlistSearch = document.getElementById("playlistSearch");
  const exportCsvBtn = document.getElementById("exportCsvBtn");
  const exportTxtBtn = document.getElementById("exportTxtBtn");
  const playlistListHead = document.getElementById("playlistListHead");
  const playlistVideoList = document.getElementById("playlistVideoList");

  const qualitySelect = document.getElementById("qualitySelect");
  const audioFormatRow = document.getElementById("audioFormatRow");
  const audioFormatSelect = document.getElementById("audioFormatSelect");
  const orderRow = document.getElementById("orderRow");
  const orderSelect = document.getElementById("orderSelect");
  const modeRow = document.getElementById("modeRow");
  const modeSelect = document.getElementById("modeSelect");
  const rangeInputsRow = document.getElementById("rangeInputsRow");
  const startIndexInput = document.getElementById("startIndex");
  const endIndexInput = document.getElementById("endIndex");
  const selectControlsRow = document.getElementById("selectControlsRow");
  const selectAllBtn = document.getElementById("selectAllBtn");
  const selectNoneBtn = document.getElementById("selectNoneBtn");
  const selectedCount = document.getElementById("selectedCount");
  const downloadDirInput = document.getElementById("downloadDirInput");
  const downloadBtn = document.getElementById("downloadBtn");

  const progressSection = document.getElementById("progressSection");
  const progressTitle = document.getElementById("progressTitle");
  const overallStatus = document.getElementById("overallStatus");
  const pauseBtn = document.getElementById("pauseBtn");
  const resumeBtn = document.getElementById("resumeBtn");
  const cancelBtn = document.getElementById("cancelBtn");
  const singleProgress = document.getElementById("singleProgress");
  const singleFilename = document.getElementById("singleFilename");
  const singleStage = document.getElementById("singleStage");
  const singleBar = document.getElementById("singleBar");
  const singlePercent = document.getElementById("singlePercent");
  const singleSize = document.getElementById("singleSize");
  const singleSpeed = document.getElementById("singleSpeed");
  const singleEta = document.getElementById("singleEta");
  const playlistProgress = document.getElementById("playlistProgress");

  // ---------- State ----------
  let fetchedData = null;   // last successful /fetch response data
  let currentTaskId = null;
  let eventSource = null;
  let playlistRowEls = {};  // index -> DOM element (progress rows)
  let completedCount = 0;
  let activeRangeCount = 0;
  let failedIndicesSet = new Set();
  let downloadState = "idle"; // idle | running | paused | done | error | cancelled
  let pauseRequested = false;
  let lastPayload = null;   // payload of the most recently started/resumed main task

  // ---------- Theme ----------
  let savedTheme = localStorage.getItem("ytdl_theme") || "dark";
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    themeToggle.textContent = t === "light" ? "🌙" : "☀️";
  }
  applyTheme(savedTheme);
  themeToggle.addEventListener("click", () => {
    savedTheme = savedTheme === "dark" ? "light" : "dark";
    localStorage.setItem("ytdl_theme", savedTheme);
    applyTheme(savedTheme);
  });

  // ---------- Sound ----------
  let soundEnabled = localStorage.getItem("ytdl_sound") !== "0";
  function applySoundIcon() {
    soundToggle.textContent = soundEnabled ? "🔔" : "🔕";
    soundToggle.classList.toggle("muted-icon", !soundEnabled);
  }
  applySoundIcon();
  soundToggle.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    localStorage.setItem("ytdl_sound", soundEnabled ? "1" : "0");
    applySoundIcon();
  });
  function playCompletionBeep() {
    if (!soundEnabled) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
      osc.onended = () => ctx.close();
    } catch (e) {
      // ignore — audio not available
    }
  }

  // ---------- Clipboard auto-paste ----------
  async function tryAutoPasteFromClipboard() {
    if (!navigator.clipboard || !navigator.clipboard.readText) return;
    if (urlInput.value.trim()) return;
    try {
      const text = await navigator.clipboard.readText();
      if (text && /(?:youtube\.com|youtu\.be)\//i.test(text) && !urlInput.value.trim()) {
        urlInput.value = text.trim();
      }
    } catch (e) {
      // permission denied / blocked — silently ignore, browsers vary a lot here
    }
  }
  window.addEventListener("load", tryAutoPasteFromClipboard);
  window.addEventListener("focus", tryAutoPasteFromClipboard);

  // ---------- Helpers ----------
  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }
  function hideError() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
  }

  function formatBytes(bytes) {
    if (bytes === null || bytes === undefined) return "Unknown";
    if (bytes === 0) return "0 B";
    const units = ["B", "KB", "MB", "GB"];
    let i = 0;
    let val = bytes;
    while (val >= 1024 && i < units.length - 1) {
      val /= 1024;
      i++;
    }
    return `${val.toFixed(val < 10 && i > 0 ? 2 : 1)} ${units[i]}`;
  }

  function formatSpeed(bytesPerSec) {
    if (!bytesPerSec) return "--";
    return formatBytes(bytesPerSec) + "/s";
  }

  function formatEta(seconds) {
    if (seconds === null || seconds === undefined) return "--:--:--";
    seconds = Math.max(0, Math.round(seconds));
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
  }

  function isPlaylistNow() {
    return !!(fetchedData && fetchedData.type === "playlist");
  }

  function resetOptionsUI() {
    qualitySelect.value = "best";
    audioFormatRow.classList.add("hidden");
    modeSelect.value = "whole";
    rangeInputsRow.classList.add("hidden");
    selectControlsRow.classList.add("hidden");
    orderSelect.value = "default";
    downloadDirInput.value = "";
  }

  // ---------- Dependency check ----------
  async function checkDeps() {
    try {
      const res = await fetch("/deps");
      const data = await res.json();
      const missing = [];
      if (!data.ffmpeg) missing.push("FFmpeg");
      if (missing.length) {
        depsWarning.textContent = `Warning: ${missing.join(", ")} not found on PATH. Merging and audio conversion will fail until this is fixed.`;
        depsWarning.classList.remove("hidden");
      }
    } catch (e) {
      // non-fatal
    }
  }
  checkDeps();

  // ---------- Fetch metadata ----------
  fetchBtn.addEventListener("click", doFetch);
  urlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") doFetch();
  });

  async function doFetch() {
    const url = urlInput.value.trim();
    hideError();
    infoSection.classList.add("hidden");
    progressSection.classList.add("hidden");
    if (!url) {
      showError("Please paste a YouTube video, playlist, or channel URL.");
      return;
    }

    fetchBtn.disabled = true;
    fetchLoading.classList.remove("hidden");

    try {
      const res = await fetch("/fetch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!data.success) {
        showError(data.error || "Failed to fetch information.");
        return;
      }
      fetchedData = data.data;
      renderInfo(fetchedData);
    } catch (e) {
      showError("Network error while contacting the server.");
    } finally {
      fetchBtn.disabled = false;
      fetchLoading.classList.add("hidden");
    }
  }

  function renderInfo(data) {
    resetOptionsUI();
    infoSection.classList.remove("hidden");
    playlistSearch.value = "";

    if (data.type === "video") {
      videoInfo.classList.remove("hidden");
      playlistInfo.classList.add("hidden");
      playlistToolsRow.classList.add("hidden");
      playlistListHead.classList.add("hidden");
      playlistVideoList.classList.add("hidden");
      orderRow.classList.add("hidden");
      modeRow.classList.add("hidden");
      rangeInputsRow.classList.add("hidden");
      selectControlsRow.classList.add("hidden");

      videoThumb.src = data.thumbnail || "";
      videoTitle.textContent = data.title;
      videoUploader.textContent = data.uploader;
      videoDuration.textContent = data.duration || "Unknown";
      videoQualities.textContent = data.available_qualities && data.available_qualities.length
        ? data.available_qualities.map((h) => `${h}p`).join(", ")
        : "Unknown";
    } else {
      playlistInfo.classList.remove("hidden");
      videoInfo.classList.add("hidden");
      playlistToolsRow.classList.remove("hidden");
      playlistListHead.classList.remove("hidden");
      playlistVideoList.classList.remove("hidden");
      orderRow.classList.remove("hidden");
      modeRow.classList.remove("hidden");

      playlistThumb.src = data.thumbnail || "";
      playlistTitle.textContent = data.title;
      playlistUploader.textContent = data.uploader;
      playlistCount.textContent = data.video_count;
      playlistChannelTag.classList.toggle("hidden", data.source !== "channel");

      startIndexInput.value = 1;
      startIndexInput.min = 1;
      startIndexInput.max = data.video_count;
      endIndexInput.value = data.video_count;
      endIndexInput.min = 1;
      endIndexInput.max = data.video_count;

      playlistVideoList.innerHTML = "";
      playlistVideoList.classList.remove("select-mode");
      playlistListHead.classList.remove("select-mode");
      data.videos.forEach((v) => {
        const row = document.createElement("div");
        row.className = "pl-item";
        row.innerHTML = `
          <input type="checkbox" class="pl-checkbox" data-index="${v.index}">
          <span class="pl-index">${v.index}</span>
          <img class="pl-thumb" src="${v.thumbnail || ""}" alt="">
          <span class="pl-title" title="${escapeHtml(v.title)}">${escapeHtml(v.title)}</span>
          <span class="pl-duration">${v.duration || "Unknown"}</span>
        `;
        playlistVideoList.appendChild(row);
      });
      updateSelectedCount();
    }
    updateEstimatedSize();
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  // ---------- Playlist search/filter ----------
  playlistSearch.addEventListener("input", () => {
    const q = playlistSearch.value.trim().toLowerCase();
    playlistVideoList.querySelectorAll(".pl-item").forEach((row) => {
      const title = row.querySelector(".pl-title").textContent.toLowerCase();
      row.classList.toggle("hidden", !!q && !title.includes(q));
    });
  });

  // ---------- Select-specific-videos checkboxes ----------
  function updateSelectedCount() {
    const n = playlistVideoList.querySelectorAll(".pl-checkbox:checked").length;
    selectedCount.textContent = `${n} selected`;
  }
  playlistVideoList.addEventListener("change", (e) => {
    if (e.target.classList.contains("pl-checkbox")) {
      updateSelectedCount();
      updateEstimatedSize();
    }
  });
  selectAllBtn.addEventListener("click", () => {
    playlistVideoList.querySelectorAll(".pl-checkbox").forEach((cb) => { cb.checked = true; });
    updateSelectedCount();
    updateEstimatedSize();
  });
  selectNoneBtn.addEventListener("click", () => {
    playlistVideoList.querySelectorAll(".pl-checkbox").forEach((cb) => { cb.checked = false; });
    updateSelectedCount();
    updateEstimatedSize();
  });

  // ---------- Export playlist list ----------
  function sanitizeFileName(name) {
    return (name || "playlist").replace(/[\\/:*?"<>|]/g, "_").slice(0, 150);
  }
  function csvEscape(v) {
    const s = String(v === null || v === undefined ? "" : v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function downloadBlob(content, mime, filename) {
    const blob = new Blob([content], { type: mime });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }
  exportCsvBtn.addEventListener("click", () => {
    if (!fetchedData || fetchedData.type !== "playlist") return;
    const rows = [["Index", "Title", "Duration", "Video URL"]];
    fetchedData.videos.forEach((v) => rows.push([
      v.index, v.title, v.duration || "", v.id ? `https://www.youtube.com/watch?v=${v.id}` : "",
    ]));
    const content = rows.map((r) => r.map(csvEscape).join(",")).join("\r\n");
    downloadBlob(content, "text/csv", `${sanitizeFileName(fetchedData.title)}.csv`);
  });
  exportTxtBtn.addEventListener("click", () => {
    if (!fetchedData || fetchedData.type !== "playlist") return;
    const content = fetchedData.videos.map((v) =>
      `${v.index}. ${v.title}${v.duration ? " (" + v.duration + ")" : ""}${v.id ? " - https://www.youtube.com/watch?v=" + v.id : ""}`
    ).join("\n");
    downloadBlob(content, "text/plain", `${sanitizeFileName(fetchedData.title)}.txt`);
  });

  // ---------- Dynamic estimated-size calculation ----------
  // Recomputed live as the user changes quality, download mode, the
  // range inputs, or which videos are checked — never a fixed number
  // fetched once from the server.
  function getSelectedVideoCount() {
    if (!fetchedData || fetchedData.type !== "playlist") return 0;
    const mode = modeSelect.value;
    if (mode === "whole") return fetchedData.video_count;
    if (mode === "range") {
      const start = parseInt(startIndexInput.value, 10);
      const end = parseInt(endIndexInput.value, 10);
      if (isNaN(start) || isNaN(end) || end < start) return 0;
      const clampedStart = Math.max(1, start);
      const clampedEnd = Math.min(fetchedData.video_count, end);
      return Math.max(0, clampedEnd - clampedStart + 1);
    }
    if (mode === "select") {
      return playlistVideoList.querySelectorAll(".pl-checkbox:checked").length;
    }
    return 0;
  }

  // Returns the current best-effort total size estimate in bytes (or null
  // if unknown), based on the currently selected quality + video count.
  function currentEstimatedTotalBytes() {
    if (!fetchedData) return null;
    const quality = qualitySelect.value;
    if (fetchedData.type === "video") {
      const map = fetchedData.estimated_bytes_by_quality || {};
      const perVideo = map[quality] ?? map.best ?? null;
      return perVideo || null;
    }
    if (fetchedData.type === "playlist") {
      const map = fetchedData.estimated_per_video_bytes_by_quality || {};
      const perVideo = map[quality] ?? map.best ?? null;
      const count = getSelectedVideoCount();
      if (!perVideo || !count) return null;
      return perVideo * count;
    }
    return null;
  }

  function updateEstimatedSize() {
    if (!fetchedData) return;
    const qualityLabel = qualitySelect.options[qualitySelect.selectedIndex]
      ? qualitySelect.options[qualitySelect.selectedIndex].text
      : "";

    if (fetchedData.type === "playlist") {
      const count = getSelectedVideoCount();
      const total = currentEstimatedTotalBytes();
      if (total && count) {
        playlistEstSize.textContent =
          `~${formatBytes(total)} for ${count} video${count === 1 ? "" : "s"} ` +
          `(${qualityLabel}, rough estimate based on one sample video)`;
        playlistEstRow.classList.remove("hidden");
      } else {
        playlistEstRow.classList.add("hidden");
      }
    } else if (fetchedData.type === "video") {
      const total = currentEstimatedTotalBytes();
      if (total) {
        videoEstSize.textContent = `~${formatBytes(total)} (${qualityLabel}, rough estimate)`;
        videoEstRow.classList.remove("hidden");
      } else {
        videoEstRow.classList.add("hidden");
      }
    }
  }

  // ---------- Options interactivity ----------
  qualitySelect.addEventListener("change", () => {
    audioFormatRow.classList.toggle("hidden", qualitySelect.value !== "audio");
    updateEstimatedSize();
  });

  modeSelect.addEventListener("change", () => {
    const mode = modeSelect.value;
    rangeInputsRow.classList.toggle("hidden", mode !== "range");
    selectControlsRow.classList.toggle("hidden", mode !== "select");
    playlistVideoList.classList.toggle("select-mode", mode === "select");
    playlistListHead.classList.toggle("select-mode", mode === "select");
    updateEstimatedSize();
  });

  startIndexInput.addEventListener("input", updateEstimatedSize);
  endIndexInput.addEventListener("input", updateEstimatedSize);

  // ---------- Download state machine ----------
  function setDownloadState(state) {
    downloadState = state;
    pauseBtn.classList.toggle("hidden", state !== "running");
    resumeBtn.classList.toggle("hidden", state !== "paused");
    cancelBtn.disabled = !(state === "running" || state === "paused");
    downloadBtn.disabled = (state === "running" || state === "paused");
    pauseBtn.disabled = state !== "running";
  }
  setDownloadState("idle");

  // ---------- Download ----------
  downloadBtn.addEventListener("click", startDownload);

  function validateRange() {
    if (!fetchedData || fetchedData.type !== "playlist" || modeSelect.value !== "range") return true;
    const start = parseInt(startIndexInput.value, 10);
    const end = parseInt(endIndexInput.value, 10);
    const total = fetchedData.video_count;
    if (isNaN(start) || start < 1) {
      showError("Starting index must be 1 or greater.");
      return false;
    }
    if (isNaN(end) || end < start) {
      showError("Ending index must be greater than or equal to starting index.");
      return false;
    }
    if (end > total) {
      showError(`Ending index cannot exceed the playlist size (${total}).`);
      return false;
    }
    return true;
  }

  function validateSelection() {
    if (!fetchedData || fetchedData.type !== "playlist" || modeSelect.value !== "select") return true;
    const n = playlistVideoList.querySelectorAll(".pl-checkbox:checked").length;
    if (n === 0) {
      showError("Please select at least one video.");
      return false;
    }
    return true;
  }

  async function checkDiskSpaceWarning(downloadDir) {
    const estimatedBytes = currentEstimatedTotalBytes();
    if (!estimatedBytes) return true;
    try {
      const qs = downloadDir ? `?dir=${encodeURIComponent(downloadDir)}` : "";
      const res = await fetch(`/diskspace${qs}`);
      const data = await res.json();
      if (!data.success) return true; // non-blocking — just skip the check
      if (data.free_bytes < estimatedBytes) {
        return confirm(
          `Estimated download size is ~${formatBytes(estimatedBytes)}, ` +
          `but only ~${formatBytes(data.free_bytes)} is free on that drive. Continue anyway?`
        );
      }
      return true;
    } catch (e) {
      return true; // non-blocking
    }
  }

  function buildPayload() {
    const isPlaylist = isPlaylistNow();
    const mode = isPlaylist ? modeSelect.value : "whole";
    const selectedIndices = mode === "select"
      ? Array.from(playlistVideoList.querySelectorAll(".pl-checkbox:checked")).map((cb) => parseInt(cb.dataset.index, 10))
      : [];
    return {
      url: fetchedData.original_url,
      quality: qualitySelect.value,
      audio_format: audioFormatSelect.value,
      is_playlist: isPlaylist,
      playlist_title: isPlaylist ? fetchedData.title : null,
      mode,
      total_videos: isPlaylist ? fetchedData.video_count : null,
      start_index: mode === "range" ? parseInt(startIndexInput.value, 10) : null,
      end_index: mode === "range" ? parseInt(endIndexInput.value, 10) : null,
      selected_indices: selectedIndices,
      order: isPlaylist ? orderSelect.value : "default",
      download_dir: downloadDirInput.value.trim(),
    };
  }

  async function startDownload() {
    if (!fetchedData) return;
    hideError();
    if (!validateRange()) return;
    if (!validateSelection()) return;

    const payload = buildPayload();

    const proceed = await checkDiskSpaceWarning(payload.download_dir);
    if (!proceed) return;

    downloadBtn.disabled = true;
    try {
      const res = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data.success) {
        showError(data.error || "Failed to start download.");
        downloadBtn.disabled = false;
        return;
      }
      lastPayload = payload;
      currentTaskId = data.task_id;
      setupProgressUI(payload.is_playlist, payload);
      setDownloadState("running");
      connectSSE(currentTaskId);
    } catch (e) {
      showError("Network error while starting the download.");
      downloadBtn.disabled = false;
    }
  }

  function itemIndicesForPayload(payload) {
    if (payload.mode === "range") {
      const out = [];
      for (let i = payload.start_index; i <= payload.end_index; i++) out.push(i);
      return out;
    }
    if (payload.mode === "select") {
      return payload.selected_indices.slice();
    }
    return fetchedData.videos.map((v) => v.index);
  }

  function setupProgressUI(isPlaylist, payload) {
    progressSection.classList.remove("hidden");
    overallStatus.textContent = "Starting...";
    progressTitle.textContent = isPlaylist ? "Downloading Playlist" : "Downloading Video";
    playlistRowEls = {};
    completedCount = 0;
    failedIndicesSet = new Set();

    if (isPlaylist) {
      singleProgress.classList.add("hidden");
      playlistProgress.classList.remove("hidden");
      playlistProgress.innerHTML = "";

      const indices = itemIndicesForPayload(payload);
      activeRangeCount = indices.length;

      indices.forEach((idx) => {
        const video = fetchedData.videos.find((v) => v.index === idx);
        const row = document.createElement("div");
        row.className = "pl-progress-item";
        row.innerHTML = `
          <div class="row1">
            <span class="row1-left"><span class="status-icon status-pending">○</span><span class="pl-title-text">${escapeHtml(video ? video.title : "Video " + idx)}</span></span>
            <span class="pct">--</span>
          </div>
          <p class="stage-label stage-tag hidden"></p>
          <div class="progress-bar-outer"><div class="progress-bar-inner" style="width:0%"></div></div>
          <div class="progress-stats">
            <span class="size">-- / --</span>
            <span class="speed">--</span>
            <span class="eta">--:--:--</span>
          </div>
        `;
        playlistProgress.appendChild(row);
        playlistRowEls[idx] = row;
      });

      overallStatus.textContent = `0 / ${activeRangeCount} videos completed`;
    } else {
      playlistProgress.classList.add("hidden");
      singleProgress.classList.remove("hidden");
      singleFilename.textContent = fetchedData.title || "";
      singleStage.textContent = "";
      singleBar.style.width = "0%";
      singlePercent.textContent = "0%";
      singleSize.textContent = "-- / --";
      singleSpeed.textContent = "--";
      singleEta.textContent = "--:--:--";
    }
  }

  function connectSSE(taskId) {
    if (eventSource) {
      eventSource.close();
    }
    eventSource = new EventSource(`/progress/${taskId}`);

    eventSource.onmessage = (evt) => {
      let data;
      try {
        data = JSON.parse(evt.data);
      } catch (e) {
        return;
      }
      handleMainEvent(data);
    };

    eventSource.onerror = () => {
      eventSource.close();
    };
  }

  // ---------- Shared row-update helpers (used by both the main task and retries) ----------
  function streamLabel(stream) {
    if (stream === "video") return "Downloading video stream...";
    if (stream === "audio") return "Downloading audio stream...";
    return "";
  }

  function updateSingleProgress(evt) {
    const pct = evt.percent !== null && evt.percent !== undefined ? evt.percent : 0;
    singleBar.style.width = `${Math.min(pct, 100)}%`;
    singlePercent.textContent = evt.percent !== null && evt.percent !== undefined ? `${evt.percent}%` : "--";
    singleSize.textContent = `${formatBytes(evt.downloaded_bytes)} / ${evt.total_bytes ? formatBytes(evt.total_bytes) : "Unknown"}`;
    singleSpeed.textContent = formatSpeed(evt.speed);
    singleEta.textContent = formatEta(evt.eta);
    singleStage.textContent = streamLabel(evt.stream);
    if (evt.filename) singleFilename.textContent = evt.filename;
  }

  function updatePlaylistRowProgress(evt) {
    const row = playlistRowEls[evt.playlist_index];
    if (!row) return;
    const icon = row.querySelector(".status-icon");
    if (icon.textContent === "○" || icon.textContent === "✕") {
      icon.className = "status-icon status-active";
      icon.textContent = "↓";
      const retryBtnEl = row.querySelector(".retry-btn");
      if (retryBtnEl) retryBtnEl.remove();
      failedIndicesSet.delete(evt.playlist_index);
    }
    const stageEl = row.querySelector(".stage-tag");
    const label = streamLabel(evt.stream);
    if (label) {
      stageEl.textContent = label;
      stageEl.classList.remove("hidden");
    } else {
      stageEl.classList.add("hidden");
    }
    const pct = evt.percent !== null && evt.percent !== undefined ? evt.percent : 0;
    row.querySelector(".progress-bar-inner").style.width = `${Math.min(pct, 100)}%`;
    row.querySelector(".pct").textContent = evt.percent !== null && evt.percent !== undefined ? `${evt.percent}%` : "--";
    row.querySelector(".size").textContent = `${formatBytes(evt.downloaded_bytes)} / ${evt.total_bytes ? formatBytes(evt.total_bytes) : "Unknown"}`;
    row.querySelector(".speed").textContent = formatSpeed(evt.speed);
    row.querySelector(".eta").textContent = formatEta(evt.eta);
  }

  function updatePlaylistRowProcessing(evt) {
    const row = playlistRowEls[evt.playlist_index];
    if (!row) return;
    row.querySelector(".status-icon").className = "status-icon status-active";
    row.querySelector(".status-icon").textContent = "↓";
    row.querySelector(".pct").textContent = "Processing";
    const label = evt.postprocessor && evt.postprocessor.toLowerCase().includes("audio")
      ? "Converting audio..."
      : "Merging video & audio...";
    const stageEl = row.querySelector(".stage-tag");
    stageEl.textContent = label;
    stageEl.classList.remove("hidden");
  }

  function markRowCompleted(idx) {
    const row = playlistRowEls[idx];
    if (!row) return;
    const icon = row.querySelector(".status-icon");
    if (icon.textContent !== "✓") {
      completedCount++;
    }
    failedIndicesSet.delete(idx);
    icon.className = "status-icon status-completed";
    icon.textContent = "✓";
    row.querySelector(".pct").textContent = "Completed";
    row.querySelector(".progress-bar-inner").style.width = "100%";
    const stageEl = row.querySelector(".stage-tag");
    stageEl.classList.add("hidden");
    stageEl.textContent = "";
    const retryBtnEl = row.querySelector(".retry-btn");
    if (retryBtnEl) retryBtnEl.remove();
  }

  function markRowFailed(idx) {
    const row = playlistRowEls[idx];
    if (!row) return;
    if (!failedIndicesSet.has(idx)) failedIndicesSet.add(idx);
    const icon = row.querySelector(".status-icon");
    icon.className = "status-icon status-failed";
    icon.textContent = "✕";
    row.querySelector(".pct").textContent = "Failed";
    const stageEl = row.querySelector(".stage-tag");
    stageEl.classList.add("hidden");
    if (!row.querySelector(".retry-btn")) {
      const btn = document.createElement("button");
      btn.className = "retry-btn";
      btn.textContent = "Retry";
      btn.addEventListener("click", () => retryVideo(idx));
      row.querySelector(".row1").appendChild(btn);
    }
  }

  // ---------- Main task SSE handling ----------
  function handleMainEvent(evt) {
    const isPlaylist = isPlaylistNow();

    if (evt.type === "progress") {
      overallStatus.textContent = isPlaylist
        ? statusLine()
        : "Downloading...";
      if (isPlaylist) updatePlaylistRowProgress(evt);
      else updateSingleProgress(evt);
    } else if (evt.type === "postprocessing") {
      if (isPlaylist) {
        updatePlaylistRowProcessing(evt);
      } else {
        const label = evt.postprocessor && evt.postprocessor.toLowerCase().includes("audio")
          ? "Converting audio..."
          : "Merging video & audio...";
        singlePercent.textContent = "Processing";
        singleStage.textContent = label;
      }
    } else if (evt.type === "video_complete") {
      if (isPlaylist) {
        markRowCompleted(evt.playlist_index);
        overallStatus.textContent = statusLine();
      }
    } else if (evt.type === "done") {
      const failed = evt.failed_indices || [];
      if (isPlaylist) {
        failed.forEach((idx) => markRowFailed(idx));
        overallStatus.textContent = statusLine() + (failed.length ? ` — ${failed.length} failed` : "");
      } else {
        overallStatus.textContent = "Download completed.";
        singleBar.style.width = "100%";
        singlePercent.textContent = "100%";
        singleStage.textContent = "";
      }
      progressTitle.textContent = failed.length ? "Download Finished (some failed)" : "Download Complete";
      setDownloadState("done");
      playCompletionBeep();
    } else if (evt.type === "cancelled") {
      if (pauseRequested) {
        pauseRequested = false;
        setDownloadState("paused");
        overallStatus.textContent = isPlaylist ? `Paused — ${statusLine()}` : "Paused.";
        progressTitle.textContent = "Download Paused";
      } else {
        setDownloadState("cancelled");
        overallStatus.textContent = "Cancelled.";
        progressTitle.textContent = "Download Cancelled";
      }
    } else if (evt.type === "error") {
      setDownloadState("error");
      overallStatus.textContent = "Error: " + evt.message;
      progressTitle.textContent = "Download Failed";
    }
  }

  function statusLine() {
    let s = `${completedCount} / ${activeRangeCount} videos completed`;
    return s;
  }

  // ---------- Pause / Resume / Cancel ----------
  pauseBtn.addEventListener("click", async () => {
    if (downloadState !== "running" || !currentTaskId) return;
    pauseRequested = true;
    pauseBtn.disabled = true;
    try {
      await fetch(`/cancel/${currentTaskId}`, { method: "POST" });
    } catch (e) {
      // ignore
    }
  });

  resumeBtn.addEventListener("click", async () => {
    if (!lastPayload) return;
    resumeBtn.disabled = true;
    overallStatus.textContent = "Resuming...";
    try {
      const res = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lastPayload),
      });
      const data = await res.json();
      if (!data.success) {
        showError(data.error || "Failed to resume.");
        resumeBtn.disabled = false;
        return;
      }
      currentTaskId = data.task_id;
      progressTitle.textContent = isPlaylistNow() ? "Downloading Playlist" : "Downloading Video";
      setDownloadState("running");
      connectSSE(currentTaskId); // playlistRowEls / completedCount are preserved on purpose
    } catch (e) {
      showError("Network error while resuming.");
      resumeBtn.disabled = false;
    }
  });

  cancelBtn.addEventListener("click", async () => {
    if (downloadState === "paused") {
      setDownloadState("cancelled");
      overallStatus.textContent = "Cancelled.";
      progressTitle.textContent = "Download Cancelled";
      return;
    }
    if (downloadState !== "running" || !currentTaskId) return;
    cancelBtn.disabled = true;
    try {
      await fetch(`/cancel/${currentTaskId}`, { method: "POST" });
    } catch (e) {
      // ignore
    }
  });

  // ---------- Retry a single failed playlist video ----------
  async function retryVideo(idx) {
    if (!lastPayload) return;
    const row = playlistRowEls[idx];
    if (row) {
      const icon = row.querySelector(".status-icon");
      icon.className = "status-icon status-active";
      icon.textContent = "↓";
      row.querySelector(".pct").textContent = "--";
      const retryBtnEl = row.querySelector(".retry-btn");
      if (retryBtnEl) retryBtnEl.remove();
    }
    const payload = {
      ...lastPayload,
      mode: "select",
      selected_indices: [idx],
      start_index: null,
      end_index: null,
    };
    try {
      const res = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data.success) {
        showError(data.error || "Retry failed to start.");
        markRowFailed(idx);
        return;
      }
      connectRetrySSE(data.task_id, idx);
    } catch (e) {
      showError("Network error while retrying.");
      markRowFailed(idx);
    }
  }

  function connectRetrySSE(taskId, idx) {
    const es = new EventSource(`/progress/${taskId}`);
    es.onmessage = (evt) => {
      let data;
      try {
        data = JSON.parse(evt.data);
      } catch (e) {
        return;
      }
      if (data.type === "progress") {
        updatePlaylistRowProgress(data);
      } else if (data.type === "postprocessing") {
        updatePlaylistRowProcessing(data);
      } else if (data.type === "video_complete") {
        markRowCompleted(data.playlist_index);
        overallStatus.textContent = statusLine();
      } else if (data.type === "done") {
        const failed = data.failed_indices || [];
        if (failed.includes(idx)) markRowFailed(idx);
        overallStatus.textContent = statusLine();
        es.close();
      } else if (data.type === "error" || data.type === "cancelled") {
        markRowFailed(idx);
        es.close();
      }
    };
    es.onerror = () => es.close();
  }
})();
