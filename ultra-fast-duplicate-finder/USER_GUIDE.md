# 📖 Ultra-Fast Duplicate Finder — User Guide

पूरी guide — installation, usage, safety, और troubleshooting।

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [First Run](#-first-run)
3. [How It Works](#-how-it-works)
4. [Step-by-Step Usage](#-step-by-step-usage)
5. [Extension Filter](#-extension-filter)
6. [Reading the Output](#-reading-the-output)
7. [Auto-Delete](#-auto-delete)
8. [Safety Guidelines](#-safety-guidelines)
9. [Performance Tips](#-performance-tips)
10. [Troubleshooting](#-troubleshooting)
11. [Advanced Usage](#-advanced-usage)
12. [FAQ](#-faq)

---

## 🛠 Installation

### Step 1: Python

- Python 3.8+ डाउनलोड करें: https://python.org
- Install करते समय **"Add Python to PATH"** ✅ करें
- Verify: `python --version`

### Step 2: Script Download

- `Ultra-Fast-Duplicate-Finder.py` को किसी folder में रखें
- कोई external package install नहीं करना

### Step 3: Verify

```bash
python -c "import hashlib, os, collections; print('All modules OK')"
```

Output: `All modules OK` ✅

---

## 🚀 First Run

### Run

```bash
python Ultra-Fast-Duplicate-Finder.py
```

### Output

```
👉 Enter folder or drive path to scan (e.g., D:/ or /sdcard):
```

Path type करें (e.g., `D:/Photos`) → Enter

```
👉 Enter file extension to filter (e.g., .mp3, .png) OR press Enter to scan ALL files:
```

Extension type करें (e.g., `.jpg`) या खाली छोड़ें → Enter

---

## 🔍 How It Works

### 2-Step Filtering

**Step 1 — Size Grouping (Fast)**
```
Files: 10,000
Same size groups: 342 files (rest unique size → skip)
```

**Step 2 — MD5 Hash (Precise)**
```
342 candidates → hashes compare → 28 duplicate groups
```

**क्यों fast है?**
- 90% files unique size के होते हैं — hash नहीं करना पड़ता
- सिर्फ़ candidates का hash होता है
- 64KB chunks में read — memory efficient

### Why MD5?

- Fast (SHA-256 से तेज़)
- Collision practically impossible for file dedup
- Industry standard for duplicate finding

---

## 🎯 Step-by-Step Usage

### STEP 1 — Path Enter करें

**Format:**
- Windows: `D:/`, `C:/Users/Name/Photos`, `D:\Music`
- Linux/Mac: `/home/user/Music`, `/mnt/drive`
- Android (Termux): `/sdcard/DCIM`

**Tips:**
- Trailing slash optional: `D:/` और `D:` दोनों चलेंगे
- Forward slash या backslash दोनों काम करते हैं
- Path में space हो तो quotes की ज़रूरत नहीं (input() handle करता है)

### STEP 2 — Extension Filter (Optional)

**कुछ examples:**

| Input | क्या scan होगा |
|-------|---------------|
| `.jpg` | सिर्फ़ JPG files |
| `.mp3` | सिर्फ़ MP3 files |
| `jpg` | Same — auto `.` add होता है |
| (खाली) | सभी files |
| `.png` | सिर्फ़ PNG |
| `.mp4` | सिर्फ़ MP4 |

**Case insensitive** — `.JPG` और `.jpg` same हैं।

### STEP 3 — Scanning

Script 2 phases में चलती है:

**Phase 1 — Folder scan:**
```
[⚡] Step 1: Scanning folder & grouping by file size...
[+] Total files scanned : 1247
[+] Potential duplicates: 342 files. Scanning hashes...
```

**Phase 2 — Hash scan with progress:**
```
🚀 [⣿⣿⣿⣿⣀⣀⣀⣀] 50% | 171/342 | ETA: 12s | [IMG_20230104.jpg]
```

### STEP 4 — Results

```
[!] Total Duplicate Groups Found: 28

[1] Group Match:
   📁 Original  : D:/Photos/2019/IMG_001.jpg
   🗑️ Duplicate : D:/Photos/2020/IMG_001_copy.jpg
   🗑️ Duplicate : D:/Photos/Backup/IMG_001.jpg
----------------------------------------------------------------------

[2] Group Match:
   📁 Original  : D:/Photos/2019/IMG_002.jpg
   🗑️ Duplicate : D:/Photos/Backup/IMG_002.jpg
----------------------------------------------------------------------

💾 Total Space to be Freed: 2.34 GB
```

### STEP 5 — Delete Confirm

```
👉 Kya aap saare duplicate files ko automatically delete karna chahte hain? [y/n]:
```

- `y` → सारी duplicates delete
- `n` → कुछ नहीं delete, safe exit
- कोई और key → `n` जैसा behavior (safe)

**Delete output:**
```
[✔] Deleted: D:/Photos/2020/IMG_001_copy.jpg
[✔] Deleted: D:/Photos/Backup/IMG_001.jpg
[✔] Deleted: D:/Photos/Backup/IMG_002.jpg
...
🎉 Success! Total 56 duplicate files delete kar di gayi hain aur 2.34 GB space free ho chuki hai.
```

---

## 🎚 Extension Filter

### Common Extensions

| Category | Extensions |
|----------|-----------|
| **Photos** | `.jpg .jpeg .png .gif .bmp .tiff .heic` |
| **Videos** | `.mp4 .mkv .avi .mov .wmv .flv .webm` |
| **Audio** | `.mp3 .wav .flac .aac .m4a .ogg .opus` |
| **Documents** | `.pdf .doc .docx .txt .xls .xlsx .ppt` |
| **Archives** | `.zip .rar .7z .tar .gz` |
| **Code** | `.py .js .html .css .json .xml` |

### Multiple Extensions

Script **एक time पर एक extension** support करती है। Multiple चाहिए तो multiple बार चलाएं।

**या** script modify करें (`target_ext` को list बनाएं):

```python
# Line ~50 के आसपास
target_exts = ['.jpg', '.png', '.gif']
# फिर condition:
if target_exts and not any(file.lower().endswith(e) for e in target_exts):
    continue
```

---

## 📊 Reading the Output

### Progress Bar

```
🚀 [⣿⣿⣿⣿⣀⣀⣀⣀] 50% | 171/342 | ETA: 12s | [IMG_20230104.jpg]
```

| Part | Meaning |
|------|---------|
| `⣿⣿⣿⣿⣀⣀⣀⣀` | Braille progress bar |
| `50%` | Percentage complete |
| `171/342` | Files hashed / total candidates |
| `ETA: 12s` | Estimated time remaining |
| `[IMG_...jpg]` | Current file (truncated) |

### Group Output

```
[1] Group Match:
   📁 Original  : path/to/original.jpg
   🗑️ Duplicate : path/to/duplicate1.jpg
   🗑️ Duplicate : path/to/duplicate2.jpg
```

- **Original** = सबसे पुरानी file (mtime के हिसाब से)
- **Duplicate** = बाकी सब

### Space Counter

```
💾 Total Space to be Freed: 2.34 GB
```

यह **सिर्फ़ duplicates** का total size है (original को छोड़कर)।

### Hash Details

हर group एक unique MD5 hash से identify होता है। Same hash = byte-level same file।

**Note:** अगर दो files का size same है लेकिन content अलग है, तो hash different होगा — वो duplicate नहीं मानी जाएंगी।

---

## 🗑 Auto-Delete

### कैसे काम करता है

1. सारी duplicates पहले **list** में print होती हैं
2. **Space calculation** दिखता है
3. **Confirm prompt** आता है
4. `y` दबाने पर **एक-एक करके** delete होती हैं
5. हर delete का status print होता है
6. Error आए तो skip होकर आगे बढ़ती है

### Delete Order

- **Oldest file पहले** — original safe
- **Duplicates** delete होती हैं
- Group-by-group order

### Error Handling

अगर कोई file delete नहीं हो पाई:
```
[❌] Error deleting D:/Photos/locked.jpg: [WinError 32] The process cannot access the file
```

Script **रुकती नहीं** — बाकी continue करती है।

### Rollback

**कोई rollback नहीं** — deleted files recycle bin में नहीं जातीं, permanent delete हैं।

**Windows पर Recycle Bin में भेजने के लिए** script modify करें:

```python
# os.remove की जगह
import send2trash   # pip install send2trash
send2trash.send2trash(dup_path)
```

---

## 🛡 Safety Guidelines

### 🟢 Safe Practices

1. **पहले test करें** — छोटे folder पर
2. **Backup रखें** — important folders का
3. **List देखें** — delete से पहले पूरी list review करें
4. **`n` दबाएं** — अगर कोई doubt हो
5. **Original verify करें** — oldest file सही है क्या?

### 🔴 Risks

1. **Permanent delete** — Recycle Bin में नहीं जाती
2. **Wrong folder** — गलत path देने पर important files जा सकती हैं
3. **Encrypted files** — Same content but different hash हो सकता है
4. **Symlinks** — Skip होते हैं, लेकिन verify करें

### ⚠️ जब न करें

- **System folders** — `C:/Windows`, `/System`, `/usr`
- **Program folders** — `C:/Program Files`
- **Active project folder** — version control के बिना
- **Photos library** — जब तक proper backup न हो

### ✅ जब करें

- **Downloads folder** — duplicate downloads
- **Photos** — same photo multiple copies
- **Music** — duplicate MP3s
- **Backup drives** — old backups
- **SD cards** — camera duplicates

---

## ⚡ Performance Tips

| Tip | फ़ायदा |
|-----|--------|
| **Extension filter** लगाएं | 5-10x तेज़ |
| **SSD** use करें | 3-5x तेज़ |
| **Specific folder** चुनें | पूरे drive से तेज़ |
| **बंद करें** background apps | Disk I/O free |
| **बड़ी files** के लिए patience | Hash time ज़्यादा |
| **Network drives** avoid करें | बहुत धीमा |

### Hash Speed

| File Size | Time per File |
|-----------|---------------|
| 1 MB | ~5 ms |
| 10 MB | ~50 ms |
| 100 MB | ~500 ms |
| 1 GB | ~5 sec |

### Example Timings

| Scenario | Files | Time |
|----------|-------|------|
| Photos folder (10K JPG) | 10,000 | 30 sec |
| Music folder (5K MP3) | 5,000 | 1 min |
| Full D: drive (SSD) | 100,000 | 15 min |
| Full D: drive (HDD) | 100,000 | 1 hour |

---

## 🐛 Troubleshooting

### ❌ Invalid path entered

**कारण:** Path गलत है या exist नहीं करता।

**Solution:**
- Path check करें
- Forward/backward slash try करें
- Quotes न लगाएं

### ❌ Permission denied

**कारण:** System files/folders scan कर रहे हैं।

**Solution:**
- **Windows:** Administrator से run करें
- **Linux/Mac:** `sudo` से run करें
- या system folders skip करें

### ❌ बहुत धीमा चल रहा है

**Solution:**
- Extension filter लगाएं
- Specific folder चुनें
- Background apps बंद करें
- HDD पर normal है, SSD पर तेज़

### ❌ Duplicate miss हो गई

**कारण:** Files का content अलग है (same size, different bytes)।

**Solution:** यह सही behavior है — MD5 byte-level match करता है।

### ❌ 0-byte files नहीं मिलीं

**कारण:** By design skip हैं।

**Solution:** Script में change करें:
```python
# Line ~55
if f_size > 0:   # इस condition को हटाएं
    size_map[f_size].append(filepath)
```

### ❌ Symlinks नहीं scan हुए

**कारण:** By design skip हैं (infinite loops से बचने के लिए)।

**Solution:** Script में change:
```python
# Line ~50
if not os.path.islink(filepath):   # हटाएं
```

### ❌ Delete fail हो रहा है

**कारण:** File open है किसी app में, या read-only है।

**Solution:**
- सारी apps बंद करें
- Read-only attribute हटाएं
- Administrator से run करें

### ❌ Script crash हो गई

**Solution:**
- Python 3.8+ check करें
- Terminal में error message देखें
- Path में special characters हैं क्या?

---

## 🚀 Advanced Usage

### 1. Multiple Extensions

`target_ext` को list बनाएं:

```python
def find_duplicates_fast(root_dir, target_exts=None):
    # ...
    if target_exts and not any(file.lower().endswith(e) for e in target_exts):
        continue
```

Run:
```python
dup_groups = find_duplicates_fast(target_path, ['.jpg', '.png', '.gif'])
```

### 2. Recycle Bin में भेजें (Windows)

```bash
pip install send2trash
```

Script में:
```python
import send2trash

# os.remove की जगह
send2trash.send2trash(dup_path)
```

### 3. Minimum Size Filter

छोटी files skip करें:

```python
MIN_SIZE = 1024 * 1024   # 1 MB

if f_size > MIN_SIZE:   # 0 की जगह
    size_map[f_size].append(filepath)
```

### 4. Dry-Run Mode

सिर्फ़ list देखें, delete न करें:

```python
choice = input("...").strip().lower()
if choice == 'y':
    # delete code
else:
    # यहीं exit कर दें
    sys.exit(0)
```

### 5. CSV Export

Results को CSV में save करें:

```python
import csv

with open("duplicates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Group", "Type", "Path", "Size"])
    for idx, (h, paths) in enumerate(dup_groups.items(), 1):
        for i, p in enumerate(paths):
            kind = "Original" if i == 0 else "Duplicate"
            size = os.path.getsize(p)
            writer.writerow([idx, kind, p, size])
```

### 6. Skip Folders

System folders skip करें:

```python
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '$RECYCLE.BIN', 'System Volume Information'}

for root, dirs, files in os.walk(root_dir):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    # ...
```

### 7. Hash Algorithm Change

SHA-256 use करें:

```python
hasher = hashlib.sha256()   # md5() की जगह
```

### 8. Android (Termux)

```bash
pkg install python
python Ultra-Fast-Duplicate-Finder.py
# Path: /sdcard/DCIM
```

**Note:** Android पर `/sdcard` access के लिए Termux को storage permission दें:
```bash
termux-setup-storage
```

---

## ❓ FAQ

### Q1: क्या यह files delete करता है?

नहीं, **आपकी permission के बिना नहीं**। पहले पूरी list दिखाता है, फिर `y` दबाने पर delete।

### Q2: कितनी files scan कर सकता है?

कोई limit नहीं — लाखों files भी handle करेगा। Time drive speed पर depend करता है।

### Q3: क्या Recycle Bin में जाती हैं?

नहीं — `os.remove()` permanent delete है। Recycle Bin के लिए `send2trash` use करें (ऊपर देखें)।

### Q4: क्या hidden files scan होती हैं?

हाँ — `os.walk()` hidden भी include करता है।

### Q5: क्या empty folders scan होते हैं?

नहीं — सिर्फ़ files। Empty folders के लिए अलग tool चाहिए।

### Q6: क्या network drives scan हो सकते हैं?

हाँ, लेकिन **बहुत धीमा** होगा। Local drive recommended है।

### Q7: Hash collision का risk?

Practically zero — MD5 के 2^128 combinations हैं। Duplicate finding के लिए 100% safe।

### Q8: क्या same size, different content detect होगा?

नहीं — hash different होगा, duplicate नहीं मानी जाएगी। ✅ सही behavior।

### Q9: क्या script parallel है?

नहीं — single-threaded है। लेकिन 2-step filtering से fast है।

### Q10: क्या Mac/Linux पर चलेगी?

हाँ — cross-platform है। Path format अलग होगा।

### Q11: Original file कैसे decide होती है?

सबसे पुरानी file (mtime के हिसाब से) — oldest = original।

### Q12: क्या multiple drives एक साथ scan हो सकते हैं?

नहीं — एक बार में एक path। Multiple के लिए multiple बार चलाएं।

### Q13: Crash हो गया, कुछ delete हुआ?

अगर delete phase में crash हुआ — जो delete हो चुकी वो गई। अगर scan phase में — कुछ नहीं हुआ।

### Q14: क्या script modify कर सकते हैं?

हाँ — MIT license है। कोई restriction नहीं।

### Q15: Encrypted files के साथ क्या होगा?

Hash content-based है — same content = same hash. Encryption अलग हो तो hash अलग।

---

## 📊 Comparison

| Tool | Speed | Precise | GUI | Price |
|------|-------|---------|-----|-------|
| **Ultra-Fast Duplicate Finder** | ⚡⚡⚡ | ✅ | ❌ | Free |
| dupeGuru | ⚡⚡ | ✅ | ✅ | Free |
| CCleaner | ⚡ | ⚠️ | ✅ | Freemium |
| Windows Search | ⚡ | ❌ | ✅ | Free |

---

## 📞 Support

- 🐛 Bug report → GitHub Issues
- 💡 Feature request → GitHub Issues

---

## 📜 License

MIT License — free to use, modify, distribute.

---

**Happy cleaning! 🧹**