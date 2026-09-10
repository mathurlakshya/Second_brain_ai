import threading
import customtkinter as ctk

from ai.thought_thread_chat import ask_memory_thread_chat
from ui.theme import (
    BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT,
    ACCENT, ACCENT_HOVER,
)


class SearchPage(ctk.CTkFrame):

    def __init__(self, parent, user_id=None):
        super().__init__(parent, fg_color=BG)
        self.user_id = user_id
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))

        ctk.CTkLabel(
            header,
            text="Memory Assistant",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Ask JARVIS about your past work, coding sessions, files, or browsing history.",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(
            fill="x", padx=42, pady=(20, 14)
        )

        chat_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        chat_panel.pack(fill="both", expand=True, padx=42, pady=(0, 14))

        top = ctk.CTkFrame(chat_panel, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(18, 8))
        ctk.CTkLabel(
            top,
            text="✦  JARVIS",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
        ).pack(side="left")
        ctk.CTkLabel(
            top,
            text="Thought Thread search",
            font=("Segoe UI", 11),
            text_color=TEXT_DIM,
        ).pack(side="right")

        self.chat_box = ctk.CTkTextbox(
            chat_panel,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_SOFT,
            font=("Segoe UI", 13),
            wrap="word",
        )
        self.chat_box.pack(fill="both", expand=True, padx=22, pady=(0, 10))
        self.chat_box.insert(
            "end",
            "✦  JARVIS\n\n"
            "Hello! I remember your previous work.\n"
            "Ask me anything about your recorded memories.\n\n"
        )
        self.chat_box.configure(state="disabled")

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=42, pady=(0, 30))

        self.entry = ctk.CTkEntry(
            input_frame,
            height=44,
            corner_radius=10,
            fg_color=SURFACE_ALT,
            border_color=BORDER_HOVER,
            text_color=TEXT_BRIGHT,
            placeholder_text="Ask about your memories...",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self.run_search())

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send  ➜",
            width=110,
            height=44,
            corner_radius=10,
            command=self.run_search,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=BG,
        )
        self.send_button.pack(side="right")

    def run_search(self):
        question = self.entry.get().strip()
        if not question:
            return

        self.entry.delete(0, "end")
        self.append_chat(f"\nYOU\n{question}\n\n", "user")
        self.append_chat("JARVIS\nThinking across your Thought Threads...\n\n", "jarvis")
        self.entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.chat_box.see("end")

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True,
        ).start()

    def get_answer(self, question):
        try:
            if self.user_id is not None:
                answer = ask_memory_thread_chat(question, self.user_id)
            else:
                # Compatibility fallback for older callers.
                from ai.gemini import ask_memory_chat
                answer = ask_memory_chat(question)
        except Exception as e:
            answer = f"I couldn't search your memories right now.\n\nError: {e}"

        self.after(0, lambda: self.show_answer(answer))

    def show_answer(self, answer):
        self.remove_thinking()
        self.append_chat(f"JARVIS\n{answer}\n\n", "jarvis")
        self.entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.entry.focus_set()
        self.chat_box.see("end")

    def append_chat(self, text, tag=None):
        self.chat_box.configure(state="normal")
        if tag:
            self.chat_box.insert("end", text, tag)
        else:
            self.chat_box.insert("end", text)
        self.chat_box.tag_config(
            "user",
            foreground=ACCENT[0] if ctk.get_appearance_mode().lower() == "light" else ACCENT[1],
            font=("Segoe UI", 12, "bold"),
        )
        self.chat_box.tag_config(
            "jarvis",
            foreground=TEXT[0] if ctk.get_appearance_mode().lower() == "light" else TEXT[1],
            font=("Segoe UI", 12, "bold"),
        )
        self.chat_box.configure(state="disabled")

    def remove_thinking(self):
        self.chat_box.configure(state="normal")
        content = self.chat_box.get("1.0", "end-1c")
        marker = "JARVIS\nThinking across your Thought Threads...\n\n"
        if content.endswith(marker):
            content = content[:-len(marker)]
            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("end", content)
        self.chat_box.configure(state="disabled")
