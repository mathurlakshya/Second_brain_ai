import customtkinter as ctk
from tkinter import filedialog, messagebox

from database.database import (
    delete_user_memories,
    export_user_memories,
    get_memory_counts,
    get_recording_preferences,
    set_recording_preferences,
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
        # A scrollable settings surface keeps About and other lower sections
        # accessible on shorter windows and high-DPI displays.
        content = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        content.pack(fill="both", expand=True)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))
        ctk.CTkLabel(header, text="Settings", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Control privacy, appearance, and your local memory data.",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkFrame(content, height=1, fg_color=BORDER).pack(fill="x", padx=42, pady=(20, 14))

        privacy = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=14)
        privacy.pack(fill="x", padx=42, pady=(0, 14))
        ctk.CTkLabel(privacy, text="PRIVACY", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )

        recording_preferences = get_recording_preferences(self.user_id)
        self.recording_switch = ctk.CTkSwitch(
            privacy,
            text="Allow local memory recording",
            command=self.toggle_recording_consent,
            text_color=TEXT_BRIGHT,
            progress_color=ACCENT,
        )
        self.recording_switch.pack(anchor="w", padx=22, pady=(0, 8))
        (self.recording_switch.select() if recording_preferences["consent"] else self.recording_switch.deselect())

        self.auto_start_switch = ctk.CTkSwitch(
            privacy,
            text="Automatically start recording when the app opens",
            command=self.toggle_auto_start_recording,
            text_color=TEXT_BRIGHT,
            progress_color=ACCENT,
        )
        self.auto_start_switch.pack(anchor="w", padx=22, pady=(0, 8))
        (self.auto_start_switch.select() if recording_preferences["auto_start"] else self.auto_start_switch.deselect())
        if not recording_preferences["consent"]:
            self.auto_start_switch.configure(state="disabled")

        ctk.CTkLabel(
            privacy,
            text="Recording reads active app/window titles and visible screen text for searchable memories. "
                 "Memory text and embeddings stay on this device by default; screenshots are not saved "
                 "unless you enable the separate option below. Optional cloud AI features may send the "
                 "prompt and relevant context you submit to the configured AI provider. Recording is "
                 "off by default and can be stopped at any time.",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 14))

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

        data = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=14)
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

        appearance_panel = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=14)
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

        about_panel = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=14)
        about_panel.pack(fill="x", expand=False, padx=42, pady=(0, 30))
        ctk.CTkLabel(about_panel, text="ABOUT SECOND BRAIN", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM).pack(
            anchor="w", padx=22, pady=(20, 8)
        )
        about = ctk.CTkTextbox(
            about_panel,
            height=180,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_SOFT,
            font=("Segoe UI", 12),
            wrap="word",
        )
        about.pack(fill="x", expand=False, padx=22, pady=(0, 20))
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

    def toggle_recording_consent(self):
        enabled = bool(self.recording_switch.get())
        preferences = get_recording_preferences(self.user_id)

        if enabled:
            accepted = messagebox.askyesno(
                "Allow local memory recording?",
                "When enabled, Second Brain AI reads active application/window titles "
                "and visible on-screen text to create searchable memories stored locally. "
                "Screenshots are off by default. Optional cloud AI actions may send the "
                "prompt and relevant context you submit to the configured AI provider. "
                "You can stop recording at any time.\n\nAllow recording?",
                icon="warning",
                parent=self.winfo_toplevel(),
            )
            if not accepted:
                self.recording_switch.deselect()
                return
            set_recording_preferences(
                self.user_id,
                consent=True,
                auto_start=preferences["auto_start"],
            )
            self.auto_start_switch.configure(state="normal")
        else:
            set_recording_preferences(self.user_id, consent=False, auto_start=False)
            self.auto_start_switch.deselect()
            self.auto_start_switch.configure(state="disabled")
            # Revoking consent stops any active recorder immediately.
            root = self.winfo_toplevel()
            app_window = getattr(root, "app_window", None)
            dashboard = getattr(app_window, "pages", {}).get("dashboard") if app_window else None
            if dashboard is not None:
                try:
                    dashboard.stop_memory_recording()
                except Exception:
                    pass

    def toggle_auto_start_recording(self):
        enabled = bool(self.auto_start_switch.get())
        preferences = get_recording_preferences(self.user_id)
        if enabled and not preferences["consent"]:
            self.auto_start_switch.deselect()
            messagebox.showinfo(
                "Recording consent required",
                "Enable local memory recording first. Automatic recording cannot be enabled without your consent.",
                parent=self.winfo_toplevel(),
            )
            return
        set_recording_preferences(
            self.user_id,
            consent=preferences["consent"],
            auto_start=enabled,
        )

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
