import customtkinter as ctk

from ui.theme import (
    SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_BRIGHT
)


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, change_page, username):
        super().__init__(
            parent,
            width=230,
            fg_color=SURFACE,
            corner_radius=0
        )

        self.username = username
        self.change_page = change_page
        self.account_menu = None
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
        self.create_button("✦ Thought Threads", "thought_threads")
        self.create_button("👁 Live Context", "live_context")
        self.create_button("🔍 Search", "search")
        self.create_button("📜 Analytics", "analytics")
        self.create_button("⚙️ Settings", "settings")

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

    def create_button(self, text, page):
        btn = ctk.CTkButton(
            self,
            text=text,
            height=45,
            corner_radius=10,
            command=lambda: self.change_page(page),
            fg_color=TEXT,
            hover_color=TEXT_MUTED,
            text_color=SURFACE
        )
        btn.pack(fill="x", padx=15, pady=6)

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
