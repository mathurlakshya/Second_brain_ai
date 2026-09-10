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
        self.nav_buttons = {}
        self.active_page = None

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

        # Keep the account control at the bottom-left of the sidebar.
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

        # Default active page matches AppWindow.show_page("dashboard")
        self.set_active("dashboard")

    def create_button(self, text, page):
        """
        Grok-style nav item:
        - Default: plain text, no box
        - Hover: rounded background appears
        - Active: soft persistent background
        Works in both light and dark appearance modes.
        """
        btn = ctk.CTkButton(
            self,
            text=text,
            height=40,
            corner_radius=10,
            command=lambda p=page: self._on_nav_click(p),
            fg_color="transparent",
            hover_color=("#E8E8E8", "#1A2433"),
            text_color=TEXT,
            border_width=0,
            anchor="w",
            font=("Segoe UI", 14)
        )
        # Mark so theme refresh does not force solid button colors on these.
        btn._is_nav_item = True
        btn.pack(
            fill="x",
            padx=12,
            pady=3
        )

        self.nav_buttons[page] = btn

    def _on_nav_click(self, page):
        self.set_active(page)
        self.change_page(page)

    def set_active(self, page):
        """Highlight the selected nav item; others stay as plain text."""
        self.active_page = page

        for name, btn in self.nav_buttons.items():
            if name == page:
                btn.configure(
                    fg_color=("#E8E8E8", "#1A2433"),
                    hover_color=("#E0E0E0", "#243449"),
                    text_color=TEXT,
                    font=("Segoe UI", 14, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=("#E8E8E8", "#1A2433"),
                    text_color=TEXT,
                    font=("Segoe UI", 14)
                )

    def show_account_menu(self):
        # Toggle the account dropdown.
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

        # Position the menu directly above the account button.
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
        # The parent Application.logout() clears the active session and
        # trusted-device token, destroys the app window, and shows AuthPage.
        self.close_account_menu()
        self.master.master.logout()
