import os
import time
import datetime
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import win32gui
import win32process
import psutil
from PIL import Image, ImageOps

from vision.screenshot import capture_screen
from vision.ocr import extract_text
from database.database import (
    create_pending_memory,
    update_memory,
    get_user_setting,
)
from ai.embeddings import create_embedding


CAPTURE_PROBE_SECONDS = 2
MEMORY_INTERVAL_SECONDS = 5
IDLE_THRESHOLD_SECONDS = 30
MAX_INACTIVE_MEMORIES = 5
SCREEN_CHANGE_THRESHOLD = 0.012
AI_ENRICHMENT_INTERVAL_SECONDS = 30
ACCESSIBILITY_MAX_CHARS = 12000


from memory.activity import get_idle_seconds

def extract_accessibility_text(hwnd, max_chars=ACCESSIBILITY_MAX_CHARS):
    """Best-effort Windows UI Automation extraction.

    Accessibility/UIA is preferred over OCR because it is cheaper and usually
    cleaner for native apps, browsers and standard controls.
    """
    try:
        from pywinauto import Desktop

        window = Desktop(backend="uia").window(handle=hwnd)
        texts = window.texts()

        cleaned = []
        seen = set()

        for value in texts:
            value = " ".join((value or "").split())

            if not value or value in seen:
                continue

            seen.add(value)
            cleaned.append(value)

            if sum(len(item) + 1 for item in cleaned) >= max_chars:
                break

        return "\n".join(cleaned)[:max_chars]

    except Exception as exc:
        print(f"ℹ️ Accessibility extraction unavailable: {exc}")
        return ""


