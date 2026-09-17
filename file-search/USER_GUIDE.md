# 📖 File Search — User Guide

पूरी guide — setup, usage, options, और troubleshooting।

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [First Run](#-first-run)
3. [UI Explained](#-ui-explained)
4. [Search Options](#-search-options)
5. [Type Filters](#-type-filters)
6. [Tips & Tricks](#-tips--tricks)
7. [Troubleshooting](#-troubleshooting)
8. [Advanced Usage](#-advanced-usage)
9. [FAQ](#-faq)

---

## 🛠 Installation

### Step 1: Python Install

- Python 3.8+ डाउनलोड करें: https://python.org
- Install करते समय **"Add Python to PATH"** ✅ करें

### Step 2: Tkinter Check

Tkinter Python के साथ आता है। Verify करें:

```bash
python -c "import tkinter; print('Tkinter OK')"
```

अगर `Tkinter OK` आए तो तैयार।

**Linux users** — अगर error आए:
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

**macOS users** — Homebrew Python:
```bash
brew install python-tk
```

### Step 3: Run

```bash
python file_search.py
```

---

## 🚀 First Run

स्क्रिप्ट चलाने पर एक window खुलेगी:

```
┌──────────────────────────────────────────────────────────┐
│  Search My Machine                                       │
├──────────────────────────────────────────────────────────┤
│  Location: [This PC ▼]  Type: [All Types ▼]             │
│  Search for: [_______________]  [Search] [Stop]         │
│  ☑ Files  ☑ Folders  ☐ Case sensitive  ☐ Exact name     │
├──────────────────────────────────────────────────────────┤
│  Type a name and press Search.                           │
│  [                                        ]              │
├──────────────────────────────────────────────────────────┤
│  Full path                    │ Type   │ Size            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

1. **Search for** field में कोई नाम type करें (e.g., `report`)
2. **Search** दबाएं या **Enter**
3. Background में scan होगा — status और progress दिखेंगे
4. Results नीचे list में आएंगे
5. किसी result पर **double-click** करें → folder खुल जाएगा

---

## 🖥 UI Explained

### Top Row

| Element | क्या करता है |
|---------|-------------|
| **Location** dropdown | `This PC` (सभी drives) या specific drive चुनें |
| **Type** dropdown | File type filter (Documents, Images, ...) |
| **Search for** entry | File/folder का नाम type करें |
| **Search** button | Search शुरू करें |
| **Stop** button | चालू search रोकें |

### Options Row

| Checkbox | Default | क्या करता है |
|----------|---------|-------------|
| **Files** | ✅ ON | Files match करें |
| **Folders** | ✅ ON | Folders match करें |
| **Case sensitive** | ⬜ OFF | `Report` vs `report` अलग मानें |
| **Exact name** | ⬜ OFF | पूरा नाम match हो, contains नहीं |

### Status + Progress

- **Status line** — अभी कौन सा folder scan हो रहा है
- **Progress bar** — animated, search चालू है का indication

### Results List

| Column | Description |
|--------|-------------|
| **Full path** | पूरा path |
| **Type** | File या Folder |
| **Size** | File size (KB/MB/GB), folder के लिए खाली |

**Double-click** → file/folder का parent folder Explorer में खुलेगा।

---

## 🎯 Search Options

### 1. Location (कहाँ ढूंढें)

**This PC** — सभी drives scan होंगे (धीमा, पूरा)
**C:\** — सिर्फ़ C drive (तेज़)
**D:\** — सिर्फ़ D drive
**E:\** — USB/external drive

**Tip:** पता है कहाँ है तो specific drive चुनें — 3-5x तेज़।

### 2. Type (क्या ढूंढें)

`All Types` — सब कुछ
`Documents` — PDF, DOC, XLS, PPT, TXT
`Images` — JPG, PNG, GIF, ...
`Videos` — MP4, MKV, AVI, ...
`Audio` — MP3, WAV, FLAC, ...
`Archives` — ZIP, RAR, 7Z, ...
`Programs` — EXE, MSI, BAT, ...
`Code` — PY, JS, HTML, ...
`Folders only` — सिर्फ़ folders

### 3. Files + Folders

दोनों ON — files और folders दोनों match होंगे
सिर्फ़ Files — folders ignore
सिर्फ़ Folders — files ignore

### 4. Case Sensitive

OFF (default) — `Report` = `report` = `REPORT`
ON — `Report` ≠ `report`

### 5. Exact Name

OFF (default) — `report` match करेगा `my_report.pdf` को भी
ON — `report` सिर्फ़ ठीक `report` file को match करेगा

---

## 📂 Type Filters

### Documents
`.pdf .doc .docx .txt .rtf .odt .xls .xlsx .ppt .pptx .csv .md`

### Images
`.jpg .jpeg .png .gif .bmp .tiff .webp .svg .ico .heic`

### Videos
`.mp4 .mkv .avi .mov .wmv .flv .webm .m4v .mpg .mpeg .3gp`

### Audio
`.mp3 .wav .flac .aac .ogg .m4a .wma .opus .aiff`

### Archives
`.zip .rar .7z .tar .gz .bz2 .xz .iso .cab`

### Programs
`.exe .msi .bat .cmd .sh .app .apk .deb .rpm`

### Code
`.py .js .ts .java .c .cpp .h .cs .php .html .css .json .xml .sql .rb .go .rs`

### Folders only
कोई extension नहीं — सिर्फ़ folder names।

---

## 💡 Tips & Tricks

### 1. तेज़ search

- **Single drive** चुनें, This PC नहीं
- **Type filter** लगाएं (Documents/Images/etc.)
- **Case sensitive** ON करें
- **Folders** uncheck करें अगर सिर्फ़ files चाहिए

### 2. Specific file type ढूंढना

Type filter में नहीं है? **All Types** रखें और name में extension type करें:
```
.mp4          → सभी mp4 files
report.pdf    → report.pdf files
*.log         → exact match OFF रखें, ".log" type करें
```

### 3. Multiple words

Search contains-based है:
```
my report     → "my report" वाला हर नाम match होगा
```

### 4. Empty search

खाली query से search नहीं होगी — कम से कम 1 character type करें।

### 5. Result खोलना

- **Double-click** → folder खुलेगा और file selected होगा
- Windows पर Explorer `/select,` use होता है

### 6. Search रोकना

**Stop** button दबाएं — 1-2 second में रुक जाएगी। जो results मिल चुके हैं वो रहेंगे।

### 7. गलत search

नई query type करें, **Search** दबाएं — पुराने results हट जाएंगे।

---

## 🐛 Troubleshooting

### ❌ Problem: Tkinter import error

```
ModuleNotFoundError: No module named 'tkinter'
```

**Solution (Linux):**
```bash
sudo apt install python3-tk
# या
sudo dnf install python3-tkinter
```

**macOS (Homebrew Python):**
```bash
brew install python-tk
```

**Windows:** Python को official installer से re-install करें, "tcl/tk" ✅ रखें।

### ❌ Problem: Search बहुत धीमा

**Solution:**
- `This PC` की जगह single drive चुनें
- Type filter लगाएं (All Types नहीं)
- Exact name use करें
- पता है folder कहाँ है? — पूरा drive scan किए बिना manual देखें

### ❌ Problem: कुछ folders scan नहीं हो रहे

**कारण:** Permission denied — system folders (जैसे `C:\Windows\System32` के कुछ हिस्से)

**Solution:**
- Script को **Administrator** से run करें
- या जान-बूझकर skip करें — यह normal है

### ❌ Problem: UI freeze हो गया

**Solution:**
- **Stop** दबाएं
- 2-3 second रुकें
- फिर नई search करें

### ❌ Problem: Stop button काम नहीं कर रहा

**कारण:** Background thread एक बड़े folder के बीच में है

**Solution:** 1-2 second wait करें — automatic रुक जाएगा। हर folder iteration पर stop check होता है।

### ❌ Problem: Results में कुछ अजीब paths

**Solution:** System files हैं (`$Recycle.Bin`, `System Volume Information` skip होते हैं, लेकिन और भी हो सकते हैं)। इन्हें ignore करें।

### ❌ Problem: USB drive dropdown में नहीं दिख रहा

**Solution:** Dropdown पर click करने से पहले USB plug-in करें। Dropdown खुलने पर list refresh होती है।

---

## 🚀 Advanced Usage

### 1. Startup पर auto-run (Windows)

1. `Win + R` → `shell:startup` → Enter
2. `file_search.bat` बनाएं:

```bat
@echo off
start "" pythonw "C:\path\to\file_search.py"
```

3. उस folder में रखें

### 2. Desktop Shortcut

1. `file_search.py` पर right-click
2. **Send to** → **Desktop (create shortcut)**
3. Shortcut properties में **Target**:
   ```
   pythonw "C:\path\to\file_search.py"
   ```

### 3. Command-line से

Windows:
```bash
python file_search.py
```

Linux/macOS:
```bash
python3 file_search.py
```

### 4. Custom skip list

`SKIP_DIR_NAMES` में अपनी folders जोड़ें:

```python
SKIP_DIR_NAMES = {
    "$Recycle.Bin", "System Volume Information", "Windows.old",
    "proc", "sys", "dev", "run",
    "node_modules",      # ✅ नया
    ".git",              # ✅ नया
    "__pycache__",       # ✅ नया
}
```

### 5. Search results export

Code जोड़ें result list को CSV में save करने के लिए:

```python
import csv

def export_results(self):
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Path", "Type", "Size"])
        for row in self.tree.get_children():
            writer.writerow(self.tree.item(row, "values"))
```

फिर एक Export button जोड़ें।

### 6. Standalone .exe बनाएं

```bash
pip install pyinstaller
pyinstaller --onefile --windowed file_search.py
```

`dist/file_search.exe` मिलेगा — Python install किए बिना चलेगा।

---

## ❓ FAQ

### Q1: क्या यह Windows Search से तेज़ है?

**A:** नहीं, Windows Search indexed है। लेकिन यह **index-free** है — USB drives, network drives, और बिना index वाली जगहों पर भी काम करता है।

### Q2: क्या search results save होते हैं?

**A:** नहीं — window बंद करने पर सब गायब। Export feature manually add कर सकते हैं (ऊपर देखें)।

### Q3: कितनी files scan हो सकती हैं?

**A:** कोई limit नहीं — depends on RAM। लाखों files में भी चलेगा, बस Treeview भारी हो सकती है।

### Q4: Network drive search?

**A:** हाँ, अगर drive mapped है (Z:\ आदि) तो dropdown में आएगा। लेकिन बहुत धीमा होगा।

### Q5: File content search?

**A:** नहीं — सिर्फ़ **filename** और **folder name** match होते हैं। Content search के लिए `grep`, `findstr`, या `ripgrep` use करें।

### Q6: Hidden files दिखेंगे?

**A:** हाँ — script hidden attribute check नहीं करती। लेकिन system folders skip होते हैं।

### Q7: क्या यह macOS पर चलेगा?

**A:** हाँ — Tkinter cross-platform है। `open -R` से Finder में reveal होगा।

### Q8: Linux पर चलेगा?

**A:** हाँ — बस Tkinter install होना चाहिए (`python3-tk`)। `xdg-open` से folder खुलेगा।

### Q9: Search cancel करने पर results रहते हैं?

**A:** हाँ — जो मिल चुके हैं वो list में रहते हैं।

### Q10: Administrator की ज़रूरत है?

**A:** Normal use में नहीं। लेकिन system folders (`C:\Windows`, `C:\Program Files`) पूरी तरह scan करने के लिए Administrator से run करें।

---

## ⚙️ Performance Comparison

| Scenario | Time (approx) |
|----------|---------------|
| Single drive, specific type | 5-30 sec |
| Single drive, all types | 30-90 sec |
| This PC, specific type | 1-3 min |
| This PC, all types | 3-10 min |

**Time depends on:**
- Disk speed (SSD vs HDD)
- Number of files
- Drive size
- Permissions

---

## 📞 Support

- 🐛 Bug report → GitHub Issues
- 💡 Feature request → GitHub Issues

---

## 📜 License

MIT License — free to use, modify, distribute.

---

**Happy searching! 🔍**