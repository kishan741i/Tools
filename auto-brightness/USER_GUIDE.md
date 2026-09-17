# 📖 Auto Brightness — User Guide

पूरी guide — setup, configuration, और troubleshooting।

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [First Run](#-first-run)
3. [Configuration](#-configuration)
4. [Tuning Guide](#-tuning-guide)
5. [Troubleshooting](#-troubleshooting)
6. [Advanced Usage](#-advanced-usage)
7. [FAQ](#-faq)

---

## 🛠 Installation

### Step 1: Python Install

- Python 3.8 या नया version डाउनलोड करें: https://python.org
- Install करते समय **"Add Python to PATH"** ज़रूर tick करें

### Step 2: Dependencies

```bash
pip install -r requirements.txt
```

अगर error आए तो:

```bash
python -m pip install --upgrade pip
pip install opencv-python numpy screen-brightness-control
```

### Step 3: Verify

```bash
python -c "import cv2; print('OpenCV OK')"
python -c "import screen_brightness_control; print('SBC OK')"
```

दोनों OK आएं तो installation सही है।

---

## 🚀 First Run

### Normal run

```bash
python auto_brightness.py
```

### Output ऐसा दिखेगा

```
============================================================
🏆 Smart Auto Brightness — Optimized
============================================================
AVG_CHANGE_THRESHOLD = 20
CHANGE_THRESHOLD     = 3
PRINT_INTERVAL       = 2.0s
============================================================
✅ Camera thread शुरू
🔍 avg=4.2 | smooth=4.2 | state=black | last=unknown
🚫 Black — no change
🔍 avg=93.5 | smooth=93.5 | state=visible | last=black

👁  Adjust — शटर खुला (edge)
   📷 93.5 (smooth=93.5) | Screen 45% → 48%
   ✅ Fade → 48%
```

### Band करने के लिए

`Ctrl + C` दबाएं

---

## ⚙️ Configuration

सारी settings `auto_brightness.py` के ऊपर **CONFIG** section में हैं।

### 1. Camera Settings

```python
CAMERA_INDEX = 0        # 0 = default, 1 = दूसरा camera
FRAME_WIDTH = 160       # कम = fast, ज़्यादा = accurate
FRAME_HEIGHT = 120
```

**कौन सा camera index use करें?**
- Built-in laptop camera → `0`
- External USB camera → `1` या `2`
- अगर `0` काम न करे → `1, 2, 3` try करें

### 2. Brightness Range

```python
MIN_BRIGHTNESS = 15     # सबसे कम (रात के लिए)
MAX_BRIGHTNESS = 100    # सबसे ज़्यादा (दिन के लिए)
```

**Recommendations:**

| Environment | MIN | MAX |
|-------------|-----|-----|
| Normal room | 15 | 100 |
| Dark room | 5 | 80 |
| Bright office | 25 | 100 |

### 3. Trigger Thresholds

```python
BLACK_FRAME_LIMIT     = 8    # Shutter बंद detect
AVG_CHANGE_THRESHOLD  = 20   # Brightness बदलाव trigger
CHANGE_THRESHOLD      = 3    # Screen पर minimum बदलाव
```

**क्या करते हैं?**

| Parameter | कम करें | बढ़ाएं |
|-----------|---------|--------|
| `BLACK_FRAME_LIMIT` | Shutter sensitive | Shutter insensitive |
| `AVG_CHANGE_THRESHOLD` | तेज़ response | Stable |
| `CHANGE_THRESHOLD` | Fine adjustment | मोटा adjustment |

### 4. Smoothing

```python
SMOOTH_FACTOR = 0.3     # 0 = कोई smoothing नहीं, 1 = बहुत smooth
```

- `0.1` → तेज़ response, थोड़ा jumpy
- `0.3` → **balanced (default)**
- `0.5` → smooth, slow response

### 5. Performance

```python
CHECK_INTERVAL = 1.0    # हर 1 सेकंड check
MAX_FRAME_AGE  = 0.15   # 150ms stale frame threshold
PRINT_INTERVAL = 2.0    # हर 2 सेकंड print
```

---

## 🎯 Tuning Guide

### Scenario 1: Brightness बहुत बार बदल रही है

```python
AVG_CHANGE_THRESHOLD = 30    # 20 → 30
SMOOTH_FACTOR = 0.4          # 0.3 → 0.4
CHECK_INTERVAL = 2.0         # 1.0 → 2.0
```

### Scenario 2: Brightness बदल ही नहीं रही

```python
AVG_CHANGE_THRESHOLD = 10    # 20 → 10
CHANGE_THRESHOLD = 2         # 3 → 2
```

### Scenario 3: रात में बहुत तेज़ brightness

```python
MIN_BRIGHTNESS = 5           # 15 → 5
```

### Scenario 4: Shutter बंद है लेकिन visible detect हो रहा

```python
BLACK_FRAME_LIMIT = 15       # 8 → 15
```

या script चलाकर देखें:
```
🔍 avg=XX.X | state=black     ← सही
🔍 avg=XX.X | state=visible   ← गलत, BLACK_FRAME_LIMIT बढ़ाएं
```

### Scenario 5: CPU बहुत use हो रहा

```python
CHECK_INTERVAL = 2.0         # 1.0 → 2.0
FRAME_WIDTH = 80             # 160 → 80
FRAME_HEIGHT = 60            # 120 → 60
PRINT_INTERVAL = 5.0         # 2.0 → 5.0
```

---

## 🐛 Troubleshooting

### ❌ Problem: Camera नहीं खुल रहा

**Solution:**
```python
CAMERA_INDEX = 1   # 0, 1, 2, 3 try करें
```

अगर फिर भी नहीं:
- Windows Settings → Privacy → Camera → "Allow apps" ON करें
- कोई और app camera use कर रही हो तो बंद करें

### ❌ Problem: Brightness adjust नहीं हो रहा

**Check 1:** Output में `👁 Adjust` आ रहा है?

- **नहीं** → `AVG_CHANGE_THRESHOLD = 10` करें
- **हाँ, लेकिन screen नहीं बदली** → permissions issue

**Windows में:**
```bash
# Administrator के रूप में run करें
```

**Check 2:** `sbc.set_brightness()` काम करता है?

```bash
python -c "import screen_brightness_control as sbc; sbc.set_brightness(50)"
```

### ❌ Problem: Shutter बंद होने पर भी "visible"

**Solution:**
```python
BLACK_FRAME_LIMIT = 15   # बढ़ाएं
```

या frame छोटा करें:
```python
FRAME_WIDTH = 80
FRAME_HEIGHT = 60
```

### ❌ Problem: Brightness झटके से बदलती है

**Solution:**
```python
SMOOTH_FACTOR = 0.5     # बढ़ाएं
```

या fade steps बढ़ाएं — `_do_fade()` method में:
```python
steps, delay = 25, 0.04    # छोटे बदलाव के लिए
```

### ❌ Problem: बहुत ज़्यादा print output

**Solution:**
```python
PRINT_INTERVAL = 10.0    # 2.0 → 10.0
```

या print हटाएं:
```python
def log(self, msg, force=False):
    return   # सब print बंद
```

### ❌ Problem: "Doosra instance already chal raha hai"

**Solution:**
```bash
# Windows
taskkill /F /IM pythonw.exe
taskkill /F /IM python.exe

# या lock file delete करें
del .guard.lock
```

---

## 🚀 Advanced Usage

### 1. Startup पर Auto-run (Windows)

**Method 1: Startup Folder**

1. `Win + R` → `shell:startup` → Enter
2. `auto_brightness.bat` बनाएं:

```bat
@echo off
start "" pythonw "C:\path\to\auto_brightness.py"
```

3. उस folder में रखें

**Method 2: Task Scheduler**

1. Task Scheduler खोलें
2. Create Basic Task
3. Trigger: "When I log on"
4. Action: `pythonw.exe` + script path
5. "Run whether user is logged on or not" ✅

### 2. Background में चलाना (No console)

```bash
pythonw auto_brightness.py
```

`pythonw` = Python without console window

### 3. Log File बनाना

Script के अंत में जोड़ें:

```python
import logging
logging.basicConfig(
    filename='brightness.log',
    level=logging.INFO,
    format='%(asctime)s | %(message)s'
)
```

और `print()` की जगह:
```python
logging.info(f"avg={cam_val:.1f}")
```

### 4. Multiple Monitors

```python
# सभी monitors पर brightness set
sbc.set_brightness(target)                # सभी
sbc.set_brightness(target, display=0)     # सिर्फ़ पहला
sbc.set_brightness(target, display=1)     # दूसरा
```

### 5. System Tray Icon (Advanced)

```bash
pip install pystray Pillow
```

फिर script में जोड़ें:

```python
from pystray import Icon, Menu, MenuItem
from PIL import Image

def on_pause(icon, item):
    ctrl.running = False

def on_quit(icon, item):
    ctrl.running = False
    icon.stop()

icon = Icon("AutoBrightness",
            Image.new('RGB', (64, 64), 'blue'),
            menu=Menu(
                MenuItem('Pause', on_pause),
                MenuItem('Quit', on_quit)
            ))
icon.run()
```

---

## ❓ FAQ

### Q1: क्या यह हर लैपटॉप पर काम करेगा?

**A:** हाँ, अगर:
- Python 3.8+ है
- Camera है
- `screen_brightness_control` supported है (Windows, Linux, macOS)

### Q2: Camera LED हमेशा जलती रहती है?

**A:** हाँ, क्योंकि camera लगातार चल रही है। इसे कम करने के लिए:
- `CHECK_INTERVAL = 2.0` करें
- या भौतिक camera cover लगाएं

### Q3: Data कहीं भेजा जाता है?

**A:** नहीं। सब कुछ local है। Camera frame कभी save/upload नहीं होता, सिर्फ़ average number use होती है।

### Q4: Battery पर कितना असर?

**A:** बहुत कम (~2-3% extra). Camera thread 50 FPS पर चलती है, लेकिन frames छोटे (160×120) हैं।

### Q5: External monitor पर काम करेगा?

**A:** DDC/CI support पर depend करता है। अगर monitor DDC/CI supported है तो हाँ।

### Q6: Brightness बहुत धीमी बदलती है?

**A:** `_do_fade()` में steps कम करें:
```python
steps, delay = 5, 0.01    # तेज़
```

### Q7: Multiple instances चला सकते हैं?

**A:** नहीं, `.guard.lock` file single instance enforce करती है।

### Q8: Script क्रैश हो गई, अब नहीं चल रही?

**A:**
```bash
del .guard.lock
python auto_brightness.py
```

### Q9: Mac/Linux पर?

**A:** हाँ, screen_brightness_control cross-platform है। पर कुछ Linux distros में extra setup चाहिए:
```bash
sudo apt install xrandr
```

### Q10: Python install किए बिना चला सकते हैं?

**A:** हाँ, PyInstaller से `.exe` बनाएं:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole auto_brightness.py
```

`dist/auto_brightness.exe` मिलेगा।

---

## 📞 Support

- 🐛 Bug report → GitHub Issues
- 💡 Feature request → GitHub Issues
- 📧 Email → mokariyakishan741@email.com

---

## 📜 License

MIT License — free to use, modify, distribute.

---

**Happy auto-brightness! 🌗**