import customtkinter as ctk

class JournalPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        title = ctk.CTkLabel(
            self,
            text="📅 AI Daily Journal",
            font=("Segoe UI",26,"bold")
        )

        title.pack(pady=30)