class MemoryRecorder:

    def __init__(self, user_id, callback=None):

        self.user_id = user_id
        self.running = False
        self.last_window = None
        self.callback = callback

        self.inactive_memory_count = 0
        self.paused_for_inactivity = False

        self.last_probe = None
        self.last_meaningful_capture = 0.0
        self.last_ai_enrichment = 0.0

        self.processing_pool = ThreadPoolExecutor(max_workers=1)

    # --------------------------------------------------
    # ACTIVE WINDOW
    # --------------------------------------------------

    def get_active_window(self):

        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return "Unknown", "Unknown", 0

        title = win32gui.GetWindowText(hwnd).strip()

        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app = process.name()
        except Exception:
            app = "Unknown"

        return app, title, hwnd

    # --------------------------------------------------
    # SCREEN CHANGE
    # --------------------------------------------------

    def _screen_changed(self, screenshot_path):

        try:
            current = Image.open(screenshot_path).convert("L")
            current = ImageOps.fit(
                current,
                (96, 54),
                method=Image.Resampling.BILINEAR,
            )

            current = np.asarray(current, dtype=np.float32) / 255.0

            if self.last_probe is None:
                self.last_probe = current
                return True

            difference = float(
                np.mean(np.abs(current - self.last_probe))
            )

            changed = difference >= SCREEN_CHANGE_THRESHOLD

            if changed:
                self.last_probe = current

            return changed

        except Exception as exc:
            print(f"⚠️ Screen-change check failed: {exc}")
            return True

    def _discard_screenshot(self, path):

        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception as exc:
            print(f"⚠️ Screenshot cleanup failed: {exc}")

    # --------------------------------------------------
    # LOCAL CONTEXT
    # --------------------------------------------------

    def _build_local_context(self, app, title, accessibility_text, ocr_text):
        text = accessibility_text or ocr_text

        if text:
            text = text[:ACCESSIBILITY_MAX_CHARS]
            return (
                f"Application: {app}\n"
                f"Window: {title}\n"
                f"Visible UI text:\n{text}"
            )

        return (
            f"Application: {app}\n"
            f"Window: {title}\n"
            f"Screen changed, but no readable UI text was available."
        )

    # --------------------------------------------------
    # START
    # --------------------------------------------------

    def start(self):

        self.running = True

        print("🧠 Adaptive memory recorder started")

        while self.running:

            cycle_start = time.time()

            try:

                app, title, hwnd = self.get_active_window()

                if not title:
                    time.sleep(1)
                    continue

                current_window = (app, title)
                window_changed = (
                    self.last_window is not None
                    and current_window != self.last_window
                )

                idle_seconds = get_idle_seconds()

                # App/window changes are meaningful context changes.
                if window_changed:
                    self.inactive_memory_count = 0
                    self.paused_for_inactivity = False
                    self.last_ai_enrichment = 0.0
                    print(
                        f"🔄 Context changed: {self.last_window} -> "
                        f"{current_window}"
                    )

                # User activity wakes the recorder immediately.
                if idle_seconds <= IDLE_THRESHOLD_SECONDS:

                    if self.paused_for_inactivity:
                        print(
                            "▶️ User activity detected. "
                            "Resuming memory capture."
                        )

                    self.inactive_memory_count = 0
                    self.paused_for_inactivity = False

                else:

                    if (
                        self.inactive_memory_count
                        >= MAX_INACTIVE_MEMORIES
                    ):

                        if not self.paused_for_inactivity:
                            print(
                                "⏸️ Memory processing paused after "
                                f"{MAX_INACTIVE_MEMORIES} inactive memories."
                            )

                        self.paused_for_inactivity = True

                        # Lightweight monitoring only. No screenshot,
                        # OCR, embedding or Gemini work while paused.
                        time.sleep(1)
                        continue

                    print(
                        f"😴 Inactivity detected ({idle_seconds:.0f}s). "
                        f"Inactive memory allowance: "
                        f"{self.inactive_memory_count}/{MAX_INACTIVE_MEMORIES} already used."
                    )

                # --------------------------------------------------
                # 1. CHEAP CAPTURE PROBE
                # --------------------------------------------------

                screenshot_path = capture_screen()

                if not self._screen_changed(screenshot_path):

                    print("⏭️ Screen unchanged; skipping memory creation.")
                    self._discard_screenshot(screenshot_path)

                    elapsed = time.time() - cycle_start
                    time.sleep(max(0, CAPTURE_PROBE_SECONDS - elapsed))
                    continue

                if (
                    self.last_meaningful_capture
                    and time.time() - self.last_meaningful_capture
                    < MEMORY_INTERVAL_SECONDS
                ):
                    print("⏱️ Screen changed too soon; delaying memory creation.")
                    self._discard_screenshot(screenshot_path)

                    elapsed = time.time() - cycle_start
                    time.sleep(max(0, CAPTURE_PROBE_SECONDS - elapsed))
                    continue

                now = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # --------------------------------------------------
                # 2. UI CALLBACK
                # --------------------------------------------------

                if self.callback:

                    try:
                        self.callback(app, title, now)
                    except Exception as exc:
                        print(f"⚠️ UI callback error: {exc}")

                # --------------------------------------------------
                # 3. ACCESSIBILITY FIRST
                # --------------------------------------------------

                accessibility_text = extract_accessibility_text(hwnd)

                if accessibility_text:
                    print("♿ Accessibility text extracted.")
                    ocr_text = accessibility_text
                else:
                    print("🔎 Accessibility unavailable; running OCR...")
                    ocr_text = extract_text(screenshot_path)

                # --------------------------------------------------
                # 4. LOCAL MEMORY FIRST
                # --------------------------------------------------

                local_summary = self._build_local_context(
                    app,
                    title,
                    accessibility_text,
                    ocr_text,
                )

                keep_screenshot = get_user_setting(self.user_id)

                stored_screenshot = (
                    screenshot_path if keep_screenshot else ""
                )

                memory_id = create_pending_memory(
                    self.user_id,
                    app,
                    title,
                    now,
                    stored_screenshot,
                )

                embedding = create_embedding(
                    local_summary + "\n" + ocr_text
                )

                update_memory(
                    memory_id,
                    local_summary,
                    ocr_text,
                    embedding,
                    0,
                    "",
                )

                print(
                    f"💾 Local memory created: ID {memory_id}"
                )

                if idle_seconds > IDLE_THRESHOLD_SECONDS:
                    self.inactive_memory_count += 1
                    print(
                        f"😴 Inactive memory stored "
                        f"{self.inactive_memory_count}/{MAX_INACTIVE_MEMORIES}."
                    )

                self.last_window = current_window
                self.last_meaningful_capture = current_time

                if not keep_screenshot:
                    self._discard_screenshot(screenshot_path)

            except Exception as exc:

                print(
                    f"❌ MEMORY RECORDER ERROR: "
                    f"{type(exc).__name__}: {exc}"
                )

            # --------------------------------------------------
            # ADAPTIVE CAPTURE INTERVAL
            # --------------------------------------------------

            elapsed = time.time() - cycle_start

            # Probes are cheap and frequent. Expensive processing only
            # happens for changed screens.
            remaining = max(
                0,
                CAPTURE_PROBE_SECONDS - elapsed,
            )

            if self.running:
                time.sleep(remaining)

    # --------------------------------------------------
    # STOP
    # --------------------------------------------------

    def stop(self):

        self.running = False

        print("🛑 Memory recorder stopped")

    # --------------------------------------------------
    # LEGACY BACKGROUND PROCESSING
    # --------------------------------------------------

    def process_memory(
        self,
        memory_id,
        screenshot_path,
        keep_screenshot,
    ):

        try:

            ocr_text = extract_text(screenshot_path)

            summary = (
                "Local screen context\n"
                + ocr_text[:ACCESSIBILITY_MAX_CHARS]
            )

            embedding = create_embedding(
                summary + "\n" + ocr_text
            )

            contains_error = 0
            error_text = ""

            keywords = [
                "Traceback",
                "Exception",
                "ImportError",
                "ModuleNotFoundError",
                "TypeError",
                "ValueError",
                "SyntaxError",
                "RuntimeError",
                "RESOURCE_EXHAUSTED",
                "AttributeError",
                "NameError",
            ]

            for word in keywords:

                if word.lower() in summary.lower():
                    contains_error = 1
                    error_text = summary
                    break

            update_memory(
                memory_id,
                summary,
                ocr_text,
                embedding,
                contains_error,
                error_text,
            )

        except Exception as exc:

            print(
                f"❌ Background processing error for memory "
                f"{memory_id}: {type(exc).__name__}: {exc}"
            )

        finally:

            if not keep_screenshot:
                self._discard_screenshot(screenshot_path)
