# 🔍 File Search

पूरे computer में किसी भी file या folder को name से search करने वाला simple desktop tool।

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()
[![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)]()

---

## ✨ Features

- 🖥 **This PC या single drive** — कहीं भी search करें
- 📁 **Files + Folders** — दोनों match करें
- 🎯 **Type filter** — Documents, Images, Videos, Audio, Archives, Code, Programs
- 🔤 **Case sensitive** search option
- ✅ **Exact name** match option
- ⚡ **Background threading** — UI कभी freeze नहीं होता
- ⏹ **Stop button** — search बीच में रोक सकें
- 📂 **Double-click** — result का folder खुल जाए
- 📊 **File size** — KB/MB/GB में दिखे
- 🚫 **Smart skip** — `$Recycle.Bin`, `System Volume Information`, etc.
- 🎨 **Clean UI** — Tkinter, कोई extra install नहीं

---

## 🚀 Quick Start

### 1. Install

कुछ install करने की ज़रूरत **नहीं** — Tkinter Python के साथ आता है।

**Linux users only:**
```bash
sudo apt install python3-tk
```

### 2. Run

```bash
python file_search.py
```

---

## 📸 कैसे काम करता है?

```
┌──────────────────────────────────────────────────────────┐
│  Location: [This PC ▼]  Type: [All Types ▼]             │
│  Search for: [_______________]  [Search] [Stop]         │
│  ☑ Files  ☑ Folders  ☐ Case sensitive  ☐ Exact name     │
├──────────────────────────────────────────────────────────┤
│  Scanning: C:\Users\...\Documents                        │
│  [████████████░░░░░░░░░░░░░░░░]                          │
├──────────────────────────────────────────────────────────┤
│  Full path                    │ Type   │ Size            │
│  C:\Users\...\report.pdf      │ File   │ 2.3 MB          │
│  C:\Users\...\Projects        │ Folder │                 │
│  D:\Backup\report.docx        │ File   │ 845.1 KB        │
└──────────────────────────────────────────────────────────┘
```

1. **Location** चुनें — `This PC` (सभी drives) या कोई specific drive
2. **Type** चुनें — All Types, Documents, Images, Videos, आदि
3. **Name** type करें → **Search** दबाएं
4. Background में scan चलेगा — UI responsive रहेगा
5. **Double-click** करके folder खोलें

---

## 📋 Requirements

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| Tkinter | Python के साथ bundled |
| OS | Windows 7+, Linux, macOS |

कोई external package नहीं।

---

## 🎯 Use Cases

| काम | कैसे |
|-----|------|
| कोई file ढूंढना | Name type करें → Search |
| सारी PDFs ढूंढना | Type = Documents, Name = `.pdf` |
| सारी images | Type = Images, Name खाली छोड़ें |
| Specific folder | Name = folder name, Folders ✅ |
| Case-sensitive | "Case sensitive" ✅ |
| Exact match | "Exact name" ✅ |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Tkinter import error (Linux) | `sudo apt install python3-tk` |
| Search बहुत धीमा | Single drive चुनें, Type filter लगाएं |
| कुछ results नहीं मिले | Permissions issue — Administrator से run करें |
| UI freeze हो गया | Stop दबाएं, फिर से Search करें |
| Stop काम नहीं कर रहा | Thread को exit होने में 1-2 sec लगते हैं |

विस्तृत guide: [`USER_GUIDE.md`](USER_GUIDE.md)

---

## 📁 Project Structure

```
file-search/
├── file_search.py       # Main script
├── requirements.txt      # (खाली — कोई dependency नहीं)
├── README.md            # This file
└── USER_GUIDE.md        # Detailed guide
```

---

## 🔒 Privacy

- ❌ कोई file content पढ़ा नहीं जाता
- ❌ कोई data internet पर नहीं जाता
- ❌ कोई telemetry नहीं
- ✅ सिर्फ़ filenames और folders scan होते हैं
- ✅ पूरी तरह offline

---

## ⚡ Performance Tips

| Tip | फ़ायदा |
|-----|--------|
| Single drive चुनें | 3-5x तेज़ |
| Type filter लगाएं | 2-4x तेज़ |
| Exact name use करें | कम false positives |
| Case sensitive ✅ | थोड़ा तेज़ |
| ज़रूरत न हो तो Folders uncheck | 10-20% तेज़ |

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Contributing

Bug report या feature request के लिए issue खोलें।

---

**Happy searching! 🔍**