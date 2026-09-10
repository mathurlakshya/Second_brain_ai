import customtkinter as ctk

from memory.thought_threads import (
    get_thought_threads,
    get_thread_memories,
    rebuild_threads,
)
from ui.theme import (
    BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT,
    ACCENT, ACCENT_HOVER, SUCCESS, WARNING,
)


class ThoughtThreadsPage(ctk.CTkFrame):
    """A timeline of coherent work streams discovered from memory embeddings."""

    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color=BG)
        self.user_id = user_id
        self.selected_thread_id = None
        self.thread_buttons = []
        self.build_ui()
        self.load_threads()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))

        ctk.CTkLabel(
            header,
            text="✦ Thought Threads",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(side="left")

        self.rebuild_btn = ctk.CTkButton(
            header,
            text="↻ Organize Memories",
            width=150,
            height=38,
            corner_radius=10,
            command=self.rebuild,
            fg_color=SURFACE_ALT,
            hover_color=BORDER_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_BRIGHT,
        )
        self.rebuild_btn.pack(side="right")

        ctk.CTkLabel(
            self,
            text="Your memories grouped into continuous streams of work, study, research, and ideas.",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=42)

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(
            fill="x", padx=42, pady=(20, 14)
        )

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=42, pady=(0, 30))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self.thread_list = ctk.CTkScrollableFrame(
            body,
            fg_color=SURFACE,
            corner_radius=14,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT_HOVER,
        )
        self.thread_list.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        detail = ctk.CTkFrame(body, fg_color="transparent")
        detail.grid(row=0, column=1, sticky="nsew")

        self.detail_title = ctk.CTkLabel(
            detail,
            text="Select a thread",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        )
        self.detail_title.pack(anchor="w", pady=(4, 2))

        self.detail_meta = ctk.CTkLabel(
            detail,
            text="",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED,
        )
        self.detail_meta.pack(anchor="w", pady=(0, 12))

        ctk.CTkFrame(detail, height=1, fg_color=BORDER).pack(fill="x", pady=(0, 12))

        self.detail_box = ctk.CTkTextbox(
            detail,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_SOFT,
            font=("Segoe UI", 13),
            wrap="word",
        )
        self.detail_box.pack(fill="both", expand=True)

    def load_threads(self):
        for button in self.thread_buttons:
            try:
                button.destroy()
            except Exception:
                pass
        self.thread_buttons.clear()

        threads = get_thought_threads(self.user_id, limit=40)

        if not threads:
            ctk.CTkLabel(
                self.thread_list,
                text="No Thought Threads yet.\n\nStart Memory to create them automatically.",
                font=("Segoe UI", 13),
                text_color=TEXT_MUTED,
                justify="left",
            ).pack(anchor="w", padx=8, pady=15)
            return

        for thread in threads:
            thread_id, title, created, updated, last_seen, count, status = thread
            button = ctk.CTkButton(
                self.thread_list,
                text=f"✦  {title}\n    {count} memories  ·  {status}",
                height=62,
                corner_radius=10,
                anchor="w",
                command=lambda tid=thread_id: self.select_thread(tid),
                fg_color="transparent",
                hover_color=SURFACE_ALT,
                text_color=TEXT,
                border_width=0,
            )
            button.pack(fill="x", padx=4, pady=3)
            self.thread_buttons.append(button)

        if self.selected_thread_id is None or not any(
            row[0] == self.selected_thread_id for row in threads
        ):
            self.select_thread(threads[0][0])

    def select_thread(self, thread_id):
        self.selected_thread_id = thread_id

        threads = get_thought_threads(self.user_id, limit=40)
        thread = next((row for row in threads if row[0] == thread_id), None)
        if thread is None:
            return

        _, title, created, updated, last_seen, count, status = thread
        self.detail_title.configure(text=f"✦  {title}")
        self.detail_meta.configure(
            text=f"{count} memories  ·  {status}  ·  Last seen {last_seen}"
        )

        memories = get_thread_memories(self.user_id, thread_id, limit=30)
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")

        if not memories:
            self.detail_box.insert("end", "No memories are attached to this thread yet.")
        else:
            for index, (timestamp, app, window_title, summary, ocr) in enumerate(memories):
                if index:
                    self.detail_box.insert("end", "\n" + "─" * 72 + "\n\n")
                self.detail_box.insert("end", f"{timestamp}\n", ("time",))
                self.detail_box.insert("end", f"{app}  ·  {window_title}\n\n", ("app",))
                self.detail_box.insert("end", f"{summary or 'Processing...'}\n")

        if memories:
            self.detail_box.tag_config("time", foreground=self._tag(TEXT_DIM))
            self.detail_box.tag_config("app", foreground=self._tag(ACCENT))
        self.detail_box.configure(state="disabled")

    @staticmethod
    def _tag(color):
        if isinstance(color, (tuple, list)):
            return color[0] if ctk.get_appearance_mode().lower() == "light" else color[1]
        return color

    def rebuild(self):
        self.rebuild_btn.configure(state="disabled", text="Organizing...")
        self.update_idletasks()
        try:
            rebuild_threads(self.user_id)
            self.selected_thread_id = None
            self.load_threads()
        finally:
            self.rebuild_btn.configure(state="normal", text="↻ Organize Memories")
