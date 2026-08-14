import customtkinter as ctk
from ui.live_context import LiveContext
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.memory_page import MemoryPage
from ui.search_page import SearchPage
from ui.settings_page import SettingsPage
from ui.analytics_page import AnalyticsPage
# (We'll create these pages next)
# from ui.live_context import LiveContext
# from ui.memory_page import MemoryPage
# from ui.timeline_page import TimelinePage
# from ui.search_page import SearchPage
# from ui.settings_page import SettingsPage


class AppWindow(ctk.CTkFrame):

    def __init__(self, parent, user_id, username):

        super().__init__(
            parent,
            fg_color="#05080F"
        )
        self.parent = parent
        self.user_id = user_id
        self.username = username

    

        self.configure(
            fg_color="#05080F"
        )

        # ---------------- Layout ---------------- #

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Main Content Area
        self.container = ctk.CTkFrame(
            self,
            fg_color="#0B1220",
            corner_radius=0
        )

        self.container.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # ---------------- Pages ---------------- #

        self.pages = {}

        self.pages["dashboard"] = Dashboard(
            self.container,
            self.user_id,
            self.username
        )

        self.pages["live_context"] = LiveContext(self.container)

        self.pages["memory"] = MemoryPage(self.container)

        self.pages["search"] = SearchPage(self.container)

        self.pages["settings"] = SettingsPage(
                self.container,
                user_id=self.user_id
            )

        self.pages["analytics"] = AnalyticsPage(self.container)

        # Uncomment these after we create them
        #
        # self.pages["live_context"] = LiveContext(self.container)
        # self.pages["memory"] = MemoryPage(self.container)
        # self.pages["timeline"] = TimelinePage(self.container)
        # self.pages["search"] = SearchPage(self.container)
        # self.pages["settings"] = SettingsPage(self.container)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    # ---------------- Navigation ---------------- #

    def show_page(self, page_name):

        page = self.pages.get(page_name)

        if page:
            page.tkraise()