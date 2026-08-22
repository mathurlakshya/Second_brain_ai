import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback

        self.is_minimized = False
        self.arrow_visible = False

        # ==================================================
        # WINDOW SETTINGS
        # ==================================================

        screen_width = self.winfo_screenwidth()

        x = screen_width - 240
        y = 40

        self.normal_width = 190
        self.normal_height = 135

        self.mini_width = 70
        self.mini_height = 48

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

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

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

        self.title.pack(
            side="left"
        )

        # --------------------------------------------------
        # MINIMIZE BUTTON
        # --------------------------------------------------

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

        self.minimize_btn.pack(
            side="right"
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status = ctk.CTkLabel(
            self.container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )

        self.status.pack()

        # --------------------------------------------------
        # CURRENT APPLICATION
        # --------------------------------------------------

        self.current_app = ctk.CTkLabel(
            self.container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )

        self.current_app.pack(
            pady=(2, 6)
        )

        # --------------------------------------------------
        # NORMAL OFF BUTTON
        # --------------------------------------------------

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
        # MINIMIZED BRAIN AREA
        # ==================================================

        self.mini_frame = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            corner_radius=24,
            fg_color="#202225"
        )

        self.mini_frame.pack_propagate(False)

        # --------------------------------------------------
        # BRAIN ICON
        # --------------------------------------------------

        self.mini_brain = ctk.CTkLabel(
            self.mini_frame,
            text="🧠",
            font=("Segoe UI Emoji", 17),
            width=48,
            height=48
        )

        self.mini_brain.pack(
            fill="both",
            expand=True
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
            font=("Segoe UI", 18, "bold"),
            command=self.show_control_menu
        )

        # ==================================================
        # SIDE CONTROL MENU
        # ==================================================

        self.control_menu = ctk.CTkFrame(
            self,
            width=135,
            height=90,
            corner_radius=10,
            fg_color="#202225"
        )

        self.control_menu.pack_propagate(False)

        # --------------------------------------------------
        # MAXIMIZE
        # --------------------------------------------------

        self.maximize_btn = ctk.CTkButton(
            self.control_menu,
            text="Maximize",
            height=30,
            corner_radius=7,
            fg_color="#30343A",
            hover_color="#444950",
            command=self.restore
        )

        self.maximize_btn.pack(
            fill="x",
            padx=8,
            pady=(8, 4)
        )

        # --------------------------------------------------
        # STOP
        # --------------------------------------------------

        self.mini_stop_btn = ctk.CTkButton(
            self.control_menu,
            text="🔴 OFF",
            height=30,
            corner_radius=7,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            text_color="white",
            command=self.stop
        )

        self.mini_stop_btn.pack(
            fill="x",
            padx=8,
            pady=(4, 8)
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
            self.mini_brain
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
        # HOVER EVENTS
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

        # Keep arrow available while mouse moves from brain
        # toward arrow.
        self.arrow_button.bind(
            "<Leave>",
            self.arrow_leave
        )

    # ======================================================
    # MINIMIZE
    # ======================================================

    def minimize(self):

        if self.is_minimized:
            return

        self.is_minimized = True

        # Remember current position
        x = self.winfo_x()
        y = self.winfo_y()

        # Hide normal UI
        self.container.pack_forget()

        # Hide control menu
        self.control_menu.place_forget()

        # Set minimized window size
        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        # Show brain
        self.mini_frame.place(
            x=0,
            y=0
        )

        # Arrow starts hidden
        self.hide_arrow()

    # ======================================================
    # RESTORE / MAXIMIZE
    # ======================================================

    def restore(self):

        if not self.is_minimized:
            return

        self.is_minimized = False

        # Hide minimized controls
        self.hide_arrow()
        self.control_menu.place_forget()

        x = self.winfo_x()
        y = self.winfo_y()

        # Hide brain
        self.mini_frame.place_forget()

        # Restore normal window
        self.geometry(
            f"{self.normal_width}x{self.normal_height}+{x}+{y}"
        )

        # Show normal UI
        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

    # ======================================================
    # SHOW ARROW
    # ======================================================

    def show_arrow(self, event=None):

        if not self.is_minimized:
            return

        self.arrow_visible = True

        self.arrow_button.place(
            x=48,
            y=9
        )

        self.arrow_button.lift()

    # ======================================================
    # HIDE ARROW
    # ======================================================

    def hide_arrow(self):

        self.arrow_visible = False

        try:
            self.arrow_button.place_forget()
        except Exception:
            pass

    # ======================================================
    # ARROW LEAVE
    # ======================================================

    def arrow_leave(self, event=None):

        # Don't immediately hide it.
        # This gives the user time to click the arrow
        # or move toward the control menu.

        self.after(
            400,
            self.check_arrow_position
        )

    def check_arrow_position(self):

        if not self.is_minimized:
            return

        # Keep arrow visible if menu is open.
        if self.control_menu.winfo_ismapped():
            return

        # Check pointer position.
        try:

            pointer_x = self.winfo_pointerx()
            pointer_y = self.winfo_pointery()

            window_x = self.winfo_rootx()
            window_y = self.winfo_rooty()

            relative_x = pointer_x - window_x
            relative_y = pointer_y - window_y

            # Keep arrow if cursor is still around
            # the minimized recorder.
            if (
                -5 <= relative_x <= self.mini_width + 10
                and
                -5 <= relative_y <= self.mini_height + 10
            ):
                return

        except Exception:
            pass

        self.hide_arrow()

    # ======================================================
    # CONTROL MENU
    # ======================================================

    def show_control_menu(self):

        if not self.is_minimized:
            return

        # Hide arrow
        self.arrow_button.place_forget()

        # Menu extends to the RIGHT of the minimized icon.
        self.control_menu.place(
            x=self.mini_width + 5,
            y=-20
        )

        self.control_menu.lift()

    # ======================================================
    # UPDATE CURRENT APPLICATION
    # ======================================================

    def update_app(self, app, title):

        text = f"{app}\n{title}"

        try:

            if self.current_app.winfo_exists():

                self.current_app.configure(
                    text=text
                )

        except Exception:
            pass

    # ======================================================
    # STOP RECORDING
    # ======================================================

    def stop(self):

        # Stop memory recorder
        self.stop_callback()

        # Get main application
        app = self.master

        try:

            app.deiconify()
            app.lift()
            app.focus_force()

        except Exception:
            pass

        # Close floating recorder
        self.destroy()

    # ======================================================
    # DRAGGING
    # ======================================================

    def start_move(self, event):

        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):

        x = self.winfo_x() + event.x - self.offset_x
        y = self.winfo_y() + event.y - self.offset_y

        self.geometry(
            f"+{x}+{y}"
        )
