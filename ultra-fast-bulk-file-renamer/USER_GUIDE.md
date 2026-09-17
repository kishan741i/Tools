# 📖 Ultra-Fast Bulk File Renamer — User Guide

पूरी guide — installation, modes, safety, और troubleshooting।

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [First Run](#-first-run)
3. [Renaming Modes](#-renaming-modes)
4. [Sorting Options](#-sorting-options)
5. [Recursive Scanning](#-recursive-scanning)
6. [Extension Filter](#-extension-filter)
7. [Preview & Confirmation](#-preview--confirmation)
8. [Undo Log](#-undo-log)
9. [Safety Guidelines](#-safety-guidelines)
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

- `Ultra-Fast-Bulk-File-Renamer.py` को किसी folder में रखें
- कोई external package install नहीं करना

### Step 3: Verify

```bash
python -c "import os, re, datetime; print('All modules OK')"
```

Output: `All modules OK` ✅

---

## 🚀 First Run

### Run

```bash
python Ultra-Fast-Bulk-File-Renamer.py
```

### Step-by-Step Input

**1. Folder path**
```
👉 Enter folder path: D:/Photos
```

**2. Recursive?**
```
👉 Kya subfolders ke andar ki files ko bhi rename karna hai? [y/n]: n
```

**3. Extension filter**
```
👉 Enter file extension to filter (e.g., .jpg, .mp4) OR press Enter for ALL: .jpg
```

**4. Mode choose करें (1-4)**
```
👉 Choose mode (1-4): 1
```

**5. Mode-specific inputs** (नीचे modes देखें)

**6. Preview + Confirm**
```
👉 Kya aap yeh changes apply karna chahte hain? [y/n]: y
```

---

## 🎯 Renaming Modes

### Mode 1 — Prefix + Counter

**कब use करें:**
- Photos को sequence में arrange करना
- Downloads को systematic नाम देना
- Project files को number करना

**Inputs:**

| Prompt | Example | Notes |
|--------|---------|-------|
| Prefix | `vacation` | Base name |
| Sorting | `2` (Oldest first) | 1=Alphabetical, 2=Oldest, 3=Newest |

**Output:**
```
IMG_001.jpg    →  vacation_01.jpg
IMG_002.jpg    →  vacation_02.jpg
DSC_9999.jpg   →  vacation_03.jpg
```

**Padding:** Auto-detect — 42 files हों तो `01, 02, ..., 42`; 500 files हों तो `001, 002, ..., 500`

**Extension:** वैसा ही रहेगा (`.jpg` → `.jpg`)

---

### Mode 2 — Find & Replace

**कब use करें:**
- Camera के prefix हटाना (`IMG_`, `DSC_`)
- Typos fix करना
- Consistent naming

**Inputs:**

| Prompt | Example |
|--------|---------|
| Text to find | `IMG` |
| Text to replace | `Vacation` |

**Output:**
```
IMG_2023_Beach.jpg    →  Vacation_2023_Beach.jpg
IMG_2023_Sunset.jpg   →  Vacation_2023_Sunset.jpg
IMG_2023_Mountain.jpg →  Vacation_2023_Mountain.jpg
```

**Case sensitive:** हाँ — `IMG` और `img` अलग हैं

**Multiple occurrences:** सब replace होते हैं
```
IMG_IMG_001.jpg  →  Vacation_Vacation_001.jpg  (find: IMG, replace: Vacation)
```

**Remove करना हो तो:** Replace field खाली छोड़ें
```
IMG_001.jpg  →  _001.jpg  (find: IMG, replace: (खाली))
```

---

### Mode 3 — Case Conversion

**कब use करें:**
- Files को consistent case में लाना
- Windows/Linux compatibility

**Inputs:**

| Prompt | Options |
|--------|---------|
| Case type | 1=lowercase, 2=UPPERCASE, 3=Title Case |

**Output:**

| Option | Input | Output |
|--------|-------|--------|
| lowercase | `My_Photo.JPG` | `my_photo.jpg` |
| UPPERCASE | `my_photo.jpg` | `MY_PHOTO.JPG` |
| Title Case | `my_photo.jpg` | `My_Photo.jpg` |

**Note:** Title Case हर word का first letter capital करता है (`_` और `-` word separator हैं)।

---

### Mode 4 — Clean Special Characters

**कब use करें:**
- Downloaded files में `(1)`, `[HD]`, emojis
- Cross-platform compatibility
- URL-safe names

**Inputs:** कोई extra input नहीं — सीधे apply

**Output:**
```
my photo (1).jpg        →  myphoto1.jpg
café ☕ résumé.pdf       →  caférésumé.pdf
₹100 - report!.docx     →  100report.docx
IMG_2023 [HD] (1080p).mkv → IMG_2023HD1080pmkv  (⚠️ extension concatenate!)
```

**⚠️ Warning:** यह mode extension को भी modify कर सकता है। जैसे `file.tar.gz` → `filetargz` (dot remove होता है)। Test folder पर try करें।

**क्या हटता है:**
- Spaces
- Emojis (☕, 😀, etc.)
- Symbols (`(`, `)`, `[`, `]`, `!`, `@`, `#`, `$`, `%`, `^`, `&`, `*`)
- Dots (middle में)

**क्या रहता है:**
- Letters (a-z, A-Z, Unicode)
- Numbers (0-9)
- Underscore `_`
- Hyphen `-`

**Better version (extension safe):**

Script modify करें:

```python
# Line ~130 के आसपास, mode 4 में
cleaned_name = re.sub(r'[^\w\-]', '', name_part)
new_name = cleaned_name + ext.lower()  # यहाँ ext safe है
```

यह already extension safe है — `name_part` और `ext` अलग हैं।

---

## 🔀 Sorting Options (Mode 1 only)

### 1 — Alphabetical (A→Z)

```
apple.jpg
banana.jpg
cherry.jpg
```
Default sorting। Case-insensitive।

### 2 — Oldest First

```
2019_photo.jpg    (oldest)
2020_photo.jpg
2023_photo.jpg    (newest)
```
File system के **modified time** (mtime) के हिसाब से।

**Use case:** Chronological order बनाना — जैसे vacation photos।

### 3 — Newest First

```
2023_photo.jpg    (newest)
2020_photo.jpg
2019_photo.jpg    (oldest)
```
Reverse chronological।

---

## 📁 Recursive Scanning

### Non-Recursive (Default — `n`)

सिर्फ़ **root folder** की files:

```
D:/Photos/
├── IMG_001.jpg     ✅ rename होगी
├── IMG_002.jpg     ✅ rename होगी
└── 2019/
    └── IMG_003.jpg  ❌ skip
```

### Recursive (`y`)

**सभी subfolders** की files:

```
D:/Photos/
├── IMG_001.jpg          ✅ rename
├── IMG_002.jpg          ✅ rename
└── 2019/
    └── IMG_003.jpg      ✅ rename (2019/ में)
└── 2020/
    └── IMG_004.jpg      ✅ rename (2020/ में)
```

**Note:** Mode 1 (Counter) recursive में **हर folder में अलग counter** चलता है — 2019 में `vacation_01, vacation_02`, 2020 में भी `vacation_01, vacation_02`।

अगर global counter चाहिए तो script modify करें:

```python
# Line ~85 के आसपास
count = 1
for old_path in all_files:
    # ... existing code
    count += 1
```

यह already global है — `count` loop के बाहर है।

---

## 🔍 Extension Filter

### Supported Formats

| Type | Extension | Example |
|------|-----------|---------|
| Photos | `.jpg`, `.jpeg`, `.png`, `.gif`, `.heic` | `.jpg` |
| Videos | `.mp4`, `.mkv`, `.avi`, `.mov` | `.mp4` |
| Audio | `.mp3`, `.wav`, `.flac`, `.m4a` | `.mp3` |
| Documents | `.pdf`, `.docx`, `.txt`, `.xlsx` | `.pdf` |
| Archives | `.zip`, `.rar`, `.7z` | `.zip` |

### Case Insensitive

`.JPG`, `.jpg`, `.Jpg` — सब same हैं।

### Multiple Extensions

Script **एक time पर एक extension** support करती है। Multiple चाहिए तो script modify करें:

```python
# Line ~30 के आसपास
ext_input = input("...").strip().lower()
target_exts = [e.strip() for e in ext_input.split(',')] if ext_input else None

# Line ~50 और ~57 में
if target_exts and not any(f.lower().endswith(e) for e in target_exts):
    continue
```

फिर input: `.jpg,.png,.gif`

---

## 📋 Preview & Confirmation

### Preview

Rename से पहले:
```
--- 📋 Preview (42 files will be renamed) ---
  IMG_20190101_120000.jpg           ➡️  vacation_01.jpg
  IMG_20190115_083000.jpg           ➡️  vacation_02.jpg
  IMG_20190120_154500.jpg           ➡️  vacation_03.jpg
  IMG_20190205_101500.jpg           ➡️  vacation_04.jpg
  IMG_20190210_173000.jpg           ➡️  vacation_05.jpg
  IMG_20190301_091500.jpg           ➡️  vacation_06.jpg
  IMG_20190315_142000.jpg           ➡️  vacation_07.jpg
  IMG_20190401_183000.jpg           ➡️  vacation_08.jpg
  IMG_20190420_073000.jpg           ➡️  vacation_09.jpg
  IMG_20190501_120000.jpg           ➡️  vacation_10.jpg
  ... aur baaki ki 32 files.
```

**क्यों सिर्फ़ 10?** — Screen clutter से बचने के लिए।

### Confirmation

```
👉 Kya aap yeh changes apply karna chahte hain? [y/n]:
```

- `y` → Apply
- `n` → Cancel (safe exit)
- कोई और key → Cancel (safe)

### Live Progress

```
[⚡] Renaming files...
🚀 [⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀]  50% | 21/42 | ETA: 1s | [IMG_2019...]
```

| Part | Meaning |
|------|---------|
| Braille bar | Progress |
| 50% | Percentage |
| 21/42 | Renamed / Total |
| ETA: 1s | Time remaining |
| `[IMG_2019...]` | Current file (truncated) |

---

## ↩️ Undo Log

### Location

Rename के बाद log file बनती है:

```
D:/Photos/rename_undo_log_20250917_143022.txt
```

Path script के अंत में print होता है:
```
📄 Undo Log saved at: D:/Photos/rename_undo_log_20250917_143022.txt
```

### Format

```
OLD_PATH | NEW_PATH
D:/Photos/IMG_001.jpg -> D:/Photos/vacation_01.jpg
D:/Photos/IMG_002.jpg -> D:/Photos/vacation_02.jpg
D:/Photos/IMG_003.jpg -> D:/Photos/vacation_03.jpg
```

### Manual Undo

**Python script:**

```python
import os

log_file = "D:/Photos/rename_undo_log_20250917_143022.txt"

with open(log_file, 'r', encoding='utf-8') as f:
    next(f)  # skip header
    renames = []
    for line in f:
        if " -> " in line:
            old, new = line.strip().split(" -> ")
            renames.append((new, old))  # reverse order

# Reverse में rename करें (नई → पुरानी)
for new, old in reversed(renames):
    if os.path.exists(new):
        try:
            os.rename(new, old)
            print(f"↩️  {new} → {old}")
        except Exception as e:
            print(f"❌ {new}: {e}")
```

**बस यह script log file के साथ run करें — सब वापस rename हो जाएंगी।**

### Windows Batch (Manual)

```bat
@echo off
for /f "tokens=1,2 delims=>" %%a in (rename_undo_log_*.txt) do (
    ren "%%a" "%%b"
)
```

**⚠️** Batch approach में careful रहें — path में spaces हो सकती हैं।

---

## 🛡 Safety Guidelines

### 🟢 Safe Practices

1. **Test folder पर try करें** — पहली बार छोटे folder पर
2. **Preview देखें** — confirm से पहले पूरी list review करें
3. **Undo log रखें** — delete न करें जब तक satisfied न हों
4. **Backup रखें** — important folders का
5. **Extension filter** use करें — specific files ही rename करें

### 🔴 Risks

1. **Permanent** — undo log manually चलाना पड़ेगा
2. **Wrong folder** — गलत path पर सब rename हो जाएंगी
3. **Collisions** — same name existing file → skip (crash नहीं)
4. **Extension damage** — Mode 4 में `.tar.gz` जैसे extensions damage हो सकते हैं

### ⚠️ जब न करें

- **System folders** — `C:\Windows`, `/System`
- **Program folders** — `C:\Program Files`
- **Git repos** — version control files
- **Active projects** — बिना backup के
- **Download folder** — अगर browser downloads pending हों

### ✅ जब करें

- **Photo libraries** — chronological naming
- **Downloads** — cleanup
- **Music collections** — consistent format
- **Backup folders** — before archiving
- **Old projects** — reorganization

---

## 🐛 Troubleshooting

### ❌ Yeh folder exist nahi karta

**कारण:** Path गलत है या folder नहीं है।

**Solution:**
- Path check करें
- Forward/backward slash try करें
- Network drive mapped है क्या?

### ❌ Koi bhi file match nahi hui

**कारण:** Extension filter से कोई file match नहीं हुई, या folder खाली है।

**Solution:**
- Extension filter हटाएं (Enter दबाएं)
- Folder contents check करें

### ❌ Permission denied

**कारण:** Files read-only हैं या system files हैं।

**Solution:**
- **Windows:** Administrator से run करें
- **Linux/Mac:** `sudo` से run करें
- Read-only attribute हटाएं

### ❌ कुछ files skip हो गईं

**कारण:** Same नाम की file पहले से exist करती है (collision)।

**Solution:** Script collision पर **skip** करती है (crash नहीं)। Files सुरक्षित हैं। पहले conflicting files हटाएं/rename करें।

### ❌ Rename fail हो रहा है

**कारण:** File किसी app में open है।

**Solution:**
- सारी apps बंद करें (Photos, VLC, etc.)
- Windows: File Explorer बंद करें
- Retry करें

### ❌ Mode 4 ने extension damage कर दिया

**कारण:** `file.tar.gz` → `filetargz` (middle dot remove हो गया)।

**Solution:** Undo log से restore करें। या Mode 4 को safer बनाएं:

```python
# Line ~130
name_part, ext = os.path.splitext(filename)  # ext safe है
cleaned_name = re.sub(r'[^\w\-]', '', name_part)  # सिर्फ़ name_part clean
new_name = cleaned_name + ext.lower()  # ext preserve
```

यह already safe है — extension separate रखा जाता है।

### ❌ Script crash हो गई

**Solution:**
- Python 3.8+ check करें
- Terminal में error message देखें
- Path में special characters हैं क्या?
- बहुत गहरे folders (Windows path limit 260 chars)?

---

## 🚀 Advanced Usage

### 1. Multiple Extensions

Input में comma-separated:

```python
# Script modify करें
ext_input = input("...").strip().lower()
target_exts = [e.strip() if e.strip().startswith('.') else '.'+e.strip() 
               for e in ext_input.split(',')] if ext_input else None

# File gathering में
if target_exts and not any(f.lower().endswith(e) for e in target_exts):
    continue
```

Input: `.jpg,.jpeg,.png`

### 2. Date-based Renaming

Script modify करें (Mode 1 में):

```python
# Line ~85
for old_path in all_files:
    # ...
    mtime = os.path.getmtime(old_path)
    date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y%m%d")
    new_name = f"{date_str}_{prefix}_{padded_counter}{ext}"
```

Output: `20250917_vacation_01.jpg`

### 3. Custom Regex (Mode 4)

सिर्फ़ alphanumeric, underscore, hyphen रखें:

```python
# Line ~130
cleaned_name = re.sub(r'[^a-zA-Z0-9_\-]', '', name_part)
```

या lowercase only:

```python
cleaned_name = re.sub(r'[^a-z0-9_\-]', '', name_part.lower())
```

### 4. Dry-Run Mode

Sirf preview देखें, apply न करें:

```python
# Line ~155 (confirm के बाद) में add करें:
if confirm == 'y':
    # existing code
else:
    # यहीं exit
    sys.exit(0)
```

या script में `DRY_RUN = True` flag:

```python
DRY_RUN = True   # Line 1 पर

# Line ~175
if confirm == 'y' and not DRY_RUN:
    # rename code
elif DRY_RUN:
    print("[Dry-run] No files renamed.")
```

### 5. Skip Hidden Files

```python
# File gathering में
if f.startswith('.'):  # Linux/Mac
    continue
if f.startswith('~$'):  # Office temp files
    continue
```

### 6. CSV Report

```python
import csv

with open("rename_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Old Name", "New Name", "Status"])
    for old_p, new_p, old_n, new_n in renames:
        status = "Success" if os.path.exists(new_p) else "Failed"
        writer.writerow([old_n, new_n, status])
```

### 7. Subfolder-wise Counter

हर folder में counter reset करें:

```python
# Line ~85
from collections import defaultdict
counters = defaultdict(int)

for old_path in all_files:
    directory = os.path.dirname(old_path)
    counters[directory] += 1
    count = counters[directory]
    # ... baaki code
```

### 8. Scheduled Renaming (Windows)

`.bat` file बनाएं:

```bat
@echo off
python "C:\path\to\Ultra-Fast-Bulk-File-Renamer.py" < inputs.txt
```

Task Scheduler से daily run करें।

---

## ❓ FAQ

### Q1: क्या यह files delete करता है?

नहीं, सिर्फ़ **rename** करता है। Delete नहीं होती।

### Q2: Undo possible है?

हाँ — undo log file manually run करके। Automatic undo नहीं है (लेकिन script छोटा है — ऊपर दिया है)।

### Q3: कितनी files rename कर सकता है?

कोई limit नहीं — लाखों files भी।

### Q4: क्या hidden files rename होंगी?

हाँ — `os.walk` और `os.listdir` hidden भी include करते हैं।

### Q5: क्या same name collision पर crash होगा?

नहीं — script **skip** करती है और continue करती है।

### Q6: Subfolders भी rename होंगे?

सिर्फ़ **files** — folders rename नहीं होते।

### Q7: क्या network drive पर चलेगा?

हाँ — लेकिन धीमा होगा। Path format `//server/share/folder` use करें।

### Q8: Original file names कैसे recover करें?

Undo log से — `rename_undo_log_*.txt` file खोलें।

### Q9: क्या script parallel है?

नहीं — single-threaded है। लेकिन rename fast operation है।

### Q10: Mac/Linux पर चलेगी?

हाँ — cross-platform है।

### Q11: Case-sensitive filesystem?

Linux/Mac पर case-sensitive हो सकता है — `File.jpg` और `file.jpg` अलग हैं।

### Q12: Long path issue (Windows)?

Windows 260 char limit — बहुत गहरे folders में fail हो सकता है। Enable long paths या shorter names use करें।

### Q13: Empty folders rename होंगे?

नहीं, सिर्फ़ files।

### Q14: Symlinks?

`os.walk` symlinks को follow करता है (Linux/Mac)। Windows पर junction points अलग हैं।

### Q15: Multiple folders एक साथ?

नहीं — एक folder per run। Multiple के लिए multiple बार चलाएं।

### Q16: क्या script modify कर सकते हैं?

हाँ — MIT license है।

---

## 📊 Comparison

| Tool | Speed | Modes | GUI | Undo |
|------|-------|-------|-----|------|
| **Ultra-Fast Bulk File Renamer** | ⚡⚡⚡ | 4 | ❌ | ✅ Log |
| Bulk Rename Utility (Win) | ⚡⚡ | 20+ | ✅ | ✅ |
| Advanced Renamer (Win) | ⚡⚡ | 15+ | ✅ | ✅ |
| Thunar Bulk Rename (Linux) | ⚡⚡ | 8 | ✅ | ❌ |
| Python `os.rename` script | ⚡⚡⚡ | Custom | ❌ | Manual |

---

## 📞 Support

- 🐛 Bug report → GitHub Issues
- 💡 Feature request → GitHub Issues

---

## 📜 License

MIT License — free to use, modify, distribute.

---

**Happy renaming! 🚀**