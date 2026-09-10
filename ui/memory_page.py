import customtkinter as ctk
import sqlite3

from ui.theme import (
    BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT,
    ACCENT, ACCENT_HOVER,
)


class MemoryPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build_ui()
        self.load_memories()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))

        ctk.CTkLabel(header, text="Memory History", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Browse the activity JARVIS has remembered from your computer.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 0))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=42, pady=(18, 12))
        self.count_label = ctk.CTkLabel(toolbar, text="Recent memories", font=("Segoe UI", 12, "bold"), text_color=TEXT_DIM)
        self.count_label.pack(side="left")

        self.refresh_btn = ctk.CTkButton(toolbar, text="↻  Refresh", command=self.load_memories, width=110, height=38, corner_radius=10, fg_color=SURFACE_ALT, hover_color="#172536", border_width=1, border_color=BORDER_HOVER, text_color=TEXT_BRIGHT)
        self.refresh_btn.pack(side="right")

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(0, 12))

        body = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        body.pack(fill="both", expand=True, padx=42, pady=(0, 30))

        self.memory_box = ctk.CTkTextbox(body, fg_color="transparent", border_width=0, corner_radius=14, text_color=TEXT_SOFT, font=("Segoe UI", 12), wrap="word", scrollbar_button_color=BORDER, scrollbar_button_hover_color=ACCENT_HOVER)
        self.memory_box.pack(fill="both", expand=True, padx=22, pady=20)

    def load_memories(self):
        self.memory_box.configure(state="normal")
        self.memory_box.delete("1.0", "end")

        try:
            conn = sqlite3.connect("second_brain.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, app_name, window_title
                FROM memories
                ORDER BY id DESC
                LIMIT 100
            """)
            rows = cursor.fetchall()
            conn.close()
        except sqlite3.Error as e:
            self.memory_box.insert("end", f"Could not load memories.\n\n{e}")
            self.memory_box.configure(state="disabled")
            return

        self.count_label.configure(text=f"{len(rows)} recent memor{'y' if len(rows) == 1 else 'ies'}")

        if not rows:
            self.memory_box.insert("end", "No memories recorded yet.\n\nStart Memory from the Dashboard to begin building your digital memory.")
            self.memory_box.configure(state="disabled")
            return

        for index, (timestamp, app, title) in enumerate(rows):
            if index:
                self.memory_box.insert("end", "\n" + "─" * 72 + "\n\n")
            self.memory_box.insert("end", f"{timestamp}\n", ("time",))
            self.memory_box.insert("end", f"{app}\n", ("app",))
            self.memory_box.insert("end", f"{title}\n", ("title",))

        # CustomTkinter CTkTextbox intentionally forbids a per-tag font because
        # tag fonts bypass CustomTkinter's scaling system. Keep the global font
        # and use tags only for colors.
        self.memory_box.tag_config("time", foreground=TEXT_DIM)
        self.memory_box.tag_config("app", foreground=ACCENT)
        self.memory_box.tag_config("title", foreground=TEXT_BRIGHT)
        self.memory_box.configure(state="disabled")
