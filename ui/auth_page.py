import customtkinter as ctk

from database.auth import create_user, login_user


class AuthPage(ctk.CTkFrame):

    def __init__(self, parent, on_login):
        super().__init__(
            parent,
            fg_color="#0B1220"
        )

        self.on_login = on_login
        
        from session import save_session

        save_session(user)

        self.build_ui()

    def build_ui(self):

        container = ctk.CTkFrame(
            self,
            width=450,
            height=500,
            corner_radius=20,
            fg_color="#111827"
        )

        container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title = ctk.CTkLabel(
            container,
            text="🧠 Second Brain AI",
            font=("Segoe UI", 28, "bold"),
            text_color="#F5FAFF"
        )

        title.pack(
            pady=(35, 5)
        )

        subtitle = ctk.CTkLabel(
            container,
            text="Your personal digital memory",
            font=("Segoe UI", 14),
            text_color="#A9C7E8"
        )

        subtitle.pack(
            pady=(0, 25)
        )

        self.username_entry = ctk.CTkEntry(
            container,
            width=330,
            height=40,
            placeholder_text="Username"
        )

        self.username_entry.pack(
            pady=8
        )

        self.email_entry = ctk.CTkEntry(
            container,
            width=330,
            height=40,
            placeholder_text="Email"
        )

        self.email_entry.pack(
            pady=8
        )

        self.password_entry = ctk.CTkEntry(
            container,
            width=330,
            height=40,
            placeholder_text="Password",
            show="*"
        )

        self.password_entry.pack(
            pady=8
        )

        self.message_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF6B6B"
        )

        self.message_label.pack(
            pady=8
        )

        self.signup_btn = ctk.CTkButton(
            container,
            width=330,
            height=42,
            text="📝 Create Account",
            command=self.signup
        )

        self.signup_btn.pack(
            pady=8
        )

        self.login_btn = ctk.CTkButton(
            container,
            width=330,
            height=42,
            text="🔐 Login",
            command=self.login
        )

        self.login_btn.pack(
            pady=8
        )

    def signup(self):

        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not username or not email or not password:

            self.message_label.configure(
                text="Please fill in all fields."
            )

            return

        success, user_id = create_user(
            username,
            email,
            password
        )

        if not success:

            self.message_label.configure(
                text="An account with this email or username already exists."
            )

            return

        self.message_label.configure(
            text="Account created! You can now login.",
            text_color="#4ADE80"
        )

    def login(self):

        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:

            self.message_label.configure(
                text="Enter your email and password."
            )

            return

        user = login_user(
            email,
            password
        )

        if user is None:

            self.message_label.configure(
                text="Invalid email or password."
            )

            return

        self.on_login(user)