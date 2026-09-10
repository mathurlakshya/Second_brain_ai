import customtkinter as ctk

from ui.theme import BG, SURFACE, BORDER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM


class JournalPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="AI Daily Journal", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="A calm space for your daily reflection and remembered activity.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 0))
        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(20, 14))

        panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        panel.pack(fill="both", expand=True, padx=42, pady=(0, 30))
        ctk.CTkLabel(panel, text="TODAY", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=22, pady=(20, 8))
        self.journal_box = ctk.CTkTextbox(panel, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Segoe UI", 13), wrap="word")
        self.journal_box.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self.journal_box.insert("end", "Your AI-generated daily journal will appear here.\n\nThis page is ready to be connected to your memory summaries.")
