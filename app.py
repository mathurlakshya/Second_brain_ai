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

        # ---------------------------------------------
        # CHECK TRUSTED DEVICE
        # ---------------------------------------------

        trusted_user = validate_trusted_device()

        if trusted_user:

            # We have a valid trusted device.
            save_session(trusted_user)

            self.login_success(
                trusted_user
            )

        else:

            # No valid trusted device.
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

    def logout(self):

        # Invalidate trusted device.
        clear_trusted_device()

        # Clear normal session.
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
