import customtkinter as ctk

from database.database import create_database
from ui.auth_page import AuthPage
from ui.app_window import AppWindow

from session import (
    save_session,
    load_session,
    validate_trusted_device,
    clear_session,
    clear_trusted_device
)


class Application(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Second Brain AI")

        self.geometry("1366x768")

        self.minsize(
            1200,
            700
        )

        self.configure(
            fg_color="#05080F"
        )

        # Make sure database/tables exist.
        create_database()

        # Trusted-device login lets the app reopen automatically after
        # Windows logs the user in, without requiring a daily sign-in.
        trusted_user = validate_trusted_device()

        if trusted_user:
            save_session(trusted_user)
            self.login_success(trusted_user)
        else:
            self.show_auth()

    def show_auth(self):

        self.auth_page = AuthPage(
            self,
            self.login_success
        )

        self.auth_page.pack(
            fill="both",
            expand=True
        )

    def login_success(self, user):

        # Remove AuthPage if it exists.
        if hasattr(self, "auth_page"):

            try:
                self.auth_page.destroy()
            except Exception:
                pass

        self.app_window = AppWindow(
            self,
            user_id=user["id"],
            username=user["username"]
        )

        self.app_window.pack(
            fill="both",
            expand=True
        )

        # Start recording automatically after login. This means the user
        # does not have to press "Start Memory" every day.
        self.after(
            500,
            self.app_window.start_recording_on_launch
        )

    def logout(self):

        # Stop recording before destroying the authenticated app window.
        if hasattr(self, "app_window"):

            try:
                self.app_window.shutdown()
            except Exception:
                pass

        clear_trusted_device()
        clear_session()

        if hasattr(self, "app_window"):

            try:
                self.app_window.destroy()
            except Exception:
                pass

        self.show_auth()


if __name__ == "__main__":

    ctk.set_appearance_mode(
        "Dark"
    )

    ctk.set_default_color_theme(
        "dark-blue"
    )

    app = Application()

    app.mainloop()
