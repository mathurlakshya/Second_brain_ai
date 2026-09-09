import threading
import customtkinter as ctk
from ui.floating_recorder import FloatingRecorder
from memory.recorder import MemoryRecorder
from ui.chat_panel import ChatPanel


class Dashboard(ctk.CTkFrame):

    def __init__(self, parent, user_id, username):
        super().__init__(parent, fg_color="#05080F")

        self.user_id = user_id
        self.username = username

        self.recorder = MemoryRecorder(
            user_id=self.user_id,
            callback=self.on_memory_saved
        )

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
            text=f"Welcome back, {self.username}",
            font=("Segoe UI", 30, "bold"),
            text_color="#F4F7FB"
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Your digital memory is ready.",
            font=("Segoe UI", 14),
            text_color="#7F91A8"
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        # ---------- MAIN CANVAS ----------
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=42, pady=(12, 28))

        # LEFT: lightweight information rail
        self.left_panel = ctk.CTkScrollableFrame(
            content,
            width=300,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#182332",
            scrollbar_button_hover_color="#26374B"
        )
        self.left_panel.pack(
            side="left",
            fill="y",
            padx=(0, 42)
        )

        # RIGHT: completely flat JARVIS workspace
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

        # ---------- LEFT RAIL ----------
        section = ctk.CTkLabel(
            self.left_panel,
            text="MEMORY",
            font=("Segoe UI", 11, "bold"),
            text_color="#5F738C"
        )
        section.pack(anchor="w", padx=2, pady=(5, 10))

        self.create_stat_row("Memory", "Idle")
        self.create_stat_row("Screens", "0")
        self.create_stat_row("AI", "0")
        self.create_stat_row("Runtime", "00:00")

        ctk.CTkFrame(
            self.left_panel,
            height=1,
            fg_color="#17212E"
        ).pack(fill="x", pady=(20, 18))

        self.start_btn = ctk.CTkButton(
            self.left_panel,
            text="▶  Start Memory",
            height=40,
            corner_radius=10,
            command=self.toggle_memory,
            fg_color="#101A27",
            hover_color="#172536",
            border_width=1,
            border_color="#243449",
            text_color="#DCE8F5"
        )
        self.start_btn.pack(fill="x", pady=(0, 20))

        status_title = ctk.CTkLabel(
            self.left_panel,
            text="LIVE STATUS",
            font=("Segoe UI", 11, "bold"),
            text_color="#5F738C"
        )
        status_title.pack(anchor="w", padx=2, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="🔴 Idle",
            font=("Segoe UI", 13, "bold"),
            text_color="#A9B7C7"
        )
        self.status_label.pack(anchor="w", padx=2, pady=(0, 8))

        self.current_app = ctk.CTkLabel(
            self.left_panel,
            text="Current App : -",
            font=("Segoe UI", 12),
            text_color="#7F91A8",
            wraplength=280,
            justify="left"
        )
        self.current_app.pack(anchor="w", padx=2, pady=2)

        self.current_window = ctk.CTkLabel(
            self.left_panel,
            text="Current Window : -",
            font=("Segoe UI", 12),
            text_color="#7F91A8",
            wraplength=280,
            justify="left"
        )
        self.current_window.pack(anchor="w", padx=2, pady=2)

        self.last_updated = ctk.CTkLabel(
            self.left_panel,
            text="Updated : -",
            font=("Segoe UI", 12),
            text_color="#7F91A8"
        )
        self.last_updated.pack(anchor="w", padx=2, pady=2)

        ctk.CTkFrame(
            self.left_panel,
            height=1,
            fg_color="#17212E"
        ).pack(fill="x", pady=(22, 18))

        activity_title = ctk.CTkLabel(
            self.left_panel,
            text="RECENT ACTIVITY",
            font=("Segoe UI", 11, "bold"),
            text_color="#5F738C"
        )
        activity_title.pack(anchor="w", padx=2, pady=(0, 10))

        self.timeline = ctk.CTkTextbox(
            self.left_panel,
            height=230,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            text_color="#8294A9",
            font=("Segoe UI", 11),
            wrap="word"
        )
        self.timeline.pack(fill="x", padx=0, pady=0)
        self.timeline.insert("end", "Waiting for activity...")
        self.timeline.configure(state="disabled")

        # ---------- JARVIS ----------
        jarvis_header = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )
        jarvis_header.pack(
            fill="x",
            pady=(8, 0)
        )

        # Floating-style icon
        icon = ctk.CTkLabel(
            jarvis_header,
            text="✦",
            font=("Segoe UI", 31, "bold"),
            text_color="#5BD7FF"
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
            text_color="#F4F7FB"
        )
        jarvis_title.pack(anchor="w")

        jarvis_sub = ctk.CTkLabel(
            heading_group,
            text="Your memory-aware desktop intelligence",
            font=("Segoe UI", 12),
            text_color="#71849A"
        )
        jarvis_sub.pack(anchor="w", pady=(1, 0))

        ctk.CTkFrame(
            self.right_panel,
            height=1,
            fg_color="#111B27"
        ).pack(fill="x", pady=(20, 12))

        self.chat = ChatPanel(self.right_panel)
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
            text_color="#71849A"
        )
        label.pack(side="left")

        value_label = ctk.CTkLabel(
            row,
            text=value,
            font=("Segoe UI", 12, "bold"),
            text_color="#C7D3E0"
        )
        value_label.pack(side="right")

    # ---------------------------------------------------
    # START / STOP MEMORY
    # ---------------------------------------------------

    def toggle_memory(self):
        if self.recorder.running:
            self.stop_memory_recording()
        else:
            self.start_memory_recording()

    def start_memory_recording(self):
        print("🟢 STARTING MEMORY RECORDING")

        if self.recorder.running:
            print("🟢 Memory recorder is already running")
            self.sync_floating_state(True)
            return True

        self.recording_session = True

        self.recorder = MemoryRecorder(
            user_id=self.user_id,
            callback=self.on_memory_saved
        )

        self.recorder_thread = threading.Thread(
            target=self.recorder.start,
            daemon=True
        )
        self.recorder_thread.start()

        self.create_floating_recorder()

        self.start_btn.configure(text="🟢  Recording...")
        self.status_label.configure(
            text="🟢 Recording",
            text_color="#6EE7A8"
        )

        self.sync_floating_state(True)

        print("🧠 Floating recorder started")
        return True

    def stop_memory_recording(self):
        print("🔴 STOPPING MEMORY RECORDING")

        if not self.recorder.running:
            print("🔴 Memory recorder is already stopped")
            self.recording_session = False
            self.sync_floating_state(False)
            self.start_btn.configure(text="▶  Start Memory")
            self.status_label.configure(
                text="🔴 Idle",
                text_color="#A9B7C7"
            )
            return True

        self.recording_session = False
        self.recorder.stop()

        self.sync_floating_state(False)

        self.start_btn.configure(text="▶  Start Memory")
        self.status_label.configure(
            text="🔴 Idle",
            text_color="#A9B7C7"
        )
        self.current_app.configure(text="Current App : -")
        self.current_window.configure(text="Current Window : -")
        self.last_updated.configure(text="Updated : -")

        print("🔴 Recording stopped")
        return True

    # ---------------------------------------------------
    # FLOATING RECORDER
    # ---------------------------------------------------

    def create_floating_recorder(self):
        if self.floating is not None:
            try:
                if self.floating.winfo_exists():
                    self.sync_floating_state(self.recorder.running)
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

            self.sync_floating_state(self.recorder.running)

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

    # ---------------------------------------------------
    # LIVE STATUS UPDATE
    # ---------------------------------------------------

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
            f"[{timestamp[-8:]}]\n{app}\n{title}\n\n"
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
