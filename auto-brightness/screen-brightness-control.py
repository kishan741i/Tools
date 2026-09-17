import cv2
import numpy as np
import screen_brightness_control as sbc
import time
import threading

# ================= CONFIG =================
CAMERA_INDEX          = 0
CHECK_INTERVAL        = 1.0
MIN_BRIGHTNESS        = 15
MAX_BRIGHTNESS        = 100
SMOOTH_FACTOR         = 0.3
BLACK_FRAME_LIMIT     = 8
CHANGE_THRESHOLD      = 3
AVG_CHANGE_THRESHOLD  = 20
FRAME_WIDTH           = 160
FRAME_HEIGHT          = 120
MAX_FRAME_AGE         = 0.15
PRINT_INTERVAL        = 2.0     # ✅ हर 2 सेकंड में print
# ==========================================


# ---------- Camera Thread (optimized) ----------
class CameraReader:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        for _ in range(5):
            self.cap.grab()

        self.gray = None            # ✅ grayscale cache
        self.frame_time = 0
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("✅ Camera thread शुरू")

    def _loop(self):
        while self.running:
            for _ in range(2):
                self.cap.grab()
            ret, frame = self.cap.retrieve()
            if ret:
                # ✅ यहीं grayscale convert
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                with self.lock:
                    self.gray = gray
                    self.frame_time = time.monotonic()
            time.sleep(0.02)

    def get_brightness(self):
        with self.lock:
            gray = self.gray
            frame_time = self.frame_time

        if gray is None:
            return None, True

        age = time.monotonic() - frame_time
        if age > MAX_FRAME_AGE:
            for _ in range(2):
                self.cap.grab()
            ret, frame = self.cap.retrieve()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                with self.lock:
                    self.gray = gray
                    self.frame_time = time.monotonic()

        # ✅ cv2.mean सबसे तेज़
        avg = float(cv2.mean(gray)[0])
        return avg, avg < BLACK_FRAME_LIMIT

    def stop(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()


# ---------- Brightness Controller (optimized) ----------
class BrightnessController:
    def __init__(self):
        self.cam = None
        self.running = True
        self.last_state = "unknown"
        self.last_adjusted_avg = None
        self.smoothed_cam = None
        self.last_target = None
        self.last_print = 0

        # ✅ Single long-lived fade thread
        self.fade_request = None
        self.fade_event = threading.Event()
        self.fade_lock = threading.Lock()
        self.fade_thread = threading.Thread(target=self._fade_worker, daemon=True)
        self.fade_thread.start()

    @staticmethod
    def map_to_screen(cam_value):
        cam_min, cam_max = 20, 200
        if cam_value <= cam_min:
            return MIN_BRIGHTNESS
        if cam_value >= cam_max:
            return MAX_BRIGHTNESS
        ratio = (cam_value - cam_min) / (cam_max - cam_min)
        return int(MIN_BRIGHTNESS + ratio * (MAX_BRIGHTNESS - MIN_BRIGHTNESS))

    # ---------- Fade worker (long-lived) ----------
    def _fade_worker(self):
        while self.running:
            self.fade_event.wait(timeout=0.5)
            self.fade_event.clear()

            with self.fade_lock:
                req = self.fade_request
                self.fade_request = None

            if req is None:
                continue

            start, target = req
            self._do_fade(start, target)

    def _do_fade(self, start, target):
        diff_abs = abs(target - start)

        # ✅ Adaptive steps — बड़े बदलाव पर तेज़
        if diff_abs > 40:
            steps, delay = 10, 0.02
        elif diff_abs > 15:
            steps, delay = 15, 0.025
        else:
            steps, delay = 25, 0.03

        diff = target - start
        last_set = start

        for i in range(1, steps + 1):
            if not self.running:
                return
            t = i / steps
            ease = 1 - (1 - t) ** 3
            value = int(round(start + diff * ease))
            value = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, value))

            # ✅ Skip duplicate values
            if abs(value - last_set) < 1:
                continue

            try:
                sbc.set_brightness(value)
                last_set = value
            except Exception:
                return
            time.sleep(delay)

        # Final exact value
        try:
            sbc.set_brightness(target)
            self.last_target = target
            print(f"   ✅ Fade → {target}%")
        except Exception:
            pass

    def fade_brightness(self, target, current):
        if current is None:
            try:
                sbc.set_brightness(target)
                self.last_target = target
            except Exception:
                pass
            return target
        if abs(target - current) < 1:
            return current

        with self.fade_lock:
            self.fade_request = (current, target)
        self.fade_event.set()
        return target

    # ---------- Throttled print ----------
    def log(self, msg, force=False):
        now = time.monotonic()
        if force or (now - self.last_print) >= PRINT_INTERVAL:
            print(msg)
            self.last_print = now

    # ---------- Main loop ----------
    def run(self):
        # Initial brightness — सिर्फ़ एक बार
        try:
            cur = sbc.get_brightness(display=0)
            self.last_target = cur[0] if isinstance(cur, list) else cur
        except Exception:
            self.last_target = None

        self.cam = CameraReader(CAMERA_INDEX)

        try:
            while self.running:
                loop_start = time.monotonic()

                cam_val, is_black = self.cam.get_brightness()

                if cam_val is None:
                    time.sleep(CHECK_INTERVAL)
                    continue

                state = "black" if is_black else "visible"

                # Smoothing — सिर्फ़ visible के लिए, और सिर्फ़ ज़रूरत पर
                if state == "visible":
                    if self.smoothed_cam is None:
                        self.smoothed_cam = cam_val
                    elif abs(cam_val - self.smoothed_cam) >= 2:
                        self.smoothed_cam = (SMOOTH_FACTOR * self.smoothed_cam +
                                             (1 - SMOOTH_FACTOR) * cam_val)
                    smoothed = self.smoothed_cam
                else:
                    smoothed = cam_val

                # ============ DECISION ============
                should_adjust = False
                reason = ""

                if state == "black":
                    if self.last_state != "black":
                        self.log(f"🚫 Black — no change", force=True)
                    self.last_state = "black"
                    self.last_adjusted_avg = None

                elif state == "visible":
                    if self.last_state != "visible":
                        should_adjust = True
                        reason = "शटर खुला (edge)"
                    else:
                        if self.last_adjusted_avg is None:
                            should_adjust = True
                            reason = "पहली visible"
                        elif abs(smoothed - self.last_adjusted_avg) >= AVG_CHANGE_THRESHOLD:
                            should_adjust = True
                            reason = (f"avg बदला "
                                      f"({self.last_adjusted_avg:.1f}→{smoothed:.1f})")

                    self.last_state = "visible"

                # ============ ADJUST ============
                if should_adjust:
                    target = self.map_to_screen(smoothed)

                    if self.last_target is None or abs(target - self.last_target) >= CHANGE_THRESHOLD:
                        print(f"\n👁  Adjust — {reason}")
                        print(f"   📷 {cam_val:.1f} (smooth={smoothed:.1f}) | "
                              f"Screen {self.last_target}% → {target}%")
                        self.fade_brightness(target, self.last_target)
                        self.last_adjusted_avg = smoothed
                    else:
                        self.log(f"   📷 No change (target={target}%)")
                        self.last_adjusted_avg = smoothed

                # Debug log — throttled
                self.log(f"🔍 avg={cam_val:.1f} | smooth={smoothed:.1f} | "
                         f"state={state} | last={self.last_state}")

                elapsed = time.monotonic() - loop_start
                time.sleep(max(0, CHECK_INTERVAL - elapsed))

        finally:
            self.running = False
            self.fade_event.set()   # worker को जगाओ
            if self.fade_thread.is_alive():
                self.fade_thread.join(timeout=1)
            if self.cam:
                self.cam.stop()
            print("🛑 बंद")


if __name__ == "__main__":
    print("=" * 60)
    print("🏆 Smart Auto Brightness — Optimized")
    print("=" * 60)
    print(f"AVG_CHANGE_THRESHOLD = {AVG_CHANGE_THRESHOLD}")
    print(f"CHANGE_THRESHOLD     = {CHANGE_THRESHOLD}")
    print(f"PRINT_INTERVAL       = {PRINT_INTERVAL}s")
    print("=" * 60)

    ctrl = BrightnessController()
    try:
        ctrl.run()
    except KeyboardInterrupt:
        ctrl.running = False
        print("\n✅ Exiting...")