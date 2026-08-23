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

        self.running = True
    
        while self.running:
    
            try:
                print("\n🧠 Memory recorder cycle started")
    
                # 1. Get current active window
                app, title = self.get_active_window()
    
                print(f"🪟 Active window: {app} | {title}")
    
                if not title:
                    time.sleep(5)
                    continue
    
                # 2. Timestamp
                now = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
    
                # 3. Screenshot setting
                keep_screenshot = get_user_setting(
                    self.user_id
                )
    
                print(
                    f"2️⃣ Screenshot retention: "
                    f"{keep_screenshot}"
                )
    
                # 4. Capture screenshot
                screenshot_path = capture_screen()
    
                print(
                    f"3️⃣ Screenshot captured: "
                    f"{screenshot_path}"
                )
    
                # 5. OCR
                ocr_text = extract_text(
                    screenshot_path
                )
    
                print("4️⃣ OCR completed")
    
                # 6. Gemini summary
                summary = summarize_screen(
                    screenshot_path,
                    ocr_text
                )
    
                print("5️⃣ Gemini summary completed")
    
                # 7. Embedding
                combined = (
                    summary +
                    "\n" +
                    ocr_text
                )
    
                embedding = create_embedding(
                    combined
                )
    
                print("6️⃣ Embedding completed")
    
                # 8. Detect errors
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
    
                for word in keywords:
    
                    if word.lower() in summary.lower():
    
                        contains_error = 1
                        error_text = summary
                        break
    
                # 9. Decide screenshot storage
                stored_screenshot = (
                    screenshot_path
                    if keep_screenshot
                    else ""
                )
    
                print("7️⃣ Saving memory...")
    
                # 10. SAVE EVERY 5 SECONDS
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
    
                # 11. Delete temporary screenshot
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
    
                # ==================================================
                # IMPORTANT:
                # UPDATE DASHBOARD EVERY 5 SECONDS
                # NOT ONLY WHEN WINDOW CHANGES
                # ==================================================
    
                if self.callback:
    
                    try:
    
                        self.callback(
                            app,
                            title,
                            now
                        )
    
                    except Exception as callback_error:
    
                        print(
                            "⚠️ Dashboard callback failed:",
                            callback_error
                        )
    
                # Remember current window
                self.last_window = (
                    app,
                    title
                )
    
            except Exception as e:
    
                print(
                    f"❌ MEMORY RECORDER FAILED: "
                    f"{type(e).__name__}: {e}"
                )
    
            # EXACTLY 5 SECOND INTERVAL
            time.sleep(1)    
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
