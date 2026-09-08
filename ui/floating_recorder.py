import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, start_callback=None, stop_callback=None):
        super().__init__(parent)

        self.start_callback = start_callback
        self.stop_callback = stop_callback

        self.recording = True
        self.is_minimized = False
        self.bar_open = False

        self.normal_width = 190
        self.normal_height = 135
        self.mini_width = 64
        self.mini_height = 50
        self.bar_width = 250
        self.bar_height = 50
        self.arrow_width = 22
        self.arrow_height = 32

        screen_width = self.winfo_screenwidth()
        x = screen_width - self.normal_width - 30
        y = 40

        self.geometry(f"{self.normal_width}x{self.normal_height}+{x}+{y}")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#202225")

        self.container = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#202225"
        )
        self.container.pack(fill="both", expand=True, padx=3, pady=3)

        self.header = ctk.CTkFrame(
            self.container, fg_color="transparent"
        )
        self.header.pack(fill="x", padx=8, pady=(6, 0))

        self.title_label = ctk.CTkLabel(
            self.header, text="🧠 REC",
            font=("Segoe UI", 14, "bold")
        )
        self.title_label.pack(side="left")

        self.minimize_btn = ctk.CTkButton(
            self.header, text="−", width=26, height=24,
            corner_radius=6, fg_color="transparent",
            hover_color="#34373C",
            font=("Segoe UI", 16, "bold"),
            command=self.minimize
        )
        self.minimize_btn.pack(side="right")

        self.status = ctk.CTkLabel(
            self.container, text="🟢 Recording",
            font=("Segoe UI", 11)
        )
        self.status.pack(pady=(5, 0))

        self.current_app = ctk.CTkLabel(
            self.container, text="Waiting...",
            font=("Segoe UI", 10), wraplength=160
        )
        self.current_app.pack(pady=(2, 7))

        self.stop_btn = ctk.CTkButton(
            self.container, text="🔴 OFF", width=90, height=28,
            corner_radius=8, fg_color="#D32F2F",
            hover_color="#B71C1C", text_color="white",
            command=self.stop
        )
        self.stop_btn.pack(pady=(0, 8))

        self.mini_frame = ctk.CTkFrame(
            self, width=self.mini_width, height=self.mini_height,
            corner_radius=25, fg_color="#202225"
        )
        self.mini_frame.pack_propagate(False)

        self.mini_brain = ctk.CTkLabel(
            self.mini_frame, text="🧠",
            font=("Segoe UI Emoji", 18), width=34, height=34
        )
        self.mini_brain.place(x=5, y=8)

        self.glow = ctk.CTkFrame(
            self.mini_frame, width=5, height=5,
            corner_radius=3, fg_color="#00FF66"
        )
        self.glow.place(x=7, y=7)

        self.arrow_button = ctk.CTkButton(
            self.mini_frame, text="›",
            width=self.arrow_width, height=self.arrow_height,
            corner_radius=7, fg_color="#30343A",
            hover_color="#4A4F57", text_color="white",
            font=("Segoe UI", 18, "bold"),
            command=self.toggle_side_bar
        )
        self.arrow_button.place(
            x=self.mini_width - self.arrow_width - 3, y=9
        )

        self.control_bar = ctk.CTkFrame(
            self, width=self.bar_width, height=self.bar_height,
            corner_radius=25, fg_color="#202225"
        )
        self.control_bar.pack_propagate(False)

        self.bar_brain = ctk.CTkLabel(
            self.control_bar, text="🧠",
            font=("Segoe UI Emoji", 17)
        )
        self.bar_brain.place(x=8, y=10)

        self.bar_off = ctk.CTkButton(
            self.control_bar, text="●", width=32, height=32,
            corner_radius=16, fg_color="#E53935",
            hover_color="#B71C1C", text_color="white",
            font=("Segoe UI", 14, "bold"),
            command=self.stop
        )
        self.bar_off.place(x=42, y=9)

        self.bar_on = ctk.CTkButton(
            self.control_bar, text="●", width=32, height=32,
            corner_radius=16, fg_color="#285C3A",
            hover_color="#285C3A", text_color="#6F8F7A",
            font=("Segoe UI", 14, "bold"),
            command=self.start_recording
        )
        self.bar_on.place(x=80, y=9)

        self.maximize_btn = ctk.CTkButton(
            self.control_bar, text="⛶", width=32, height=32,
            corner_radius=8, fg_color="#30343A",
            hover_color="#444950", text_color="white",
            font=("Segoe UI", 16, "bold"),
            command=self.restore
        )
        self.maximize_btn.place(x=118, y=9)

        self.close_btn = ctk.CTkButton(
            self.control_bar, text="✕", width=32, height=32,
            corner_radius=8, fg_color="#30343A",
            hover_color="#444950", text_color="white",
            font=("Segoe UI", 14, "bold"),
            command=self.close_floating
        )
        self.close_btn.place(x=156, y=9)

        self.bar_arrow = ctk.CTkButton(
            self.control_bar, text="‹",
            width=self.arrow_width, height=self.arrow_height,
            corner_radius=7, fg_color="#30343A",
            hover_color="#4A4F57", text_color="white",
            font=("Segoe UI", 18, "bold"),
            command=self.close_side_bar
        )
        self.bar_arrow.place(
            x=self.bar_width - self.arrow_width - 3, y=9
        )

        self.offset_x = 0
        self.offset_y = 0

        drag_widgets = [
            self, self.container, self.header, self.title_label,
            self.status, self.current_app, self.mini_frame,
            self.mini_brain, self.glow, self.control_bar,
            self.bar_brain
        ]

        for widget in drag_widgets:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        self.mini_frame.place_forget()
        self.control_bar.place_forget()

        self.update_recording_visuals()

    # --------------------------------------------------
    # AUTHORITATIVE STATE SYNC
    # --------------------------------------------------

    def set_recording_state(self, recording):
        self.recording = bool(recording)
        self.update_recording_visuals()

    # --------------------------------------------------
    # MINIMIZE / BAR
    # --------------------------------------------------

    def minimize(self):
        if self.is_minimized:
            return

        print("🔽 FloatingRecorder minimized")

        self.is_minimized = True
        self.bar_open = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.container.pack_forget()
        self.control_bar.place_forget()

        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        self.mini_frame.place(x=0, y=0)
        self.position_mini_elements()
        self.update_recording_visuals()

    def position_mini_elements(self):
        self.mini_brain.place(x=5, y=8)
        self.glow.place(x=7, y=7)
        self.arrow_button.place(
            x=self.mini_width - self.arrow_width - 3, y=9
        )

        self.mini_brain.lift()
        self.glow.lift()
        self.arrow_button.lift()

    def open_side_bar(self):
        if not self.is_minimized or self.bar_open:
            return

        print("➡ Opening FloatingRecorder control bar")

        self.bar_open = True

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.bar_width}x{self.bar_height}+{x}+{y}"
        )

        self.mini_frame.place_forget()
        self.control_bar.place(x=0, y=0)

        self.bar_arrow.place(
            x=self.bar_width - self.arrow_width - 3, y=9
        )
        self.bar_arrow.lift()

        self.update_recording_visuals()

    def close_side_bar(self):
        if not self.bar_open:
            return

        print("⬅ Closing FloatingRecorder control bar")

        self.bar_open = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        self.control_bar.place_forget()
        self.mini_frame.place(x=0, y=0)

        self.position_mini_elements()
        self.update_recording_visuals()

    def toggle_side_bar(self):
        if not self.is_minimized:
            return

        if self.bar_open:
            self.close_side_bar()
        else:
            self.open_side_bar()

    def restore(self):
        if not self.is_minimized:
            return

        print("⛶ Restoring FloatingRecorder")

        x = self.winfo_x()
        y = self.winfo_y()

        self.is_minimized = False
        self.bar_open = False

        self.mini_frame.place_forget()
        self.control_bar.place_forget()

        self.geometry(
            f"{self.normal_width}x{self.normal_height}+{x}+{y}"
        )

        self.container.pack(
            fill="both", expand=True, padx=3, pady=3
        )

        self.update_recording_visuals()

    # --------------------------------------------------
    # VISUAL STATE
    # --------------------------------------------------

    def update_recording_visuals(self):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        try:
            if self.recording:
                self.status.configure(text="🟢 Recording")

                self.stop_btn.configure(
                    text="🔴 OFF",
                    fg_color="#D32F2F",
                    hover_color="#B71C1C",
                    state="normal"
                )

                self.bar_off.configure(
                    state="normal",
                    fg_color="#E53935",
                    hover_color="#B71C1C",
                    text_color="white"
                )

                self.bar_on.configure(
                    state="disabled",
                    fg_color="#285C3A",
                    hover_color="#285C3A",
                    text_color="#6F8F7A"
                )

                self.glow.configure(fg_color="#00FF66")

            else:
                self.status.configure(text="🔴 Not Recording")

                self.stop_btn.configure(
                    text="🔴 OFF",
                    fg_color="#5A2929",
                    hover_color="#5A2929",
                    state="disabled"
                )

                self.bar_off.configure(
                    state="disabled",
                    fg_color="#5A2929",
                    hover_color="#5A2929",
                    text_color="#8A6666"
                )

                self.bar_on.configure(
                    state="normal",
                    fg_color="#00C853",
                    hover_color="#00A846",
                    text_color="white"
                )

                self.glow.configure(fg_color="#333333")

        except Exception as e:
            print(f"⚠️ FloatingRecorder visual update failed: {e}")

    # --------------------------------------------------
    # START / STOP
    # --------------------------------------------------

    def start_recording(self):
        if self.recording:
            return

        print("🟢 FloatingRecorder ON clicked")

        if not self.start_callback:
            print("⚠️ No start callback configured")
            return

        try:
            result = self.start_callback()

            if result is False:
                print("⚠️ Parent refused to start recording")
                return

            self.recording = True
            self.update_recording_visuals()

            print("▶ Recording started")

        except Exception as e:
            print(f"⚠️ Start callback failed: {e}")

    def stop(self):
        if not self.recording:
            return

        print("🔴 FloatingRecorder OFF clicked")

        if not self.stop_callback:
            print("❌ No stop callback configured — recording was NOT stopped")
            return

        try:
            result = self.stop_callback()

            if result is False:
                print("⚠️ Parent refused to stop recording")
                return

            # Only change the floating UI after the real recorder
            # has been told to stop.
            self.recording = False
            self.update_recording_visuals()

            print("⏹ Recording stopped — FloatingRecorder remains visible")

        except Exception as e:
            print(f"⚠️ Stop callback failed: {e}")

    # --------------------------------------------------
    # APP DISPLAY
    # --------------------------------------------------

    def update_app(self, app, title):
        text = f"{app}\n{title}"

        try:
            if self.current_app.winfo_exists():
                self.current_app.configure(text=text)
        except Exception:
            pass

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    def close_floating(self):
        print("✕ Closing FloatingRecorder")

        try:
            self.destroy()
        except Exception:
            pass

    # --------------------------------------------------
    # DRAGGING
    # --------------------------------------------------

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        try:
            x = self.winfo_x() + event.x - self.offset_x
            y = self.winfo_y() + event.y - self.offset_y
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    # --------------------------------------------------
    # DESTROY
    # --------------------------------------------------

    def destroy(self):
        print("✕ Destroying FloatingRecorder")

        try:
            self.control_bar.place_forget()
        except Exception:
            pass

        try:
            self.mini_frame.place_forget()
        except Exception:
            pass

        try:
            self.container.pack_forget()
        except Exception:
            pass

        try:
            super().destroy()
        except Exception:
            pass
