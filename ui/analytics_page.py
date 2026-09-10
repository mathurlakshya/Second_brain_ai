import customtkinter as ctk
import sqlite3

from ui.theme import BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, ACCENT


class AnalyticsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.build_ui()
        self.load_data()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="Productivity Analytics", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="A lightweight overview of your recorded digital activity.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 0))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=42, pady=(22, 18))
        stats.grid_columnconfigure((0, 1, 2), weight=1)

        self.memories = self.create_card(stats, "MEMORIES", 0, 0)
        self.apps = self.create_card(stats, "APPS USED", 0, 1)
        self.latest = self.create_card(stats, "LATEST ACTIVITY", "-", 0, 2)

        ctk.CTkButton(self, text="↻  Refresh Analytics", command=self.load_data, width=150, height=38, corner_radius=10, fg_color=SURFACE_ALT, hover_color="#172536", border_width=1, border_color=BORDER_HOVER, text_color=TEXT_BRIGHT).pack(anchor="e", padx=42, pady=(0, 12))
        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(0, 12))

        panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        panel.pack(fill="both", expand=True, padx=42, pady=(0, 30))
        self.box = ctk.CTkTextbox(panel, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Segoe UI", 13), wrap="word")
        self.box.pack(fill="both", expand=True, padx=22, pady=20)

    def create_card(self, parent, title, row, column, value=0):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=14, height=110)
        card.grid(row=row, column=column, padx=(0 if column == 0 else 8, 8 if column < 2 else 0), sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(17, 2))
        label = ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 24, "bold"), text_color=TEXT_BRIGHT)
        label.pack(anchor="w", padx=18)
        return label

    def load_data(self):
        try:
            conn = sqlite3.connect("second_brain.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT app_name) FROM memories")
            apps = cursor.fetchone()[0]
            cursor.execute("SELECT timestamp FROM memories ORDER BY id DESC LIMIT 1")
            latest = cursor.fetchone()
            conn.close()
        except sqlite3.Error as e:
            self.box.delete("1.0", "end")
            self.box.insert("end", f"Could not load analytics.\n\n{e}")
            return

        self.memories.configure(text=str(total))
        self.apps.configure(text=str(apps))
        self.latest.configure(text=latest[0][-8:] if latest else "-")
        self.box.delete("1.0", "end")
        self.box.insert("end", "TODAY'S SUMMARY\n\n")
        self.box.insert("end", f"Total Memories\n{total}\n\n")
        self.box.insert("end", f"Applications Used\n{apps}\n\n")
        self.box.insert("end", f"Latest Activity\n{latest[0] if latest else 'None'}\n")
