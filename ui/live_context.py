import customtkinter as ctk
import threading
import time

from vision.screenshot import capture_screen
from ai.gemini import analyze_screen, ask_about_screen, save_context
from ui.theme import BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, ACCENT, ACCENT_HOVER


class LiveContext(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="Live Context", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(side="left")
        self.status = ctk.CTkLabel(header, text="● Ready", font=("Segoe UI", 12, "bold"), text_color=TEXT_SOFT)
        self.status.pack(side="right", pady=(8, 0))
        ctk.CTkLabel(self, text="Let JARVIS understand your current screen and answer questions about it.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", padx=42, pady=(0, 14))
        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(0, 14))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=42, pady=(0, 14))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = self.create_panel(body, "✦  CURRENT SCREEN", 0)
        right = self.create_panel(body, "✦  JARVIS", 1)

        self.analysis_box = ctk.CTkTextbox(left, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Consolas", 12), wrap="word")
        self.analysis_box.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.analysis_box.insert("end", "Capture your current desktop to let JARVIS understand what is on screen.")

        self.chat_box = ctk.CTkTextbox(right, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Segoe UI", 13), wrap="word")
        self.chat_box.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.chat_box.insert("end", "JARVIS\n\nAnalyze your screen first, then ask questions about it.\n\n")

        controls = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        controls.pack(fill="x", padx=42, pady=(0, 30))
        self.refresh_btn = ctk.CTkButton(controls, text="Capture & Analyze", width=170, height=42, corner_radius=10, command=self.refresh_context, fg_color=ACCENT, hover_color="#3EC5EF", text_color=BG)
        self.refresh_btn.pack(side="left", padx=18, pady=15)
        self.question_entry = ctk.CTkEntry(controls, height=42, corner_radius=10, fg_color=SURFACE_ALT, border_color=BORDER_HOVER, text_color=TEXT_BRIGHT, placeholder_text="Ask anything about this screen...")
        self.question_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=15)
        self.question_entry.bind("<Return>", lambda e: self.ask_screen_question())
        self.ask_btn = ctk.CTkButton(controls, text="Send  ➜", width=105, height=42, corner_radius=10, command=self.ask_screen_question, fg_color=SURFACE_ALT, hover_color="#172536", border_width=1, border_color=BORDER_HOVER, text_color=TEXT_BRIGHT)
        self.ask_btn.pack(side="right", padx=(0, 18), pady=15)

    def create_panel(self, parent, title, column):
        panel = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=14)
        panel.grid(row=0, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
        ctk.CTkLabel(panel, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(18, 12))
        return panel

    def refresh_context(self):
        self.status.configure(text="● Capturing...", text_color="#F6C76A")
        self.analysis_box.delete("1.0", "end")
        self.analysis_box.insert("end", "Capturing your desktop...\n\nPlease wait.")
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        app = self.winfo_toplevel()
        self.after(0, app.withdraw)
        time.sleep(0.8)
        image_path = capture_screen()
        self.after(0, app.deiconify)
        result = analyze_screen(image_path)
        save_context(result)
        self.after(0, lambda: self.show_analysis(result))

    def show_analysis(self, result):
        self.status.configure(text="● Screen Ready", text_color="#6EE7A8")
        self.analysis_box.delete("1.0", "end")
        self.analysis_box.insert("end", result)
        self.chat_box.insert("end", "JARVIS\n\nScreen analyzed successfully. You can now ask questions about it.\n\n")
        self.chat_box.see("end")

    def ask_screen_question(self):
        question = self.question_entry.get().strip()
        if not question:
            return
        self.question_entry.delete(0, "end")
        self.chat_box.insert("end", f"YOU\n{question}\n\nJARVIS\nThinking...\n\n")
        self.chat_box.see("end")
        threading.Thread(target=self.get_answer, args=(question,), daemon=True).start()

    def get_answer(self, question):
        try:
            answer = ask_about_screen(question)
        except Exception as e:
            answer = str(e)
        self.after(0, lambda: self.show_answer(answer))

    def show_answer(self, answer):
        content = self.chat_box.get("1.0", "end")
        marker = "JARVIS\nThinking...\n\n"
        if marker in content:
            content = content.rsplit(marker, 1)[0]
            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("end", content)
        self.chat_box.insert("end", f"JARVIS\n{answer}\n\n")
        self.chat_box.see("end")
