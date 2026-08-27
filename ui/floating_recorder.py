import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback

        # ==================================================
        # STATE
        # ==================================================

        self.recording = True
        self.is_minimized = False
        self.bar_open = False

        # ==================================================
        # SIZES
        # ==================================================

        self.normal_width = 190
        self.normal_height = 135

        self.mini_width = 64
        self.mini_height = 50

        self.bar_width = 250
        self.bar_height = 50

        self.arrow_width = 24
        self.arrow_height = 32

        # ==================================================
        # WINDOW
        # ==================================================

        screen_width = self.winfo_screenwidth()

        x = screen_width - 250
        y = 40

        self.geometry(
            f"{self.normal_width}x{self.normal_height}+{x}+{y}"
        )

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.configure(
            fg_color="#202225"
        )

        # ==================================================
        # NORMAL UI
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

        # ---------------- HEADER ----------------

        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            padx=8,
            pady=(6, 0)
        )

        self.title_label = ctk.CTkLabel(
            self.header,
            text="🧠 REC",
            font=("Segoe UI", 14, "bold")
        )

        self.title_label.pack(
            side="left"
        )

        self.normal_minimize_btn = ctk.CTkButton(
            self.header,
            text="−",
            width=26,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#34373C",
            font=("Segoe UI", 16, "bold"),
            command=self.minimize
        )

        self.normal_minimize_btn.pack(
            side="right"
        )

        # ---------------- STATUS ----------------

        self.status = ctk.CTkLabel(
            self.container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )

        self.status.pack()

        # ---------------- CURRENT APP ----------------

        self.current_app = ctk.CTkLabel(
            self.container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )

        self.current_app.pack(
            pady=(2, 6)
        )

        # ---------------- OFF BUTTON ----------------

        self.stop_btn = ctk.CTkButton(
            self.container,
            text="🔴 OFF",
            width=90,
            height=28,
            corner_radius=8,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.stop
        )

        self.stop_btn.pack(
            pady=(0, 8)
        )

        # ==================================================
        # MINI UI
        # ==================================================

        self.mini_frame = ctk.CTkFrame(
            self,
            width=self.mini_width,
            height=self.mini_height,
            corner_radius=25,
            fg_color="#202225"
        )

        self.mini_frame.pack_propagate(False)

        # ---------------- BRAIN ----------------

        self.mini_brain = ctk.CTkLabel(
            self.mini_frame,
            text="🧠",
            font=("Segoe UI Emoji", 18),
            width=32,
            height=32
        )

        self.mini_brain.place(
            x=8,
            y=9
        )

        # ---------------- GREEN LIGHT ----------------

        self.glow = ctk.CTkFrame(
            self.mini_frame,
            width=5,
            height=5,
            corner_radius=3,
            fg_color="#00FF66"
        )

        self.glow.place(
            x=6,
            y=6
        )

        # ==================================================
        # SIDE ARROW
        #
        # This is OUTSIDE mini_frame deliberately.
        # Therefore it cannot be clipped by the mini icon.
        # ==================================================

        self.arrow_button = ctk.CTkButton(
            self,
            text="›",
            width=self.arrow_width,
            height=self.arrow_height,
            corner_radius=7,
            fg_color="#30343A",
            hover_color="#4A4F57",
            font=("Segoe UI", 18, "bold"),
            command=self.toggle_side_bar
        )

        # ==================================================
        # SIDE CONTROL BAR
        # ==================================================

        self.control_bar = ctk.CTkFrame(
            self,
            width=self.bar_width,
            height=self.bar_height,
            corner_radius=25,
            fg_color="#202225"
        )

        self.control_bar.pack_propagate(False)

        # ---------------- BAR BRAIN ----------------

        self.bar_brain = ctk.CTkLabel(
            self.control_bar,
            text="🧠",
            font=("Segoe UI Emoji", 17)
        )

        self.bar_brain.pack(
            side="left",
            padx=(10, 3)
        )

        # ---------------- OFF ----------------

        self.bar_off = ctk.CTkButton(
            self.control_bar,
            text="●",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#E53935",
            hover_color="#B71C1C",
            font=("Segoe UI", 14, "bold"),
            command=self.stop
        )

        self.bar_off.pack(
            side="left",
            padx=3
        )

        # ---------------- ON ----------------

        self.bar_on = ctk.CTkButton(
            self.control_bar,
            text="●",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#285C3A",
            hover_color="#285C3A",
            text_color="#6F8F7A",
            font=("Segoe UI", 14, "bold"),
            command=self.start_recording
        )

        self.bar_on.pack(
            side="left",
            padx=3
        )

        # ---------------- MAXIMIZE ----------------

        self.maximize_btn = ctk.CTkButton(
            self.control_bar,
            text="⛶",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#444950",
            font=("Segoe UI", 16, "bold"),
            command=self.restore
        )

        self.maximize_btn.pack(
            side="left",
            padx=3
        )

        # ---------------- CLOSE ----------------

        self.close_btn = ctk.CTkButton(
            self.control_bar,
            text="✕",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#444950",
            font=("Segoe UI", 14, "bold"),
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

        for widget in [
            self,
            self.container,
            self.header,
            self.title_label,
            self.status,
            self.current_app,
            self.mini_frame,
            self.mini_brain,
            self.control_bar,
            self.bar_brain
        ]:

            widget.bind(
                "<Button-1>",
                self.start_move
            )

            widget.bind(
                "<B1-Motion>",
                self.do_move
            )

        # ==================================================
        # INITIAL STATE
        # ==================================================

        self.control_bar.place_forget()
        self.mini_frame.place_forget()
        self.arrow_button.place_forget()

        self.update_recording_visuals()

    # ==================================================
    # POSITION MINI ELEMENTS
    # ==================================================

    def position_mini_elements(self):

        # Brain is inside mini frame.
        self.mini_brain.place(
            x=8,
            y=9,
            width=32,
            height=32
        )

        # Small green light.
        self.glow.place(
            x=6,
            y=6,
            width=5,
            height=5
        )

        # Arrow is intentionally positioned OUTSIDE
        # the mini frame but inside the Toplevel.

        arrow_x = self.mini_width - self.arrow_width + 2

        arrow_y = (
            self.mini_height - self.arrow_height
        ) // 2

        self.arrow_button.place(
            x=arrow_x,
            y=arrow_y,
            width=self.arrow_width,
            height=self.arrow_height
        )

        self.arrow_button.lift()

    # ==================================================
    # MINIMIZE
    # ==================================================

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

        self.mini_frame.place(
            x=0,
            y=0,
            width=self.mini_width,
            height=self.mini_height
        )

        self.mini_frame.lift()

        self.position_mini_elements()

        self.update_recording_visuals()

    # ==================================================
    # OPEN SIDE BAR
    # ==================================================

    def open_side_bar(self):

        if not self.is_minimized:
            return

        self.bar_open = True

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.bar_width}x{self.bar_height}+{x}+{y}"
        )

        self.mini_frame.place_forget()

        self.control_bar.place(
            x=0,
            y=0,
            width=self.bar_width,
            height=self.bar_height
        )

        self.control_bar.lift()

        # Closing arrow remains at the RIGHT.
        self.arrow_button.configure(
            text="‹"
        )

        arrow_x = (
            self.bar_width
            - self.arrow_width
            - 2
        )

        arrow_y = (
            self.bar_height
            - self.arrow_height
        ) // 2

        self.arrow_button.place(
            x=arrow_x,
            y=arrow_y,
            width=self.arrow_width,
            height=self.arrow_height
        )

        self.arrow_button.lift()

        self.update_recording_visuals()

    # ==================================================
    # CLOSE SIDE BAR
    # ==================================================

    def close_side_bar(self):

        if not self.bar_open:
            return

        self.bar_open = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        self.control_bar.place_forget()

        self.mini_frame.place(
            x=0,
            y=0,
            width=self.mini_width,
            height=self.mini_height
        )

        self.arrow_button.configure(
            text="›"
        )

        self.position_mini_elements()

        self.update_recording_visuals()

    # ==================================================
    # TOGGLE SIDE BAR
    # ==================================================

    def toggle_side_bar(self):

        if not self.is_minimized:
            return

        if self.bar_open:
            self.close_side_bar()
        else:
            self.open_side_bar()

    # ==================================================
    # RESTORE
    # ==================================================

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
        self.arrow_button.place_forget()

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

        try:

            if not self.winfo_exists():
                return

        except Exception:
            return

        try:

            if self.recording:

                self.status.configure(
                    text="🟢 Recording"
                )

                self.stop_btn.configure(
                    fg_color="#D32F2F",
                    hover_color="#B71C1C"
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

                # Green light ON.
                self.glow.configure(
                    fg_color="#00FF66"
                )

            else:

                self.status.configure(
                    text="🔴 Not Recording"
                )

                self.stop_btn.configure(
                    fg_color="#5A2929",
                    hover_color="#5A2929"
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

                # Green light OFF/faded.
                self.glow.configure(
                    fg_color="#333333"
                )

        except Exception as e:

            # Do NOT crash Tkinter if a widget is being
            # destroyed during a callback.
            print(
                f"⚠️ FloatingRecorder visual update failed: {e}"
            )

    # ==================================================
    # START RECORDING
    # ==================================================

    def start_recording(self):

        if self.recording:
            return

        print("🟢 FloatingRecorder ON clicked")

        self.recording = True

        try:
            self.stop_callback()
        except Exception as e:
            print(
                f"⚠️ Start callback failed: {e}"
            )

        self.update_recording_visuals()

    # ==================================================
    # STOP RECORDING
    # ==================================================

    def stop(self):

        if not self.recording:
            return

        print("🔴 FloatingRecorder OFF clicked")

        self.recording = False

        try:
            self.stop_callback()
        except Exception as e:
            print(
                f"⚠️ Stop callback failed: {e}"
            )

        # IMPORTANT:
        # DO NOT destroy the floating recorder.
        self.update_recording_visuals()

        print(
            "⏹ Recording stopped — FloatingRecorder remains visible"
        )

    # ==================================================
    # UPDATE CURRENT APP
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
    # CLOSE FLOATING RECORDER
    # ==================================================

    def close_floating(self):

        print("✕ Closing FloatingRecorder")

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

        x = (
            self.winfo_x()
            + event.x
            - self.offset_x
        )

        y = (
            self.winfo_y()
            + event.y
            - self.offset_y
        )

        self.geometry(
            f"+{x}+{y}"
        )

        # Keep the arrow attached to the
        # right side after dragging.

        if self.is_minimized:

            if self.bar_open:

                arrow_x = (
                    self.bar_width
                    - self.arrow_width
                    - 2
                )

                arrow_y = (
                    self.bar_height
                    - self.arrow_height
                ) // 2

                self.arrow_button.place(
                    x=arrow_x,
                    y=arrow_y,
                    width=self.arrow_width,
                    height=self.arrow_height
                )

            else:

                self.position_mini_elements()
