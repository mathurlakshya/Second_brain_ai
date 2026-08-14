import customtkinter as ctk

from database.database import create_database
from ui.auth_page import AuthPage
from ui.app_window import AppWindow


class Application(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Second Brain AI")

        self.geometry("1366x768")

        self.minsize(1200, 700)

        self.configure(
            fg_color="#05080F"
        )

        create_database()

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

        self.auth_page.destroy()

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

            from session import clear_session

            clear_session()

            self.app_window.destroy()

            self.show_login()

if __name__ == "__main__":

    app = Application()

    app.mainloop()

from session import load_session

user = load_session()

if user:

    self.login_success(user)

else:

    self.show_login()    