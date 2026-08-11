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

class MemoryRecorder:

    def __init__(self, callback=None):
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

            app, title = self.get_active_window()

            if title != self.last_window:

                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                screenshot_path = capture_screen()

                ocr_text = extract_text(screenshot_path)

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
                
                combined = summary + "\n" + ocr_text

                embedding = create_embedding(combined)

                save_memory(
                    app,
                    title,
                    now,
                    screenshot_path,
                    summary,
                    ocr_text,
                    embedding,
                    contains_error,
                    error_text,
                    
                )
                if self.callback:
                 self.callback(app, title, now)
                print(f"Saved: {app} | {title}")
                print(summary)
                print("-" * 60)

                self.last_window = title

            time.sleep(5)

    def stop(self):

        self.running = False