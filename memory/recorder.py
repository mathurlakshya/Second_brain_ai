import os
import win32gui
import win32process
import psutil
import datetime
import time

from concurrent.futures import ThreadPoolExecutor
from vision.screenshot import capture_screen
from ai.gemini import summarize_screen
from vision.ocr import extract_text

from database.database import (
    create_pending_memory,
    update_memory,
    get_user_setting
)

from ai.embeddings import create_embedding


class MemoryRecorder:

    def __init__(self, user_id, callback=None):

        self.user_id = user_id
        self.running = False
        self.last_window = None
        self.callback = callback

        self.processing_pool = ThreadPoolExecutor(
            max_workers=1
        )

    # --------------------------------------------------
    # ACTIVE WINDOW
    # --------------------------------------------------

    def get_active_window(self):

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

    # --------------------------------------------------
    # START
    # --------------------------------------------------

    def start(self):

        self.running = True

        print("🧠 Memory recorder started")

        while self.running:

            cycle_start = time.time()

            try:

                # ==========================================
                # 1. GET CURRENT WINDOW
                # ==========================================

                app, title = self.get_active_window()

                print(
                    f"\n🪟 Active window: "
                    f"{app} | {title}"
                )

                if not title:

                    time.sleep(1)
                    continue

                current_window = (app, title)
            
                # ==========================================
                # 2. CAPTURE SCREENSHOT
                # ==========================================

                screenshot_path = capture_screen()

                print(
                    f"📸 Screenshot captured: "
                    f"{screenshot_path}"
                )

                now = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # ==========================================
                # 3. IMMEDIATELY UPDATE UI
                # ==========================================

                if self.callback:

                    try:

                        self.callback(
                            app,
                            title,
                            now
                        )

                    except Exception as e:

                        print(
                            f"⚠️ UI callback error: {e}"
                        )

                print(
                    "⚡ UI updated immediately "
                    "after screenshot"
                )

                # ==========================================
                # 4. CREATE MEMORY IMMEDIATELY
                # ==========================================

                keep_screenshot = get_user_setting(
                    self.user_id
                )

                stored_screenshot = (
                    screenshot_path
                    if keep_screenshot
                    else ""
                )

                memory_id = create_pending_memory(
                    self.user_id,
                    app,
                    title,
                    now,
                    stored_screenshot
                )

                print(
                    f"💾 Memory created immediately: "
                    f"ID {memory_id}"
                )

                # ==========================================
                # 5. OCR
                # ==========================================

                print("🔎 Starting OCR...")

                ocr_text = extract_text(
                    screenshot_path
                )

                print("✅ OCR completed")

                # ==========================================
                # 6. GEMINI SUMMARY
                # ==========================================

                print("🤖 Starting Gemini summary...")

                summary = summarize_screen(
                    screenshot_path,
                    ocr_text
                )

                print("✅ Gemini summary completed")

                # ==========================================
                # 7. EMBEDDING
                # ==========================================

                print("🧠 Creating embedding...")

                combined = (
                    summary +
                    "\n" +
                    ocr_text
                )

                embedding = create_embedding(
                    combined
                )

                print("✅ Embedding completed")

                # ==========================================
                # 8. ERROR DETECTION
                # ==========================================

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

                # ==========================================
                # 9. UPDATE SAME MEMORY
                # ==========================================

                update_memory(
                    memory_id,
                    summary,
                    ocr_text,
                    embedding,
                    contains_error,
                    error_text
                )

                print(
                    f"✅ Memory fully processed: "
                    f"ID {memory_id}"
                )

                # ==========================================
                # 10. DELETE TEMP SCREENSHOT
                # ==========================================

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
                                f"🗑️ Deleted temporary "
                                f"screenshot: "
                                f"{screenshot_path}"
                            )

                    except Exception as e:

                        print(
                            f"⚠️ Screenshot cleanup failed: "
                            f"{e}"
                        )

                self.last_window = current_window

            except Exception as e:

                print(
                    f"❌ MEMORY RECORDER ERROR: "
                    f"{type(e).__name__}: {e}"
                )

            # ==========================================
            # KEEP 5-SECOND CAPTURE INTERVAL
            # ==========================================

            elapsed = time.time() - cycle_start

            remaining = max(
                0,
                5 - elapsed
            )

            if self.running:

                time.sleep(remaining)

    # --------------------------------------------------
    # STOP
    # --------------------------------------------------

    def stop(self):

        self.running = False

        print("🛑 Memory recorder stopped")

    def process_memory(
        self,
        memory_id,
        screenshot_path,
        keep_screenshot
    ):
    
        try:
    
            # ==========================================
            # OCR
            # ==========================================
    
            print(
                f"🔎 OCR started for memory {memory_id}"
            )
    
            ocr_text = extract_text(
                screenshot_path
            )
    
            print(
                f"✅ OCR completed for memory {memory_id}"
            )
    
            # ==========================================
            # GEMINI
            # ==========================================
    
            summary = summarize_screen(
                screenshot_path,
                ocr_text
            )
    
            print(
                f"✅ Gemini completed for memory {memory_id}"
            )
    
            # ==========================================
            # EMBEDDING
            # ==========================================
    
            combined = (
                summary +
                "\n" +
                ocr_text
            )
    
            embedding = create_embedding(
                combined
            )
    
            print(
                f"✅ Embedding completed for memory {memory_id}"
            )
    
            # ==========================================
            # ERROR DETECTION
            # ==========================================
    
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
    
            # ==========================================
            # UPDATE MEMORY
            # ==========================================
    
            update_memory(
                memory_id,
                summary,
                ocr_text,
                embedding,
                contains_error,
                error_text
            )
    
            print(
                f"🧠 Memory {memory_id} fully processed"
            )
    
        except Exception as e:
    
            print(
                f"❌ Background processing error "
                f"for memory {memory_id}: "
                f"{type(e).__name__}: {e}"
            )
    
        finally:
    
            # ==========================================
            # DELETE TEMP SCREENSHOT
            # ==========================================
    
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
                        f"⚠️ Screenshot cleanup failed: {e}"
                    )
