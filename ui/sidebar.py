import customtkinter as ctk

from memory.thought_threads import get_thought_threads
from ui.theme import (
    SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_BRIGHT
)


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, change_page, username, user_id=None):
        super().__init__(
            parent,
            width=230,
            fg_color=SURFACE,
            corner_radius=0
        )

        self.username = username
        self.user_id = user_id
        self.change_page = change_page
        self.account_menu = None
        self.thread_rows = []
        self.thread_refresh_job = None
        self.grid_propagate(False)

        title = ctk.CTkLabel(
            self,
            text="🧠 Second Brain",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT
        )
        title.pack(pady=(30, 25))

        self.create_button("🏠 Dashboard", "dashboard")
        self.create_button("🧠 Memory", "memory")
        self.create_button("👁 Live Context", "live_context")
        self.create_button("🔍 Search", "search")
        self.create_button("📜 Analytics", "analytics")
        self.create_button("⚙️ Settings", "settings")

        # Thought Threads live directly below Settings. The section starts
        # empty and populates automatically once five sufficiently similar
        # memories have been detected for the same activity.
        self.thread_section = ctk.CTkFrame(self, fg_color="transparent")
        self.thread_section.pack(fill="x", padx=15, pady=(14, 0))

        ctk.CTkLabel(
            self.thread_section,
            text="THOUGHT THREADS",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        self.thread_empty_label = ctk.CTkLabel(
            self.thread_section,
            text="No thought threads yet",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.thread_empty_label.pack(fill="x", pady=(0, 2))

        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(expand=True, fill="both")

        ctk.CTkFrame(
            self,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", padx=15, pady=(0, 10))

        self.bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=0,
            pady=(0, 15)
        )

        self.account_button = ctk.CTkButton(
            self.bottom_frame,
            text=f"👤  {self.username}  ▾",
            command=self.show_account_menu,
            height=42,
            corner_radius=10,
            fg_color=SURFACE_ALT,
            hover_color=BORDER_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_BRIGHT,
            anchor="w"
        )
        self.account_button.pack(fill="x", padx=15)

        self.refresh_thought_threads()

    def create_button(self, text, page):
        """Create a flat navigation item: text by default, surface only on hover."""
        btn = ctk.CTkButton(
            self,
            text=text,
            height=40,
            corner_radius=8,
            command=lambda: self.change_page(page),
            fg_color="transparent",
            hover_color=SURFACE_ALT,
            text_color=TEXT,
            border_width=0,
            anchor="w"
        )
        # Theme refresh must leave these navigation items flat in both modes.
        btn._is_nav_item = True
        btn.pack(fill="x", padx=15, pady=3)
        return btn

    def refresh_thought_threads(self):
        """Refresh the sidebar list so new threads appear without restarting."""
        try:
            threads = get_thought_threads(self.user_id, limit=8) if self.user_id is not None else []

            for row in self.thread_rows:
                try:
                    row.destroy()
                except Exception:
                    pass
            self.thread_rows.clear()

            if threads:
                self.thread_empty_label.pack_forget()
                for thread in threads:
                    thread_id, title, _created, _updated, _last_seen, count, _status = thread
                    row = ctk.CTkButton(
                        self.thread_section,
                        text=f"{title}  ·  {count}"[:38],
                        height=32,
                        corner_radius=7,
                        fg_color="transparent",
                        hover_color=SURFACE_ALT,
                        text_color=TEXT_BRIGHT,
                        anchor="w",
                        font=("Segoe UI", 10),
                        command=lambda tid=thread_id: self.open_thread(tid),
                    )
                    row._is_nav_item = True
                    row.pack(fill="x", pady=1)
                    self.thread_rows.append(row)
            else:
                self.thread_empty_label.pack(fill="x", pady=(0, 2))
        except Exception as e:
            print(f"⚠️ Thought thread sidebar refresh failed: {e}")

        try:
            self.thread_refresh_job = self.after(3000, self.refresh_thought_threads)
        except Exception:
            self.thread_refresh_job = None

    def open_thread(self, thread_id):
        self.change_page("thought_threads")
        try:
            page = self.master.master.pages.get("thought_threads")
            if page is not None and hasattr(page, "select_thread"):
                page.select_thread(thread_id)
        except Exception:
            pass

    def show_account_menu(self):
        if self.account_menu is not None:
            try:
                if self.account_menu.winfo_exists():
                    self.account_menu.destroy()
                    self.account_menu = None
                    return
            except Exception:
                self.account_menu = None

        self.account_menu = ctk.CTkToplevel(self)
        self.account_menu.title("Account")
        self.account_menu.geometry("220x90")
        self.account_menu.resizable(False, False)
        self.account_menu.transient(self.winfo_toplevel())
        self.account_menu.protocol("WM_DELETE_WINDOW", self.close_account_menu)

        logout_button = ctk.CTkButton(
            self.account_menu,
            text="↪  Log out",
            command=self.logout,
            height=40,
            corner_radius=8,
            fg_color=TEXT,
            hover_color=TEXT_MUTED,
            text_color=SURFACE
        )
        logout_button.pack(fill="x", padx=15, pady=15)

        self.account_menu.update_idletasks()
        x = self.account_button.winfo_rootx()
        y = self.account_button.winfo_rooty() - self.account_menu.winfo_height() - 8
        self.account_menu.geometry(f"220x90+{x}+{max(0, y)}")
        self.account_menu.grab_set()

    def close_account_menu(self):
        if self.account_menu is not None:
            try:
                self.account_menu.grab_release()
                self.account_menu.destroy()
            except Exception:
                pass
            self.account_menu = None

    def logout(self):
        self.close_account_menu()
        self.master.master.logout()
