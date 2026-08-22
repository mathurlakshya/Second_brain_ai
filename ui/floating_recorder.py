import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback
        self.is_minimized = False

        screen_width = self.winfo_screenwidth()

        x = screen_width - 220
        y = 40

        self.normal_geometry = f"190x135+{x}+{y}"

        self.geometry(self.normal_geometry)

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.configure(fg_color="#202225")

        # -------------------------------------------------
        # NORMAL RECORDER
        # -------------------------------------------------

        self.container = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

        # Header
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

        # Minimize button
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

        # Status
        self.status = ctk.CTkLabel(
            self.container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )

        self.status.pack()

        # Current application
        self.current_app = ctk.CTkLabel(
            self.container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )

        self.current_app.pack(
            pady=(2, 6)
        )

        # Stop button
        self.stop_btn = ctk.CTkButton(
            self.container,
            text="⏹ OFF",
            width=90,
            height=28,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white",
            corner_radius=8,
            command=self.stop
        )

        self.stop_btn.pack(
            pady=(0, 8)
        )

        # -------------------------------------------------
        # MINIMIZED ICON
        # -------------------------------------------------

        self.mini_button = ctk.CTkButton(
            self,
            text="🧠",
            width=55,
            height=55,
            corner_radius=28,
            font=("Segoe UI Emoji", 22, "bold"),
            fg_color="#202225",
            hover_color="#34373C",
            command=self.restore
        )

        # -------------------------------------------------
        # DRAGGING
        # -------------------------------------------------

        self.offset_x = 0
        self.offset_y = 0

        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        self.title.bind("<Button-1>", self.start_move)
        self.title.bind("<B1-Motion>", self.do_move)

    # =====================================================
    # MINIMIZE
    # =====================================================

    def minimize(self):

        if self.is_minimized:
            return

        self.is_minimized = True

        # Remember current position
        x = self.winfo_x()
        y = self.winfo_y()

        self.mini_button.place(
            x=0,
            y=0
        )

        self.geometry(
            f"55x55+{x}+{y}"
        )

        self.container.pack_forget()

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(self):

        if not self.is_minimized:
            return

        self.is_minimized = False

        x = self.winfo_x()
        y = self.winfo_y()

        self.mini_button.place_forget()

        self.geometry(
            f"190x135+{x}+{y}"
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

    # =====================================================
    # UPDATE CURRENT APP
    # =====================================================

    def update_app(self, app, title):

        text = f"{app}\n{title}"

        try:

            if self.current_app.winfo_exists():

                self.current_app.configure(
                    text=text
                )

        except Exception:
            pass

    # =====================================================
    # STOP RECORDING
    # =====================================================

    def stop(self):

        self.stop_callback()

        app = self.master

        app.deiconify()
        app.lift()
        app.focus_force()

        self.destroy()

    # =====================================================
    # DRAGGING
    # =====================================================

    def start_move(self, event):

        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):

        x = self.winfo_x() + event.x - self.offset_x
        y = self.winfo_y() + event.y - self.offset_y

        self.geometry(
            f"+{x}+{y}"
        )
