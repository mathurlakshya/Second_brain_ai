import threading
import customtkinter as ctk
from ui.floating_recorder import FloatingRecorder
from memory.recorder import MemoryRecorder
from ui.chat_panel import ChatPanel


class Dashboard(ctk.CTkFrame):

    def __init__(self, parent, user_id, username):
        super().__init__(parent, fg_color="#101826")

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
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header, text="Welcome Back 👋",
            font=("Segoe UI", 30, "bold"), text_color="white"
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header, text="Your Digital Memory is Ready",
            font=("Segoe UI", 15), text_color="#F2F6FF"
        )
        subtitle.pack(anchor="w")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        self.left_panel = ctk.CTkScrollableFrame(
            content, width=380, corner_radius=15, fg_color="#1E293B"
        )
        self.left_panel.pack(side="left", fill="y", padx=(0, 15))
        self.left_panel.configure(width=380, height=650)

        self.right_panel = ctk.CTkFrame(content, corner_radius=15)
        self.right_panel.pack(side="left", fill="both", expand=True)

        stats = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        stats.pack(fill="x", padx=15, pady=15)

        self.create_card(stats, "🧠 Memory", "Idle", 0)
        self.create_card(stats, "📸 Screens", "0", 1)
        self.create_card(stats, "💬 AI", "0", 2)
        self.create_card(stats, "⏱ Runtime", "00:00", 3)

        controls = ctk.CTkFrame(self.left_panel)
        controls.pack(fill="x", padx=15, pady=10)

        self.start_btn = ctk.CTkButton(
            controls,
            text="▶ Start Memory",
            height=42,
            command=self.toggle_memory,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )
        self.start_btn.pack(fill="x", padx=12, pady=(12, 8))

        status = ctk.CTkFrame(self.left_panel)
        status.pack(fill="x", padx=15, pady=10)

        status_title = ctk.CTkLabel(
            status, text="🟢 Live Status",
            font=("Segoe UI", 18, "bold"), text_color="#9DB1C7"
        )
        status_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.status_label = ctk.CTkLabel(status, text="🔴 Idle")
        self.status_label.pack(anchor="w", padx=15)

        self.current_app = ctk.CTkLabel(status, text="Current App : -")
        self.current_app.pack(anchor="w", padx=15)

        self.current_window = ctk.CTkLabel(status, text="Current Window : -")
        self.current_window.pack(anchor="w", padx=15)

        self.last_updated = ctk.CTkLabel(status, text="Updated : -")
        self.last_updated.pack(anchor="w", padx=15, pady=(0, 12))

        timeline = ctk.CTkFrame(self.left_panel)
        timeline.pack(fill="x", padx=15, pady=(10, 10))
        timeline.configure(height=250)

        lbl = ctk.CTkLabel(
            timeline, text="📜 Recent Activity",
            font=("Segoe UI", 18, "bold")
        )
        lbl.pack(anchor="w", padx=15, pady=(12, 8))

        self.timeline = ctk.CTkTextbox(timeline, height=170)
        self.timeline.pack(fill="x", padx=10, pady=10)
        self.timeline.insert("end", "Waiting for activity...")
        self.timeline.configure(state="disabled")

        jarvis_title = ctk.CTkLabel(
            self.right_panel, text="🤖 JARVIS ",
            font=("Segoe UI", 28, "bold")
        )
        jarvis_title.pack(anchor="w", padx=20, pady=(20, 5))

        jarvis_sub = ctk.CTkLabel(
            self.right_panel,
            text="Ask anything about your memories, current work or computer activity.",
            font=("Segoe UI", 15)
        )
        jarvis_sub.pack(anchor="w", padx=20, pady=(0, 15))

        self.chat = ChatPanel(self.right_panel)
        self.chat.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, width=155, height=90, corner_radius=12)
        card.grid(row=column // 2, column=column % 2, padx=8, pady=8)
        card.grid_propagate(False)

        label = ctk.CTkLabel(
            card, text=title, font=("Segoe UI", 14, "bold")
        )
        label.pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card, text=value, font=("Segoe UI", 20)
        )
        value_label.pack()

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

        # Prevent duplicate recorder threads.
        if self.recorder.running:
            print("🟢 Memory recorder is already running")
            self.sync_floating_state(True)
            return True

        if self.recorder_thread is not None and self.recorder_thread.is_alive():
            print("⚠️ Recorder thread is still alive; refusing duplicate start")
            return False

        self.recording_session = True

        self.recorder_thread = threading.Thread(
            target=self.recorder.start,
            daemon=True
        )
        self.recorder_thread.start()

        self.create_floating_recorder()

        self.start_btn.configure(text="🟢 Recording...")
        self.status_label.configure(text="🟢 Recording")

        print("🧠 Floating recorder started")
        return True

    def stop_memory_recording(self):
        print("🔴 STOPPING MEMORY RECORDING")

        self.recording_session = False

        # This stops the REAL MemoryRecorder.
        self.recorder.stop()

        # IMPORTANT:
        # Do NOT destroy the floating recorder.
        # It must remain visible and show OFF.
        self.sync_floating_state(False)

        self.start_btn.configure(text="▶ Start Memory")
        self.status_label.configure(text="🔴 Idle")
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

            # The actual recorder state is authoritative.
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
            lambda: self.current_app.configure(text=f"Current App : {app}")
        )

        self.after(
            0,
            lambda: self.current_window.configure(text=f"Current Window : {title}")
        )

        self.after(
            0,
            lambda: self.last_updated.configure(text=f"Updated : {timestamp}")
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
