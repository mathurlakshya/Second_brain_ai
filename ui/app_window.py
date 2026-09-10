import customtkinter as ctk

from database.database import create_database
from memory.thought_threads import ensure_thought_threads_schema
from ui.live_context import LiveContext
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.memory_page import MemoryPage
from ui.search_page import SearchPage
from ui.settings_page import SettingsPage
from ui.analytics_page import AnalyticsPage
from ui.thought_threads_page import ThoughtThreadsPage
from ui.theme import BG, SURFACE


class AppWindow(ctk.CTkFrame):

    def __init__(self, parent, user_id, username):
        super().__init__(parent, fg_color=BG)
        self.parent = parent
        self.user_id = user_id
        self.username = username

        create_database()
        ensure_thought_threads_schema()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page, username, user_id=self.user_id)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.container = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            corner_radius=0,
        )
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "dashboard": Dashboard(self.container, self.user_id, self.username),
            "memory": MemoryPage(self.container),
            "thought_threads": ThoughtThreadsPage(self.container, self.user_id),
            "live_context": LiveContext(self.container),
            "search": SearchPage(self.container, self.user_id),
            "analytics": AnalyticsPage(self.container),
            "settings": SettingsPage(self.container, user_id=self.user_id),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if page:
            page.tkraise()

    def logout(self):
        self.master.logout()
