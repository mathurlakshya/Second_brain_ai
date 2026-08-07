import customtkinter as ctk
from ui.app_window import AppWindow
from database.database import create_database

def main():

    create_database()   # <-- ADD THIS

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()