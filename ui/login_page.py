import customtkinter as ctk
from database.users import login_user


class LoginPage(ctk.CTkFrame):

    def __init__(self, parent, on_login, on_signup):
        super().__init__(parent)

        self.on_login = on_login
        self.on_signup = on_signup

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="🤖 Second Brain AI",
            font=("Segoe UI", 32, "bold")
        )
        title.pack(pady=(80, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Welcome back. Sign in to access your memories.",
            font=("Segoe UI", 15)
        )
        subtitle.pack(pady=(0, 30))

        self.email_entry = ctk.CTkEntry(
            self,
            width=350,
            height=45,
            placeholder_text="Email"
        )
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self,
            width=350,
            height=45,
            placeholder_text="Password",
            show="*"
        )
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(
            self,
            text="🔐 Login",
            width=350,
            height=45,
            command=self.login
        )
        self.login_button.pack(pady=(20, 10))

        signup_button = ctk.CTkButton(
            self,
            text="Create an account",
            width=350,
            height=40,
            fg_color="transparent",
            border_width=1,
            command=self.on_signup
        )
        signup_button.pack(pady=10)

        self.message = ctk.CTkLabel(
            self,
            text=""
        )
        self.message.pack(pady=10)

    def login(self):

        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            self.message.configure(
                text="⚠️ Please enter your email and password."
            )
            return

        user = login_user(email, password)

        if user:
            self.message.configure(
                text="✅ Login successful!"
            )

            self.on_login(user)

        else:
            self.message.configure(
                text="❌ Invalid email or password."
            )