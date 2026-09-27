import customtkinter as ctk
from tkinter import filedialog, messagebox

from database.database import (
    delete_user_memories,
    export_user_memories,
    get_memory_counts,
    get_user_setting,
    set_user_setting,
)
from ui.theme import (
    BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, ACCENT, ACCENT_HOVER,
    TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, refresh_theme,
)


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color=BG)
        self.user_id = user_id
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="Settings", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Control privacy, appearance, and your local memory data.",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(20, 14))

        privacy = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        privacy.pack(fill="x", padx=42, pady=(0, 14))
        ctk.CTkLabel(privacy, text="PRIVACY", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )

        save_screenshots = get_user_setting(self.user_id)
        self.screenshot_switch = ctk.CTkSwitch(
            privacy,
            text="Keep screenshots for visual recall",
            command=self.toggle_screenshot_setting,
            text_color=TEXT_BRIGHT,
            progress_color=ACCENT,
        )
        self.screenshot_switch.pack(anchor="w", padx=22, pady=(0, 8))
        (self.screenshot_switch.select() if save_screenshots else self.screenshot_switch.deselect())

        ctk.CTkLabel(
            privacy,
            text="Off by default. Screen text and embeddings remain local unless you explicitly use a cloud AI feature.",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 18))

        data = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        data.pack(fill="x", padx=42, pady=(0, 14))
        ctk.CTkLabel(data, text="YOUR DATA", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )

        self.data_status = ctk.CTkLabel(data, text="", font=("Segoe UI", 11), text_color=TEXT_MUTED)
        self.data_status.pack(anchor="w", padx=22, pady=(0, 10))

        actions = ctk.CTkFrame(data, fg_color="transparent")
        actions.pack(fill="x", padx=22, pady=(0, 20))

        ctk.CTkButton(
            actions,
            text="Export My Memories",
            command=self.export_memories,
            fg_color=SURFACE_ALT,
            hover_color=ACCENT_HOVER,
            border_width=1,
            border_color=BORDER_HOVER,
            text_color=TEXT_BRIGHT,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Delete My Memories",
            command=self.delete_memories,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color="#FFFFFF",
        ).pack(side="left")

        appearance_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        appearance_panel.pack(fill="x", padx=42, pady=(0, 14))
        ctk.CTkLabel(appearance_panel, text="APPEARANCE", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )
        self.appearance = ctk.CTkOptionMenu(
            appearance_panel,
            values=["Dark", "Light"],
            command=self.change_mode,
            fg_color=SURFACE_ALT,
            button_color=SURFACE_ALT,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_BRIGHT,
            dropdown_fg_color=SURFACE_ALT,
            dropdown_hover_color=ACCENT_HOVER,
        )
        self.appearance.set(ctk.get_appearance_mode())
        self.appearance.pack(anchor="w", padx=22, pady=(0, 20))

        about_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        about_panel.pack(fill="both", expand=True, padx=42, pady=(0, 30))
        ctk.CTkLabel(about_panel, text="ABOUT SECOND BRAIN", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )
        about = ctk.CTkTextbox(
            about_panel,
            height=150,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_SOFT,
            font=("Segoe UI", 12),
            wrap="word",
        )
        about.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        about.insert(
            "end",
            "Second Brain AI\n\n"
            "Version 1.0\n\n"
            "Your recordings, OCR text, embeddings, and memories are stored locally. "
            "Gemini is an optional cloud intelligence layer used only for explicit AI features. "
            "Use Export before deleting memories if you want a portable copy.",
        )
        about.configure(state="disabled")

        self.refresh_data_status()

    def refresh_data_status(self):
        memories, threads = get_memory_counts(self.user_id)
        self.data_status.configure(text=f"{memories} memories  •  {threads} thought threads")

    def change_mode(self, mode):
        ctk.set_appearance_mode(mode)
        refresh_theme(self.winfo_toplevel())

    def toggle_screenshot_setting(self):
        set_user_setting(self.user_id, bool(self.screenshot_switch.get()))

    def export_memories(self):
        path = filedialog.asksaveasfilename(
            title="Export Second Brain memories",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="second_brain_memories.json",
        )
        if not path:
            return
        try:
            export_user_memories(self.user_id, path)
            messagebox.showinfo("Export complete", "Your memory data was exported successfully.")
        except Exception as exc:
            messagebox.showerror("Export failed", "The memory export could not be completed.")

    def delete_memories(self):
        memories, _ = get_memory_counts(self.user_id)
        if memories == 0:
            messagebox.showinfo("Nothing to delete", "You do not have any recorded memories.")
            return

        confirmed = messagebox.askyesno(
            "Delete memories",
            "Delete all of your recorded memories and screenshots? This cannot be undone.",
            icon="warning",
        )
        if not confirmed:
            return

        try:
            delete_user_memories(self.user_id)
            self.refresh_data_status()
            messagebox.showinfo("Memories deleted", "Your recorded memory data was deleted.")
        except Exception:
            messagebox.showerror("Delete failed", "Your memory data could not be deleted completely.")
