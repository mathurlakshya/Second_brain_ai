import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, change_page):
        super().__init__(
            parent,
            width=230,
            fg_color="#161B22",
            corner_radius=0
        )

        self.change_page = change_page

        self.grid_propagate(False)

        title = ctk.CTkLabel(
            self,
            text="🧠 Second Brain",
            font=("Segoe UI", 24, "bold")
        )

        title.pack(pady=(30, 25))

        self.create_button("🏠 Dashboard", "dashboard")
        self.create_button("🧠 Memory", "memory")
        self.create_button("👁 Live Context", "live_context")
        self.create_button("🔍 Search", "search")
        self.create_button("📜 Analytics", "analytics")
        self.create_button("⚙️ Settings", "settings")

        spacer = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        spacer.pack(expand=True, fill="both")

        version = ctk.CTkLabel(
            self,
            text="Second Brain AI\nCompetition Edition",
            justify="center",
            text_color="gray"
        )

        version.pack(pady=20)

    def create_button(self, text, page):

        btn = ctk.CTkButton(
            self,
            text=text,
            height=45,
            corner_radius=10,
            command=lambda: self.change_page(page)
        )

        btn.pack(
            fill="x",
            padx=15,
            pady=6
        )