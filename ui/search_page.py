import customtkinter as ctk

from ai.gemini import ask_memory_chat
from ui.theme import BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, ACCENT, ACCENT_HOVER


class SearchPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))

        ctk.CTkLabel(header, text="Memory Assistant", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Ask JARVIS about your past work, coding sessions, files, or browsing history.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(20, 14))

        chat_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        chat_panel.pack(fill="both", expand=True, padx=42, pady=(0, 14))

        top = ctk.CTkFrame(chat_panel, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(18, 8))
        ctk.CTkLabel(top, text="✦  JARVIS", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(top, text="Semantic memory search", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(side="right")

        self.chat_box = ctk.CTkTextbox(chat_panel, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Segoe UI", 13), wrap="word")
        self.chat_box.pack(fill="both", expand=True, padx=22, pady=(0, 10))
        self.chat_box.insert("end", "✦  JARVIS\n\nHello! I remember your previous work.\nAsk me anything about your recorded memories.\n\n")

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=42, pady=(0, 30))

        self.entry = ctk.CTkEntry(input_frame, height=44, corner_radius=10, fg_color=SURFACE_ALT, border_color=BORDER_HOVER, text_color=TEXT_BRIGHT, placeholder_text="Ask about your memories...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.run_search())

        ctk.CTkButton(input_frame, text="Send  ➜", width=110, height=44, corner_radius=10, command=self.run_search, fg_color=ACCENT, hover_color="#3EC5EF", text_color=BG).pack(side="right")

    def run_search(self):
        question = self.entry.get().strip()
        if not question:
            return

        self.chat_box.insert("end", f"\nYOU\n{question}\n\n", ("user",))
        self.entry.delete(0, "end")
        self.chat_box.insert("end", "JARVIS\nThinking...\n\n", ("jarvis",))
        self.chat_box.see("end")

        try:
            answer = ask_memory_chat(question)
        except Exception as e:
            answer = f"I couldn't search your memories right now.\n\nError: {e}"

        content = self.chat_box.get("1.0", "end")
        marker = "JARVIS\nThinking...\n\n"
        if marker in content:
            content = content.rsplit(marker, 1)[0]
            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("end", content)

        self.chat_box.insert("end", f"JARVIS\n{answer}\n\n")
        self.chat_box.see("end")
        self.chat_box.tag_config("user", foreground=ACCENT, font=("Segoe UI", 12, "bold"))
        self.chat_box.tag_config("jarvis", foreground=TEXT, font=("Segoe UI", 12, "bold"))
