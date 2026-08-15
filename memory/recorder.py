import os
import win32gui
import win32process
import psutil
import datetime
import time
from vision.screenshot import capture_screen
from ai.gemini import summarize_screen
from vision.ocr import extract_text
from database.database import save_memory
from ai.embeddings import create_embedding
from database.database import (
    save_memory,
    get_user_setting
)


class MemoryRecorder:

    def __init__(self, user_id, callback=None):
        self.user_id = user_id
        self.running = False
        self.last_window = ""
        self.callback = callback

    def get_active_window(self):

        hwnd = win32gui.GetForegroundWindow()

        title = win32gui.GetWindowText(hwnd)

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        try:
            process = psutil.Process(pid)
            app = process.name()

        except:
            app = "Unknown"

        return app, title

    def start(self):

        self.running = True

        while self.running:

            screenshot_path = None

            try:
                app, title = self.get_active_window()

                if title != self.last_window:

                    now = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # 1. Capture temporary screenshot
                    screenshot_path = capture_screen()

                    # 2. OCR
                    ocr_text = extract_text(screenshot_path)

                    # 3. Generate summary
                    summary = summarize_screen(
                        screenshot_path,
                        ocr_text
                    )
                    keep_screenshot = get_user_setting(self.user_id)
                    if not keep_screenshot:

                        try:
                            if screenshot_path and os.path.exists(screenshot_path):
                                os.remove(screenshot_path)
                                screenshot_path = ""

                        except Exception as e:
                            print(f"Could not delete screenshot: {e}")
                    # 4. Detect errors
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

                    # 5. Create embedding
                    combined = summary + "\n" + ocr_text

                    embedding = create_embedding(combined)

                    # 6. Save memory
                    save_memory(
                        self.user_id,
                        app,
                        title,
                        now,
                        screenshot_path,
                        summary,
                        ocr_text,
                        embedding,
                        contains_error,
                        error_text
                    )

                    # 7. Callback
                    if self.callback:
                        self.callback(
                            app,
                            title,
                            now
                        )

                    print(
                        f"Saved: {app} | {title}"
                    )

                    print(summary)
                    print("-" * 60)

                    self.last_window = title

            except Exception as e:

                print("⚠️ Memory recording error:")
                print(e)

            finally:

                if screenshot_path:

                    save_screenshots = get_user_setting(
                        self.user_id
                    )

                    if not save_screenshots:
                        self.delete_screenshot(
                            screenshot_path
                        )

            time.sleep(5)

    def stop(self):

        self.running = False

    def delete_screenshot(self, path):
        if not path:
            return

        if not os.path.exists(path):
            return

        try:
            os.remove(path)
            print(f"🗑️ Deleted temporary screenshot: {path}")
        except Exception as e:
            print(f"⚠️ Could not delete screenshot: {e}")    
