import customtkinter as ctk
from database.database import (
    get_user_setting,
    set_user_setting
)

class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, user_id):

        super().__init__(
            parent,
            fg_color="#111827"
        )

        self.user_id = user_id
        
        save_screenshots = get_user_setting(self.user_id)
        self.screenshot_switch = ctk.CTkSwitch(
                self,
                text="Keep screenshots for visual recall",
                command=self.toggle_screenshot_setting
            )

        self.screenshot_switch.pack(
            padx=20,
            pady=20
        )

        if save_screenshots:
            self.screenshot_switch.select()
        else:
            self.screenshot_switch.deselect()

        title = ctk.CTkLabel(
            self,
            text="⚙ Settings",
            font=("Segoe UI", 28, "bold"),
            text_color="#F2F6FF"
        )
        title.pack(pady=(25, 15))

        ctk.CTkLabel(
            self,
            text="Appearance Mode"
        ).pack(anchor="w", padx=30)

        appearance = ctk.CTkOptionMenu(
            self,
            values=["Dark", "Light"],
            command=self.change_mode
        )

        appearance.set("Dark")
        appearance.pack(
            padx=30,
            pady=(5, 20),
            anchor="w"
        )

        ctk.CTkLabel(
            self,
            text="About"
        ).pack(anchor="w", padx=30)

        about = ctk.CTkTextbox(
            self,
            height=220
        )

        about.pack(
            fill="x",
            padx=30,
            pady=15
        )

        about.insert(
            "end",
            """Second Brain AI

Version 1.0

JARVIS is an intelligent desktop assistant designed to remember, understand, and organize your digital activities. 
It continuously captures your workflow, recognizes on-screen content, and builds a searchable memory of your work, allowing you to retrieve past information using simple natural language. 
Whether you're coding, researching, studying, or managing documents, JARVIS helps you instantly recall what you've seen, learned, or worked on—so you can focus on creating instead of remembering. 
Built with privacy and productivity at its core, JARVIS transforms your computer into a smart, context-aware workspace that evolves with you.
"""
        )

        about.configure(state="disabled")


    def change_mode(self, mode):

        ctk.set_appearance_mode(mode)

    def toggle_screenshot_setting(self):

        enabled = self.screenshot_switch.get()

        set_user_setting(
            self.user_id,
            bool(enabled)
        )

        if enabled:
            print("📸 Screenshot storage enabled")
        else:
            print("🔒 Screenshot storage disabled")    