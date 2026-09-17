# 🌗 Auto Brightness

Camera से ambient light detect करके screen की brightness automatically adjust करने वाला Python tool।

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

---

## ✨ Features

- 🎥 **Camera-based** — ambient light खुद measure करता है
- 🚫 **Shutter-aware** — camera बंद (black frame) हो तो कुछ नहीं करता
- 🌊 **Smooth fade** — brightness gradually बदलती है, झटका नहीं
- ⚡ **Optimized** — ~2% CPU, threaded camera + adaptive fade
- 🔒 **Privacy-first** — कोई data save/upload नहीं होता
- 🎯 **Smart triggers** — सिर्फ़ ज़रूरत पर brightness बदलता है

---

## 🚀 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Run

```bash
python auto_brightness.py
```

### 3. Background में चलाने के लिए

```bash
pythonw auto_brightness.py
```

---

## 📸 कैसे काम करता है?

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Camera     │───▶│  Average     │───▶│   Screen     │
│   Frame      │    │  Brightness  │    │  Brightness  │
└──────────────┘    └──────────────┘    └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Decision    │
                  │  Logic       │
                  └──────────────┘
```

1. Camera हर 1 सेकंड में frame capture करता है
2. Frame की average brightness निकाली जाती है (0-255)
3. Black frame (shutter बंद) → कोई action नहीं
4. Visible frame → brightness smoothly adjust होती है
5. बदलाव बड़ा हो तो ही adjust, वरना skip

---

## 📋 Requirements

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| OS | Windows 10/11, Linux, macOS |
| Camera | कोई भी (built-in या USB) |

---

## ⚙️ Configuration

`auto_brightness.py` के ऊपर **CONFIG** section में settings बदलें:

```python
CAMERA_INDEX          = 0      # कौन सा camera (0, 1, 2)
CHECK_INTERVAL        = 1.0    # हर 1 सेकंड check
MIN_BRIGHTNESS        = 15     # Minimum screen brightness (%)
MAX_BRIGHTNESS        = 100    # Maximum screen brightness (%)
BLACK_FRAME_LIMIT     = 8      # Shutter बंद threshold
AVG_CHANGE_THRESHOLD  = 20     # Brightness बदलाव threshold
SMOOTH_FACTOR         = 0.3    # Camera smoothing (0-1)
```

पूरी tuning guide के लिए [`USER_GUIDE.md`](USER_GUIDE.md) देखें।

---

## 🎬 Usage Examples

### Normal run

```bash
python auto_brightness.py
```

### Background (Windows)

```bash
pythonw auto_brightness.py
```

### Startup पर auto-run (Windows)

1. `Win + R` → `shell:startup` → Enter
2. `auto_brightness.bat` का shortcut वहाँ रखें:

```bat
@echo off
start "" pythonw "C:\path\to\auto_brightness.py"
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera नहीं खुला | `CAMERA_INDEX = 1, 2, 3` try करें |
| Brightness adjust नहीं हो रहा | `AVG_CHANGE_THRESHOLD = 10` करें |
| बहुत ज़्यादा बदलाव | `AVG_CHANGE_THRESHOLD = 40` करें |
| Shutter बंद होने पर भी visible | `BLACK_FRAME_LIMIT = 15` करें |
| CPU ज़्यादा | `CHECK_INTERVAL = 2.0` करें |

विस्तृत troubleshooting: [`USER_GUIDE.md`](USER_GUIDE.md)

---

## 📁 Project Structure

```
auto-brightness/
├── auto_brightness.py       # Main script
├── requirements.txt          # Dependencies
├── README.md                # This file
├── USER_GUIDE.md            # Detailed guide
└── .guard.lock              # Runtime lock (auto-generated)
```

---

## 🔒 Privacy

- ❌ कोई image/video save नहीं होता
- ❌ कोई data internet पर नहीं जाता
- ❌ कोई user tracking नहीं
- ✅ सिर्फ़ average brightness number use होती है

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Contributing

Bug report या feature request के लिए issue खोलें।

---

## ⭐ Credits

Built with:
- [OpenCV](https://opencv.org/) — Camera capture
- [screen-brightness-control](https://github.com/Crozzers/screen_brightness_control) — Brightness API
- [NumPy](https://numpy.org/) — Math

---

**Enjoy automatic brightness! 🌗**