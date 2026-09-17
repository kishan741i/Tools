# 🚀 Ultra-Fast Bulk File Renamer

पूरे folder (या subfolders) की files को एक साथ rename करने वाला CLI tool — 4 powerful modes, live progress, और undo log के साथ।

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

---

## ✨ Features

- 🎯 **4 Renaming Modes** — Prefix+Counter, Find&Replace, Case, Clean
- 📁 **Recursive scanning** — subfolders भी scan करें (optional)
- 🔍 **Extension filter** — सिर्फ़ `.jpg`, `.mp4`, आदि
- 📊 **Live progress bar** — Braille + ETA + speed
- 📋 **Preview before apply** — पहले 10 renames दिखेंगे
- ↩️ **Undo log** — हर rename का record, वापस कर सकते हैं
- 🛡 **Safe** — confirm के बिना कुछ नहीं होता
- 🚫 **Collision-aware** — existing files overwrite नहीं होतीं
- 💻 **Zero dependencies** — कोई pip install नहीं
- 🌍 **Cross-platform** — Windows, Linux, macOS

---

## 🚀 Quick Start

### 1. Install

कुछ install करने की ज़रूरत **नहीं** — Python 3.8+ सीधे चलाएं।

### 2. Run

```bash
python Ultra-Fast-Bulk-File-Renamer.py
```

### 3. Example

```
=== 🚀 Ultimate Master Python Bulk File Renamer ===
👉 Enter folder path: D:/Photos
👉 Kya subfolders ke andar ki files ko bhi rename karna hai? [y/n]: n
👉 Enter file extension to filter (e.g., .jpg, .mp4) OR press Enter for ALL: .jpg

Select Completely Renaming Mode:
  [1] Prefix + Counter (e.g., photo_01.jpg, photo_02.jpg)
  [2] Find & Replace Text (e.g., replace 'IMG' with 'Vacation')
-----------------------------------------------------------------------------
Select Existing Name Modification Mode:
  [3] Case Conversion (Lower / Upper / Title Case)
  [4] Clean Special Characters & Spaces

👉 Choose mode (1-4): 1
👉 Enter new base name/prefix (e.g., 'photo'): vacation

Select Sorting Order:
  [1] Alphabetical (A to Z)
  [2] Oldest First (Purani files pehle)
  [3] Newest First (Nayi files pehle)
👉 Choose sorting method (1, 2, or 3): 2

--- 📋 Preview (42 files will be renamed) ---
  IMG_20190101_120000.jpg           ➡️  vacation_01.jpg
  IMG_20190115_083000.jpg           ➡️  vacation_02.jpg
  ...
  ... aur baaki ki 32 files.

👉 Kya aap yeh changes apply karna chahte hain? [y/n]: y

[⚡] Renaming files...
🚀 [⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀]  50% | 21/42 | ETA: 1s | [IMG_2019...]

🎉 Success! Total 42 files successfully rename ho chuki hain.
📄 Undo Log saved at: D:/Photos/rename_undo_log_20250917_143022.txt
```

---

## 🎯 4 Renaming Modes

### Mode 1 — Prefix + Counter

```
IMG_001.jpg       →  vacation_01.jpg
IMG_002.jpg       →  vacation_02.jpg
DSC_9999.jpg      →  vacation_03.jpg
```

**Sorting options:**
- Alphabetical (A→Z)
- Oldest first (by modified time)
- Newest first

### Mode 2 — Find & Replace

```
IMG_2023_Beach.jpg    →  Vacation_2023_Beach.jpg
IMG_2023_Sunset.jpg   →  Vacation_2023_Sunset.jpg
```
(find: `IMG` → replace: `Vacation`)

### Mode 3 — Case Conversion

```
my_photo.jpg      →  MY_PHOTO.JPG    (UPPERCASE)
MY_PHOTO.JPG      →  my_photo.jpg    (lowercase)
my_photo.jpg      →  My_Photo.jpg    (Title Case)
```

### Mode 4 — Clean Special Characters

```
my photo (1).jpg       →  myphoto1.jpg
café ☕ résumé.pdf      →  caférésumé.pdf
₹100 - report!.docx    →  100report.docx
```

**क्या हटता है:** Spaces, emojis, symbols, brackets
**क्या रहता है:** Letters, numbers, `_`, `-`, Unicode letters

---

## 📁 Recursive Scanning

**Subfolders भी scan करें:**

```
D:/Photos/
├── 2019/
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── 2020/
│   ├── IMG_003.jpg
│   └── IMG_004.jpg
```

`y` चुनने पर — चारों files rename होंगी (अपने-अपने folder में)।
`n` चुनने पर — सिर्फ़ root folder की files।

---

## 🔍 Extension Filter

| Input | क्या scan होगा |
|-------|---------------|
| `.jpg` | सिर्फ़ JPG |
| `jpg` | Same — auto `.` add |
| `.mp4` | सिर्फ़ MP4 |
| (खाली) | सभी files |

---

## ↩️ Undo Log

हर rename का record `rename_undo_log_YYYYMMDD_HHMMSS.txt` में save होता है:

```
OLD_PATH | NEW_PATH
D:/Photos/IMG_001.jpg -> D:/Photos/vacation_01.jpg
D:/Photos/IMG_002.jpg -> D:/Photos/vacation_02.jpg
```

### Manual Undo

Log file खोलें और reverse rename करें:

```python
# Example undo script
with open("rename_undo_log_20250917_143022.txt") as f:
    next(f)  # skip header
    for line in f:
        old, new = line.strip().split(" -> ")
        os.rename(new, old)
```

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| **Invalid path** | Path सही है क्या? Folder exist करता है? |
| **Permission denied** | Administrator/sudo से run करें |
| **0 files matched** | Extension filter check करें |
| **Files skip हो गईं** | Same name पहले से exist है (collision) |
| **Rename fail** | File किसी app में open है |

---

## ⚠️ Safety Notes

- 🟢 **Preview पहले** — rename से पहले list दिखती है
- 🟢 **Confirm ज़रूरी** — `y` दबाने तक कुछ नहीं होता
- 🟢 **Undo log** — हर rename का record
- 🟢 **No overwrite** — existing file overwrite नहीं होती
- 🔴 **Backup रखें** — important folders का
- 🔴 **Test folder पर try करें** — पहली बार छोटे folder पर
- 🔴 **Permanent** — undo log manually चलाना पड़ेगा

---

## 📋 Requirements

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| OS | Windows, Linux, macOS |
| Dependencies | कोई नहीं |

---

## 🔒 Privacy

- ✅ 100% offline — कोई network नहीं
- ✅ कोई data upload नहीं
- ✅ सब कुछ local machine पर

---

## ⚡ Performance

| Files | Time (SSD) | Time (HDD) |
|-------|------------|------------|
| 100 | ~1 sec | ~2 sec |
| 1,000 | ~5 sec | ~15 sec |
| 10,000 | ~45 sec | ~2 min |
| 100,000 | ~7 min | ~20 min |

**Time depends on:**
- Disk speed
- Recursive scanning (गहरे folders = ज़्यादा time)
- File system (NTFS, ext4, APFS)

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Contributing

Bug report या feature request के लिए issue खोलें।

---

**Happy renaming! 🚀**