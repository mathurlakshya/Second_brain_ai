import os
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

        except Exception:
            app = "Unknown"

        return app, title

    def start(self):

        self.running = True

        while self.running:

            try:

                app, title = self.get_active_window()

                if title != self.last_window:

                    now = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Get the user's screenshot preference.
                    # This is defined BEFORE it is used.
                    keep_screenshot = get_user_setting(
                        self.user_id
                    )

                    print(
                        f"Screenshot retention: "
                        f"{keep_screenshot}"
                    )

                    # Capture screenshot temporarily.
                    screenshot_path = capture_screen()

                    # OCR
                    ocr_text = extract_text(
                        screenshot_path
                    )

                    # Gemini summary
                    summary = summarize_screen(
                        screenshot_path,
                        ocr_text
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
                        "NameError"
                    ]

                    for word in keywords:

                        if word.lower() in summary.lower():

                            contains_error = 1
                            error_text = summary

                            break

                    combined = (
                        summary
                        + "\n"
                        + ocr_text
                    )

                    embedding = create_embedding(
                        combined
                    )

                    # If screenshots are disabled,
                    # don't store a permanent path.
                    stored_screenshot_path = (
                        screenshot_path
                        if keep_screenshot
                        else ""
                    )

                    # Save memory.
                    save_memory(
                        app,
                        title,
                        now,
                        stored_screenshot_path,
                        summary,
                        ocr_text,
                        embedding,
                        contains_error,
                        error_text
                    )

                    # Delete temporary screenshot
                    # when the user doesn't want
                    # screenshot retention.
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
                                    "🗑️ Deleted temporary "
                                    f"screenshot: "
                                    f"{screenshot_path}"
                                )

                        except Exception as e:

                            print(
                                "⚠️ Could not delete "
                                f"screenshot: {e}"
                            )

                    if self.callback:

                        self.callback(
                            app,
                            title,
                            now
                        )

                    print(
                        f"✅ Saved: {app} | {title}"
                    )

                    print(summary)

                    print("-" * 60)

                    self.last_window = title

            except Exception as e:

                print(
                    "⚠️ Memory recording error:"
                )

                print(
                    repr(e)
                )

            time.sleep(5)

    def stop(self):

        self.running = False
