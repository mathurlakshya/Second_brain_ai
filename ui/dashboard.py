import threading
import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    get_recording_preferences,
    set_recording_preferences,
)
from ui.floating_recorder import FloatingRecorder
from ui.chat_panel import ChatPanel
from ui.theme import (
    BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER,
    TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT,
    ACCENT, ACCENT_HOVER, SUCCESS
)


class Dashboard(ctk.CTkFrame):

    def __init__(self, parent, user_id, username):
        super().__init__(parent, fg_color=BG)

        self.user_id = user_id
        self.username = username

        # The OCR/embedding stack is loaded only if recording is enabled.
        self.recorder = None
        self._recorder_starting = False

        self.floating = None
        self.recording_session = False
        self.recorder_thread = None

        self.build_ui()

    def build_ui(self):
        # ---------- HEADER ----------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(30, 8))

        title = ctk.CTkLabel(
            header,
            text="👋 Welcome back",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Your digital memory is ready.",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=42, pady=(12, 28))

        self.left_panel = ctk.CTkScrollableFrame(
            content,
            width=300,
            fg_color=SURFACE,
            corner_radius=0,
            scrollbar_button_color=TEXT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        self.left_panel.pack(
            side="left",
            fill="y",
            padx=(0, 42)
        )

        self.right_panel = ctk.CTkFrame(
            content,
            fg_color="transparent",
            corner_radius=0
        )
        self.right_panel.pack(
            side="left",
            fill="both",
            expand=True
        )

        section = ctk.CTkLabel(
            self.left_panel,
            text="MEMORY",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT
        )
        section.pack(anchor="w", padx=2, pady=(5, 10))

        self.create_stat_row("Memory", "Idle")
        self.create_stat_row("Screens", "0")
        self.create_stat_row("AI", "0")
        self.create_stat_row("Runtime", "00:00")

        ctk.CTkFrame(
            self.left_panel,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", pady=(20, 18))

        self.start_btn = ctk.CTkButton(
            self.left_panel,
            text="▶  Start Memory",
            height=40,
            corner_radius=10,
            command=self.toggle_memory,
            fg_color=TEXT,
            hover_color=TEXT_MUTED,
            border_width=1,
            border_color=TEXT,
            text_color=SURFACE
        )
        self.start_btn.pack(fill="x", pady=(0, 20))

        status_title = ctk.CTkLabel(
            self.left_panel,
            text="LIVE STATUS",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT
        )
        status_title.pack(anchor="w", padx=2, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="🔴 Idle",
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT
        )
        self.status_label.pack(anchor="w", padx=2, pady=(0, 8))

        self.current_app = ctk.CTkLabel(
            self.left_panel,
            text="Current App : -",
            font=("Segoe UI", 12),
            text_color=TEXT,
            wraplength=280,
            justify="left"
        )
        self.current_app.pack(anchor="w", padx=2, pady=2)

        self.current_window = ctk.CTkLabel(
            self.left_panel,
            text="Current Window : -",
            font=("Segoe UI", 12),
            text_color=TEXT,
            wraplength=280,
            justify="left"
        )
        self.current_window.pack(anchor="w", padx=2, pady=2)

        self.last_updated = ctk.CTkLabel(
            self.left_panel,
            text="Updated : -",
            font=("Segoe UI", 12),
            text_color=TEXT
        )
        self.last_updated.pack(anchor="w", padx=2, pady=2)

        ctk.CTkFrame(
            self.left_panel,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", pady=(22, 18))

        activity_title = ctk.CTkLabel(
            self.left_panel,
            text="RECENT ACTIVITY",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT
        )
        activity_title.pack(anchor="w", padx=2, pady=(0, 10))

        self.timeline = ctk.CTkTextbox(
            self.left_panel,
            height=230,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            text_color=TEXT,
            font=("Segoe UI", 11),
            wrap="word",
            scrollbar_button_color=TEXT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        self.timeline.pack(fill="x", padx=0, pady=0)
        self.timeline.insert("end", "Waiting for activity...")
        self.timeline.configure(state="disabled")

        jarvis_header = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )
        jarvis_header.pack(
            fill="x",
            pady=(8, 0)
        )

        icon = ctk.CTkLabel(
            jarvis_header,
            text="✦",
            font=("Segoe UI", 31, "bold"),
            text_color=ACCENT
        )
        icon.pack(side="left", padx=(0, 12))

        heading_group = ctk.CTkFrame(
            jarvis_header,
            fg_color="transparent"
        )
        heading_group.pack(side="left")

        jarvis_title = ctk.CTkLabel(
            heading_group,
            text="JARVIS",
            font=("Segoe UI", 25, "bold"),
            text_color=TEXT
        )
        jarvis_title.pack(anchor="w")

        jarvis_sub = ctk.CTkLabel(
            heading_group,
            text="Your memory-aware desktop intelligence",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED
        )
        jarvis_sub.pack(anchor="w", pady=(1, 0))

        ctk.CTkFrame(
            self.right_panel,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", pady=(20, 12))

        self.chat = ChatPanel(self.right_panel, user_id=self.user_id)
        self.chat.pack(fill="both", expand=True)

    def create_stat_row(self, title, value):
        row = ctk.CTkFrame(
            self.left_panel,
            fg_color="transparent",
            height=30
        )
        row.pack(fill="x", pady=3)

        label = ctk.CTkLabel(
            row,
            text=title,
            font=("Segoe UI", 12),
            text_color=TEXT
        )
        label.pack(side="left")

        value_label = ctk.CTkLabel(
            row,
            text=value,
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT
        )
        value_label.pack(side="right")

    def start_recording_on_launch(self):
        """Start only when consent and the separate auto-start option are enabled."""
        try:
            preferences = get_recording_preferences(self.user_id)
            if (
                preferences["consent"]
                and preferences["auto_start"]
                and (self.recorder is None or not self.recorder.running)
                and not self._recorder_starting
            ):
                self.start_memory_recording()
        except Exception as e:
            print(f"Automatic recording start failed: {e}")

    def shutdown(self):
        """Stop background recording and remove the floating window."""
        self.recording_session = False
        self._recorder_starting = False
        try:
            if self.recorder is not None and self.recorder.running:
                self.recorder.stop()
        except Exception as e:
            print(f"Recorder shutdown failed: {e}")
        try:
            self.destroy_floating_recorder()
        except Exception as e:
            print(f"Floating recorder shutdown failed: {e}")

    def toggle_memory(self):
        if self._recorder_starting:
            return
        if self.recorder is not None and self.recorder.running:
            self.stop_memory_recording()
        else:
            self.start_memory_recording()

    def start_memory_recording(self):
        # All entry points pass through this consent check before capture starts.
        preferences = get_recording_preferences(self.user_id)
        if not preferences["consent"]:
            accepted = messagebox.askyesno(
                "Enable Second Brain memory recording?",
                "Second Brain AI can monitor the active application and window "
                "title, and read visible on-screen text using Windows accessibility "
                "features and OCR. This text is stored locally to build searchable "
                "memories. Screenshots are not saved by default. If you choose "
                "optional cloud AI features, the prompt and relevant context you "
                "submit may be sent to the configured AI provider.\n\n"
                "Recording stays off unless you enable it. You can stop it at any "
                "time and change these choices in Settings. Enable recording now?",
                icon="warning",
                parent=self.winfo_toplevel(),
            )
            if not accepted:
                return False
            set_recording_preferences(
                self.user_id,
                consent=True,
                auto_start=preferences["auto_start"],
            )

        if self._recorder_starting:
            return True
        if self.recorder is not None and self.recorder.running:
            self.sync_floating_state(True)
            return True

        self.recording_session = True
        self._recorder_starting = True
        self.start_btn.configure(text="⏳  Starting Memory...")
        self.status_label.configure(text="Preparing memory engine...", text_color=TEXT_MUTED)

        # Importing PyTorch, OCR and embedding libraries can be expensive. Do it
        # off the UI thread so the window remains responsive during first start.
        threading.Thread(target=self._load_and_start_recorder, daemon=True).start()
        return True

    def _load_and_start_recorder(self):
        try:
            from memory.recorder import MemoryRecorder

            if not self.recording_session:
                self.after(0, self._cancel_recorder_start)
                return

            recorder = MemoryRecorder(
                user_id=self.user_id,
                callback=self.on_memory_saved,
            )
            self.recorder = recorder

            if not self.recording_session:
                self.after(0, self._cancel_recorder_start)
                return

            self.recorder_thread = threading.Thread(
                target=recorder.start,
                daemon=True,
            )
            self.recorder_thread.start()
            self.after(0, self._finish_recorder_start)
        except Exception as exc:
            print(f"Memory engine failed to load: {type(exc).__name__}: {exc}")
            try:
                self.after(0, self._recorder_start_failed, str(exc))
            except Exception:
                pass

    def _finish_recorder_start(self):
        self._recorder_starting = False
        if not self.recording_session or self.recorder is None:
            return
        self.create_floating_recorder()
        self.start_btn.configure(text="🟢  Recording...")
        self.status_label.configure(text="🟢 Recording", text_color=SUCCESS)
        self.sync_floating_state(self.recorder is not None and self.recorder.running)
        print("Memory recorder started")

    def _cancel_recorder_start(self):
        self._recorder_starting = False
        if self.recorder is not None and self.recorder.running:
            self.recorder.stop()
        self.start_btn.configure(text="▶  Start Memory")
        self.status_label.configure(text="🔴 Idle", text_color=TEXT)

    def _recorder_start_failed(self, error):
        self._recorder_starting = False
        self.recording_session = False
        self.start_btn.configure(text="▶  Start Memory")
        self.status_label.configure(text="🔴 Idle", text_color=TEXT)
        messagebox.showerror(
            "Memory engine unavailable",
            "Second Brain AI could not initialize its recording engine. "
            "Please restart the app and try again.\n\n" + error,
            parent=self.winfo_toplevel(),
        )

    def stop_memory_recording(self):
        print("Stopping memory recording")
        self.recording_session = False
        self._recorder_starting = False

        if self.recorder is None or not self.recorder.running:
            self.sync_floating_state(False)
            self.start_btn.configure(text="▶  Start Memory")
            self.status_label.configure(text="🔴 Idle", text_color=TEXT)
            return True

        self.recorder.stop()
        self.sync_floating_state(False)
        self.start_btn.configure(text="▶  Start Memory")
        self.status_label.configure(text="🔴 Idle", text_color=TEXT)
        self.current_app.configure(text="Current App : -")
        self.current_window.configure(text="Current Window : -")
        self.last_updated.configure(text="Updated : -")
        print("Recording stopped")
        return True

    def create_floating_recorder(self):
        if self.floating is not None:
            try:
                if self.floating.winfo_exists():
                    self.sync_floating_state(self.recorder is not None and self.recorder.running)
                    return
            except Exception:
                pass

        try:
            root = self.winfo_toplevel()

            print("🧠 Creating FloatingRecorder...")

            self.floating = FloatingRecorder(
                root,
                start_callback=self.start_memory_recording,
                stop_callback=self.stop_memory_recording
            )

            self.floating.deiconify()
            self.floating.lift()
            self.floating.attributes("-topmost", True)

            self.floating.bind("<Destroy>", self.on_floating_destroyed)

            self.sync_floating_state(self.recorder is not None and self.recorder.running)

            print("✅ FloatingRecorder CREATED")

        except Exception as e:
            self.floating = None
            print(f"❌ Could not create FloatingRecorder: {e}")

    def sync_floating_state(self, recording):
        floating = self.floating

        if floating is None:
            return

        try:
            if floating.winfo_exists():
                floating.set_recording_state(recording)
        except Exception as e:
            print(f"⚠️ Could not sync FloatingRecorder state: {e}")

    def destroy_floating_recorder(self):
        floating = self.floating
        self.floating = None

        if floating is None:
            return

        try:
            if floating.winfo_exists():
                print("🗑️ Destroying FloatingRecorder...")
                floating.destroy()
        except Exception as e:
            print(f"⚠️ FloatingRecorder destroy error: {e}")

    def on_floating_destroyed(self, event=None):
        try:
            if self.floating is not None and not self.floating.winfo_exists():
                self.floating = None
                print("🧹 FloatingRecorder reference cleared")
        except Exception:
            self.floating = None

    def update_status(self, app, title, timestamp):
        self.after(
            0,
            lambda: self.status_label.configure(text="🟢 Recording")
        )

        self.after(
            0,
            lambda: self.current_app.configure(
                text=f"Current App : {app}"
            )
        )

        self.after(
            0,
            lambda: self.current_window.configure(
                text=f"Current Window : {title}"
            )
        )

        self.after(
            0,
            lambda: self.last_updated.configure(
                text=f"Updated : {timestamp}"
            )
        )

        self.after(0, self.add_activity, app, title, timestamp)

        if self.floating:
            self.after(
                0,
                lambda: (
                    self.floating.update_app(app, title)
                    if self.floating is not None
                    else None
                )
            )

    def add_activity(self, app, title, timestamp):
        self.timeline.configure(state="normal")
        self.timeline.insert(
            "1.0",
            f"[{timestamp[-8:]}]\n"
            f"{app}\n"
            f"{title}\n\n"
        )
        self.timeline.configure(state="disabled")

    def update_memory_status(self, status):
        self.status_label.configure(text=status)

    def clear_timeline(self):
        self.timeline.configure(state="normal")
        self.timeline.delete("1.0", "end")
        self.timeline.insert("end", "Waiting for activity...")
        self.timeline.configure(state="disabled")

    def add_system_message(self, message):
        self.timeline.configure(state="normal")
        self.timeline.insert("1.0", f"🧠 {message}\n\n")
        self.timeline.configure(state="disabled")

    def refresh_statistics(self):
        pass

    def refresh_dashboard(self):
        pass

    def load_today_summary(self):
        pass

    def update_runtime(self):
        pass

    def on_memory_saved(self, app, title, timestamp):
        print(f"📢 New memory saved: {app} | {title}")

        try:
            self.after(
                0,
                self.update_status,
                app,
                title,
                timestamp
            )
        except Exception as e:
            print(f"⚠️ Dashboard update error: {e}")
