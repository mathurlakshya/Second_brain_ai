import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback

        self.is_minimized = False
        self.bar_open = False
        self.recording = True

        # ==================================================
        # WINDOW SETTINGS
        # ==================================================

        screen_width = self.winfo_screenwidth()

        x = screen_width - 250
        y = 40

        self.normal_width = 190
        self.normal_height = 135

        self.mini_width = 62
        self.mini_height = 50

        self.bar_width = 255
        self.bar_height = 50

        self.geometry(
            f"{self.normal_width}x{self.normal_height}+{x}+{y}"
        )

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.configure(
            fg_color="#202225"
        )

        # ==================================================
        # NORMAL RECORDER
        # ==================================================

        self.container = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#202225"
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

        # ==================================================
        # HEADER
        # ==================================================

        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            padx=8,
            pady=(5, 0)
        )

        self.title = ctk.CTkLabel(
            self.header,
            text="🧠 REC",
            font=("Segoe UI", 14, "bold")
        )

        self.title.pack(side="left")

        self.minimize_btn = ctk.CTkButton(
            self.header,
            text="−",
            width=25,
            height=22,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#34373C",
            font=("Segoe UI", 16, "bold"),
            command=self.minimize
        )

        self.minimize_btn.pack(side="right")

        # ==================================================
        # STATUS
        # ==================================================

        self.status = ctk.CTkLabel(
            self.container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )

        self.status.pack()

        # ==================================================
        # CURRENT APP
        # ==================================================

        self.current_app = ctk.CTkLabel(
            self.container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )

        self.current_app.pack(
            pady=(2, 6)
        )

        # ==================================================
        # NORMAL STOP BUTTON
        # ==================================================

        self.stop_btn = ctk.CTkButton(
            self.container,
            text="🔴 OFF",
            width=90,
            height=28,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            text_color="white",
            corner_radius=8,
            command=self.stop
        )

        self.stop_btn.pack(
            pady=(0, 8)
        )

        # ==================================================
        # MINIMIZED BRAIN
        # ==================================================

        self.mini_frame = ctk.CTkFrame(
            self,
            width=self.mini_width,
            height=self.mini_height,
            corner_radius=25,
            fg_color="#202225"
        )

        self.mini_frame.pack_propagate(False)

        self.mini_brain = ctk.CTkLabel(
            self.mini_frame,
            text="🧠",
            font=("Segoe UI Emoji", 18),
            width=self.mini_width,
            height=self.mini_height
        )

        self.mini_brain.pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # SMALLER GREEN RECORDING GLOW
        # ==================================================

        self.glow = ctk.CTkFrame(
            self.mini_frame,
            width=5,
            height=5,
            corner_radius=3,
            fg_color="#00FF66"
        )

        self.glow.place(
            relx=0.13,
            rely=0.5,
            anchor="center"
        )

        # ==================================================
        # SIDE ARROW
        # ==================================================

        self.arrow_button = ctk.CTkButton(
            self,
            text="›",
            width=18,
            height=30,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#4A4F57",
            font=("Segoe UI", 17, "bold"),
            command=self.toggle_bar
        )

        # ==================================================
        # COMPACT SIDE BAR
        # ==================================================

        self.control_bar = ctk.CTkFrame(
            self,
            width=self.bar_width,
            height=self.bar_height,
            corner_radius=25,
            fg_color="#202225"
        )

        self.control_bar.pack_propagate(False)

        # ==================================================
        # BRAIN
        # ==================================================

        self.bar_brain = ctk.CTkLabel(
            self.control_bar,
            text="🧠",
            font=("Segoe UI Emoji", 17)
        )

        self.bar_brain.pack(
            side="left",
            padx=(8, 4)
        )

        # ==================================================
        # RED OFF BUTTON
        # ==================================================

        self.bar_off_btn = ctk.CTkButton(
            self.control_bar,
            text="●",
            width=34,
            height=34,
            corner_radius=17,
            fg_color="#E53935",
            hover_color="#B71C1C",
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            command=self.stop
        )

        self.bar_off_btn.pack(
            side="left",
            padx=3
        )

        # ==================================================
        # GREEN ON BUTTON
        # ==================================================

        self.bar_on_btn = ctk.CTkButton(
            self.control_bar,
            text="●",
            width=34,
            height=34,
            corner_radius=17,
            fg_color="#285C3A",
            hover_color="#285C3A",
            text_color="#6F8F7A",
            font=("Segoe UI", 14, "bold"),
            command=self.start_recording
        )

        self.bar_on_btn.pack(
            side="left",
            padx=3
        )

        # ==================================================
        # MAXIMIZE
        # ==================================================

        self.maximize_btn = ctk.CTkButton(
            self.control_bar,
            text="⛶",
            width=34,
            height=34,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#444950",
            font=("Segoe UI", 17, "bold"),
            command=self.restore
        )

        self.maximize_btn.pack(
            side="left",
            padx=3
        )

        # ==================================================
        # CLOSE
        # ==================================================

        self.close_btn = ctk.CTkButton(
            self.control_bar,
            text="✕",
            width=34,
            height=34,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#444950",
            font=("Segoe UI", 15, "bold"),
            command=self.close_floating
        )

        self.close_btn.pack(
            side="left",
            padx=3
        )

        # ==================================================
        # DRAGGING
        # ==================================================

        self.offset_x = 0
        self.offset_y = 0

        drag_widgets = [
            self,
            self.container,
            self.header,
            self.title,
            self.mini_frame,
            self.mini_brain,
            self.control_bar,
            self.bar_brain
        ]

        for widget in drag_widgets:

            widget.bind(
                "<Button-1>",
                self.start_move
            )

            widget.bind(
                "<B1-Motion>",
                self.do_move
            )

        # ==================================================
        # HOVER
        # ==================================================

        self.mini_frame.bind(
            "<Enter>",
            self.show_arrow
        )

        self.mini_brain.bind(
            "<Enter>",
            self.show_arrow
        )

        self.arrow_button.bind(
            "<Enter>",
            self.show_arrow
        )

        self.update_recording_visuals()

    # ==================================================
    # MINIMIZE
    # ==================================================

    def minimize(self):

        if self.is_minimized:
            return

        self.is_minimized = True
        self.bar_open = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.container.pack_forget()

        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        self.mini_frame.place(
            x=0,
            y=0
        )

        self.control_bar.place_forget()

        self.hide_arrow()

    # ==================================================
    # SHOW ARROW
    # ==================================================

    def show_arrow(self, event=None):

        if not self.is_minimized:
            return

        # Keep the arrow completely inside the mini icon.
        self.arrow_button.place(
            x=self.mini_width - 21,
            y=10
        )

        self.arrow_button.lift()

    # ==================================================
    # HIDE ARROW
    # ==================================================

    def hide_arrow(self):

        try:
            self.arrow_button.place_forget()
        except Exception:
            pass

    # ==================================================
    # TOGGLE BAR
    # ==================================================

    def toggle_bar(self):

        if not self.is_minimized:
            return

        if self.bar_open:
            self.close_bar()
        else:
            self.open_bar()

    # ==================================================
    # OPEN BAR
    # ==================================================

    def open_bar(self):

        self.bar_open = True

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.bar_width}x{self.bar_height}+{x}+{y}"
        )

        self.mini_frame.place_forget()

        self.control_bar.place(
            x=0,
            y=0
        )

        self.control_bar.lift()

        self.update_recording_visuals()

    # ==================================================
    # CLOSE BAR
    # ==================================================

    def close_bar(self):

        self.bar_open = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        self.control_bar.place_forget()

        self.mini_frame.place(
            x=0,
            y=0
        )

        self.hide_arrow()

    # ==================================================
    # RESTORE
    # ==================================================

    def restore(self):

        if not self.is_minimized:
            return

        x = self.winfo_x()
        y = self.winfo_y()

        self.is_minimized = False
        self.bar_open = False

        self.control_bar.place_forget()
        self.mini_frame.place_forget()
        self.hide_arrow()

        self.geometry(
            f"{self.normal_width}x{self.normal_height}+{x}+{y}"
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

        self.update_recording_visuals()

    # ==================================================
    # RECORDING VISUALS
    # ==================================================

    def update_recording_visuals(self):

        if self.recording:

            # ---------------- RECORDING ON ----------------

            self.status.configure(
                text="🟢 Recording"
            )

            self.stop_btn.configure(
                text="🔴 OFF",
                fg_color="#D32F2F",
                hover_color="#B71C1C"
            )

            self.bar_off_btn.configure(
                state="normal",
                fg_color="#E53935",
                hover_color="#B71C1C",
                text_color="white"
            )

            self.bar_on_btn.configure(
                state="disabled",
                fg_color="#285C3A",
                hover_color="#285C3A",
                text_color="#6F8F7A"
            )

            # Small green glow
            self.glow.configure(
                fg_color="#00FF66"
            )

        else:

            # ---------------- RECORDING OFF ----------------

            self.status.configure(
                text="🔴 Not Recording"
            )

            self.stop_btn.configure(
                text="🔴 OFF",
                fg_color="#5A2929",
                hover_color="#5A2929"
            )

            self.bar_off_btn.configure(
                state="disabled",
                fg_color="#5A2929",
                hover_color="#5A2929",
                text_color="#8A6666"
            )

            self.bar_on_btn.configure(
                state="normal",
                fg_color="#00C853",
                hover_color="#00A846",
                text_color="white"
            )

            self.glow.configure(
                fg_color="#333333"
            )

    # ==================================================
    # START RECORDING
    # ==================================================

    def start_recording(self):

        if self.recording:
            return

        print("🟢 FloatingRecorder ON clicked")

        self.recording = True

        # Dashboard's toggle_memory() starts the recorder.
        try:
            self.stop_callback()
        except Exception as e:
            print(
                f"⚠️ Start callback failed: {e}"
            )

        self.update_recording_visuals()

    # ==================================================
    # UPDATE APP
    # ==================================================

    def update_app(self, app, title):

        text = f"{app}\n{title}"

        try:

            if self.current_app.winfo_exists():

                self.current_app.configure(
                    text=text
                )

        except Exception:
            pass

    # ==================================================
    # STOP RECORDING
    # ==================================================

    def stop(self):

        print("🔴 FloatingRecorder OFF clicked")

        self.recording = False

        # Stop the actual MemoryRecorder.
        try:
            self.stop_callback()
        except Exception as e:
            print(
                f"⚠️ Stop callback failed: {e}"
            )

        # IMPORTANT:
        # Do NOT destroy the floating recorder.
        # Do NOT open/deiconify the main application.
        #
        # The floating recorder remains available so
        # the user can turn recording back ON directly.

        self.update_recording_visuals()

    # ==================================================
    # CLOSE FLOATING RECORDER
    # ==================================================

    def close_floating(self):

        print("✕ Floating recorder closed")

        try:
            self.destroy()
        except Exception:
            pass

    # ==================================================
    # DRAGGING
    # ==================================================

    def start_move(self, event):

        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):

        x = self.winfo_x() + event.x - self.offset_x
        y = self.winfo_y() + event.y - self.offset_y

        self.geometry(
            f"+{x}+{y}"
        )

    # ==================================================
    # DESTROY
    # ==================================================

    def destroy(self):

        try:
            self.hide_arrow()
            self.control_bar.place_forget()
            self.mini_frame.place_forget()
        except Exception:
            pass

        super().destroy()
