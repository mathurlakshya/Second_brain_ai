import os
import threading
import win32gui
import win32process
import psutil
import datetime
import time

from vision.screenshot import capture_screen
from ai.gemini import summarize_screen
from vision.ocr import extract_text
from database.database import save_memory, get_user_setting
from ai.embeddings import create_embedding


class MemoryRecorder:

    CAPTURE_INTERVAL = 5.0

    def __init__(self, user_id, callback=None):

        self.user_id = user_id
        self.running = False
        self.callback = callback

        # Prevent multiple start() calls from creating
        # multiple recorder loops.
        self.thread = None

    # ==========================================================
    # ACTIVE WINDOW
    # ==========================================================

    def get_active_window(self):

        try:

            hwnd = win32gui.GetForegroundWindow()

            if not hwnd:
                return "Unknown", "Unknown"

            title = win32gui.GetWindowText(hwnd).strip()

            try:

                _, pid = win32process.GetWindowThreadProcessId(hwnd)

                process = psutil.Process(pid)

                app = process.name()

            except Exception:

                app = "Unknown"

            return app, title

        except Exception as e:

            print(
                f"⚠️ Active window detection failed: {e}"
            )

            return "Unknown", "Unknown"

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        # Already running
        if self.running:

            print(
                "⚠️ Memory recorder is already running"
            )

            return

        self.running = True

        print(
            "🧠 Memory recorder started "
            "(5 second capture interval)"
        )

        # ------------------------------------------------------
        # Capture loop
        # ------------------------------------------------------

        while self.running:

            cycle_start = time.monotonic()

            try:

                print(
                    "\n🧠 Memory recorder cycle started"
                )

                # ----------------------------------------------
                # Get current foreground window
                # ----------------------------------------------

                app, title = self.get_active_window()

                print(
                    f"🪟 Active window: "
                    f"{app} | {title}"
                )

                if not title:

                    print(
                        "⏳ No active window title. "
                        "Skipping this cycle."
                    )

                else:

                    # ------------------------------------------
                    # Capture screenshot IMMEDIATELY
                    # ------------------------------------------

                    screenshot_path = capture_screen()

                    print(
                        f"📸 Screenshot captured: "
                        f"{screenshot_path}"
                    )

                    # ------------------------------------------
                    # IMPORTANT
                    #
                    # Processing happens in a separate thread.
                    # Therefore the recorder does NOT wait for
                    # OCR/Gemini/embedding before the next 5 sec
                    # capture.
                    # ------------------------------------------

                    processing_thread = threading.Thread(
                        target=self.process_screenshot,
                        args=(
                            screenshot_path,
                            app,
                            title
                        ),
                        daemon=True
                    )

                    processing_thread.start()

            except Exception as e:

                print(
                    f"❌ MEMORY CAPTURE FAILED: "
                    f"{type(e).__name__}: {e}"
                )

            # ==================================================
            # KEEP CAPTURE INTERVAL AT 5 SECONDS
            # ==================================================

            elapsed = (
                time.monotonic()
                - cycle_start
            )

            remaining = max(
                0,
                self.CAPTURE_INTERVAL - elapsed
            )

            if remaining > 0:

                time.sleep(remaining)

        print(
            "🔴 Memory recorder loop stopped"
        )

    # ==========================================================
    # PROCESS SCREENSHOT
    # ==========================================================

    def process_screenshot(
        self,
        screenshot_path,
        app,
        title
    ):

        keep_screenshot = False

        try:

            print(
                f"🔄 Processing screenshot: "
                f"{app} | {title}"
            )

            # --------------------------------------------------
            # Timestamp
            # --------------------------------------------------

            now = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # --------------------------------------------------
            # Screenshot retention setting
            # --------------------------------------------------

            keep_screenshot = get_user_setting(
                self.user_id
            )

            print(
                f"📸 Screenshot retention: "
                f"{keep_screenshot}"
            )

            # --------------------------------------------------
            # OCR
            # --------------------------------------------------

            ocr_text = extract_text(
                screenshot_path
            )

            print(
                "4️⃣ OCR completed"
            )

            # --------------------------------------------------
            # Gemini summary
            # --------------------------------------------------

            summary = summarize_screen(
                screenshot_path,
                ocr_text
            )

            print(
                "5️⃣ Gemini summary completed"
            )

            # --------------------------------------------------
            # Embedding
            # --------------------------------------------------

            combined = (
                str(summary)
                + "\n"
                + str(ocr_text)
            )

            embedding = create_embedding(
                combined
            )

            print(
                "6️⃣ Embedding completed"
            )

            # --------------------------------------------------
            # Error detection
            # --------------------------------------------------

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
                "NameError"

            ]

            summary_text = str(summary)

            for word in keywords:

                if word.lower() in summary_text.lower():

                    contains_error = 1

                    error_text = summary_text

                    break

            # --------------------------------------------------
            # Screenshot path
            # --------------------------------------------------

            stored_screenshot = (
                screenshot_path
                if keep_screenshot
                else ""
            )

            # --------------------------------------------------
            # SAVE MEMORY
            # --------------------------------------------------

            print(
                "7️⃣ Saving memory..."
            )

            save_memory(
                self.user_id,
                app,
                title,
                now,
                stored_screenshot,
                summary,
                ocr_text,
                embedding,
                contains_error,
                error_text
            )

            print(
                f"8️⃣ ✅ Memory saved: "
                f"{app} | {title}"
            )

            # --------------------------------------------------
            # Update Dashboard
            # --------------------------------------------------

            if self.callback:

                try:

                    self.callback(
                        app,
                        title,
                        now
                    )

                except Exception as e:

                    print(
                        f"⚠️ Dashboard callback failed: "
                        f"{e}"
                    )

            # --------------------------------------------------
            # Delete temporary screenshot
            # --------------------------------------------------

            if not keep_screenshot:

                try:

                    if (
                        screenshot_path
                        and os.path.exists(
                            screenshot_path
                        )
                    ):

                        os.remove(
                            screenshot_path
                        )

                        print(
                            f"🗑️ Deleted temporary screenshot: "
                            f"{screenshot_path}"
                        )

                except Exception as e:

                    print(
                        f"⚠️ Screenshot cleanup failed: "
                        f"{e}"
                    )

        except Exception as e:

            print(
                f"❌ MEMORY PROCESSING FAILED: "
                f"{type(e).__name__}: {e}"
            )

            # --------------------------------------------------
            # Cleanup screenshot even if processing fails
            # --------------------------------------------------

            if (
                not keep_screenshot
                and screenshot_path
            ):

                try:

                    if os.path.exists(
                        screenshot_path
                    ):

                        os.remove(
                            screenshot_path
                        )

                except Exception:
                    pass

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        if not self.running:

            return

        print(
            "🔴 Stopping memory recorder..."
        )

        self.running = False

        print(
            "🔴 Memory recorder stopped"
        )
