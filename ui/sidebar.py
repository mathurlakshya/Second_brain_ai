import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, change_page,username):
        super().__init__(
            parent,
            width=230,
            fg_color="#161B22",
            corner_radius=0
        )
        self.username = username 
        print('sidebar username: ',self.username)
        

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

        self.bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.bottom_frame.pack(
            side="bottom",
            fill="x",
            pady=20
        )

        self.account_button = ctk.CTkButton(
            self.bottom_frame,
            text=f"👤 {self.username} ▼",
            command=self.show_account_menu
        )

        self.account_button.pack(fill="x", padx=15)

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

    def show_account_menu(self):

        # If menu already exists, close it
        if hasattr(self, "account_menu") and self.account_menu.winfo_exists():
            self.account_menu.destroy()
            return

        self.account_menu = ctk.CTkToplevel(self)

        self.account_menu.title("Account")
        self.account_menu.geometry("180x70")
        self.account_menu.resizable(False, False)

        # Keep it above the main application
        self.account_menu.transient(self.winfo_toplevel())
        self.account_menu.grab_set()

        logout_button = ctk.CTkButton(
            self.account_menu,
            text="Logout",
            command=self.logout,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )

        logout_button.pack(
            fill="x",
            padx=15,
            pady=15
        )   

    def logout(self):

        if hasattr(self, "account_menu") and self.account_menu.winfo_exists():
            self.account_menu.destroy()

        self.master.master.logout()