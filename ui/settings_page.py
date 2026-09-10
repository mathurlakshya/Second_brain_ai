import customtkinter as ctk
from database.database import get_user_setting, set_user_setting
from ui.theme import BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, ACCENT, ACCENT_HOVER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, refresh_theme


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color=BG)
        self.user_id = user_id
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="Settings", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Control how Second Brain behaves and how your memories are stored.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(20, 14))

        panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        panel.pack(fill="x", padx=42, pady=(0, 14))

        ctk.CTkLabel(panel, text="PRIVACY", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=22, pady=(20, 8))
        save_screenshots = get_user_setting(self.user_id)
        self.screenshot_switch = ctk.CTkSwitch(
            panel,
            text="Keep screenshots for visual recall",
            command=self.toggle_screenshot_setting,
            text_color=TEXT_BRIGHT,
            progress_color=ACCENT
        )
        self.screenshot_switch.pack(anchor="w", padx=22, pady=(0, 20))
        if save_screenshots:
            self.screenshot_switch.select()
        else:
            self.screenshot_switch.deselect()

        appearance_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        appearance_panel.pack(fill="x", padx=42, pady=(0, 14))
        ctk.CTkLabel(appearance_panel, text="APPEARANCE", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=22, pady=(20, 8))
        self.appearance = ctk.CTkOptionMenu(
            appearance_panel,
            values=["Dark", "Light"],
            command=self.change_mode,
            fg_color=SURFACE_ALT,
            button_color=SURFACE_ALT,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_BRIGHT,
            dropdown_fg_color=SURFACE_ALT,
            dropdown_hover_color=ACCENT_HOVER
        )
        self.appearance.set(ctk.get_appearance_mode())
        self.appearance.pack(anchor="w", padx=22, pady=(0, 20))

        about_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        about_panel.pack(fill="both", expand=True, padx=42, pady=(0, 30))
        ctk.CTkLabel(about_panel, text="ABOUT SECOND BRAIN", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=22, pady=(20, 8))
        about = ctk.CTkTextbox(about_panel, height=180, fg_color="transparent", border_width=0, text_color=TEXT_SOFT, font=("Segoe UI", 12), wrap="word")
        about.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        about.insert("end", "Second Brain AI\n\nVersion 1.0\n\nJARVIS is an intelligent desktop assistant designed to remember, understand, and organize your digital activities. It captures your workflow, understands on-screen content, and builds a searchable memory of your work so you can recall past information using natural language.")
        about.configure(state="disabled")

    def change_mode(self, mode):
        ctk.set_appearance_mode(mode)
        refresh_theme(self.winfo_toplevel())

    def toggle_screenshot_setting(self):
        enabled = self.screenshot_switch.get()
        set_user_setting(self.user_id, bool(enabled))
