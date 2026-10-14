import customtkinter as ctk

from database.database import create_database
from memory.thought_threads import ensure_thought_threads_schema
from ui.sidebar import Sidebar
from ui.theme import BG, SURFACE


class AppWindow(ctk.CTkFrame):
    """Authenticated shell that creates feature pages only when first opened."""

    PAGE_MODULES = {
        "dashboard": ("ui.dashboard", "Dashboard"),
        "memory": ("ui.memory_page", "MemoryPage"),
        "thought_threads": ("ui.thought_threads_page", "ThoughtThreadsPage"),
        "live_context": ("ui.live_context", "LiveContext"),
        "search": ("ui.search_page", "SearchPage"),
        "analytics": ("ui.analytics_page", "AnalyticsPage"),
        "settings": ("ui.settings_page", "SettingsPage"),
    }

    def __init__(self, parent, user_id, username):
        super().__init__(parent, fg_color=BG)
        self.parent = parent
        self.user_id = user_id
        self.username = username
        self.pages = {}

        create_database()
        ensure_thought_threads_schema()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page, username, user_id=self.user_id)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.container = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_page("dashboard")

    def _create_page(self, page_name):
        module_name, class_name = self.PAGE_MODULES[page_name]
        module = __import__(module_name, fromlist=[class_name])
        page_class = getattr(module, class_name)

        if page_name == "dashboard":
            page = page_class(self.container, self.user_id, self.username)
        elif page_name == "settings":
            page = page_class(self.container, user_id=self.user_id)
        elif page_name in ("memory", "thought_threads", "search", "analytics"):
            page = page_class(self.container, self.user_id)
        else:
            page = page_class(self.container)

        page.grid(row=0, column=0, sticky="nsew")
        self.pages[page_name] = page
        return page

    def show_page(self, page_name):
        if page_name not in self.PAGE_MODULES:
            return
        page = self.pages.get(page_name)
        if page is None:
            try:
                page = self._create_page(page_name)
            except Exception as exc:
                print(f"Could not open {page_name}: {type(exc).__name__}: {exc}")
                return
        if page_name == "settings" and hasattr(page, "refresh_recording_controls"):
            page.refresh_recording_controls()
        page.tkraise()

    def start_recording_on_launch(self):
        """Respect both consent and the separate auto-start preference."""
        dashboard = self.pages.get("dashboard")
        if dashboard is None:
            return False
        return dashboard.start_recording_on_launch()

    def shutdown(self):
        dashboard = self.pages.get("dashboard")
        if dashboard is not None:
            try:
                dashboard.shutdown()
            except Exception as exc:
                print(f"Recorder shutdown failed: {exc}")

    def logout(self):
        self.master.logout()
