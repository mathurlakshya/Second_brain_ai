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
                print("\n🧠 Memory recorder cycle started")
    
                app, title = self.get_active_window()
    
                print(f"🪟 Active window: {app} | {title}")
    
                if title and title != self.last_window:
    
                    print("1️⃣ Window changed")
    
                    now = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
    
                    keep_screenshot = get_user_setting(
                        self.user_id
                    )
    
                    print(
                        f"2️⃣ Screenshot retention: "
                        f"{keep_screenshot}"
                    )
    
                    screenshot_path = capture_screen()
    
                    print(
                        f"3️⃣ Screenshot captured: "
                        f"{screenshot_path}"
                    )
    
                    ocr_text = extract_text(
                        screenshot_path
                    )
    
                    print("4️⃣ OCR completed")
    
                    summary = summarize_screen(
                        screenshot_path,
                        ocr_text
                    )
    
                    print("5️⃣ Gemini summary completed")
    
                    combined = summary + "\n" + ocr_text
    
                    embedding = create_embedding(
                        combined
                    )
    
                    print("6️⃣ Embedding completed")
    
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
    
                    stored_screenshot = (
                        screenshot_path
                        if keep_screenshot
                        else ""
                    )
    
                    print("7️⃣ Saving memory...")
    
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
    
                    if self.callback:
    
                        self.callback(
                            app,
                            title,
                            now
                        )
    
                    self.last_window = title
    
                else:
    
                    print("⏳ Same window — waiting...")
    
            except Exception as e:
    
                print(
                    f"❌ MEMORY RECORDER FAILED: "
                    f"{type(e).__name__}: {e}"
                )
    
            time.sleep(5)    
    def stop(self):
       self.running = False
