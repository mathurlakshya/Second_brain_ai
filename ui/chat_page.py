import customtkinter as ctk
from ui.chat_panel import ChatPanel

class ChatPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        chat = ChatPanel(self)
        chat.pack(fill="both", expand=True, padx=20, pady=20)