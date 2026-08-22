import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback

        self.is_minimized = False
        self.arrow_visible = False
        self.control_menu = None

        # ==================================================
        # WINDOW SETTINGS
        # ==================================================

        screen_width = self.winfo_screenwidth()

        x = screen_width - 250
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
        # MINIMIZE
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
        # CURRENT APP
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
        # OFF BUTTON
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
        # MINIMIZED BRAIN
        # ==================================================

        self.mini_frame = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            corner_radius=24,
            fg_color="#202225"
        )

        self.mini_frame.pack_propagate(False)

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

    # ======================================================
    # MINIMIZE
    # ======================================================

    def minimize(self):

        if self.is_minimized:
            return

        self.is_minimized = True

        x = self.winfo_x()
        y = self.winfo_y()

        # Hide normal recorder
        self.container.pack_forget()

        # Make small window
        self.geometry(
            f"{self.mini_width}x{self.mini_height}+{x}+{y}"
        )

        # Show brain
        self.mini_frame.place(
            x=0,
            y=0
        )

        # Arrow hidden initially
        self.hide_arrow()

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
    # CONTROL MENU
    # ======================================================

    def show_control_menu(self):

        if not self.is_minimized:
            return

        # Close existing menu first
        self.close_control_menu()

        # Get recorder position
        recorder_x = self.winfo_rootx()
        recorder_y = self.winfo_rooty()

        # Create a NEW top-level window
        self.control_menu = ctk.CTkToplevel(
            self
        )

        self.control_menu.overrideredirect(True)
        self.control_menu.attributes(
            "-topmost",
            True
        )

        self.control_menu.configure(
            fg_color="#202225"
        )

        # Menu size
        menu_width = 145
        menu_height = 95

        # Put menu to the RIGHT of recorder
        menu_x = recorder_x + self.mini_width + 5
        menu_y = recorder_y - 5

        self.control_menu.geometry(
            f"{menu_width}x{menu_height}+{menu_x}+{menu_y}"
        )

        # ==================================================
        # MENU CONTENT
        # ==================================================

        menu_frame = ctk.CTkFrame(
            self.control_menu,
            corner_radius=10,
            fg_color="#202225"
        )

        menu_frame.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        # --------------------------------------------------
        # MAXIMIZE
        # --------------------------------------------------

        maximize_btn = ctk.CTkButton(
            menu_frame,
            text="Maximize",
            height=32,
            corner_radius=7,
            fg_color="#30343A",
            hover_color="#444950",
            command=self.restore
        )

        maximize_btn.pack(
            fill="x",
            padx=8,
            pady=(8, 4)
        )

        # --------------------------------------------------
        # STOP
        # --------------------------------------------------

        stop_btn = ctk.CTkButton(
            menu_frame,
            text="🔴 OFF",
            height=32,
            corner_radius=7,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            text_color="white",
            command=self.stop
        )

        stop_btn.pack(
            fill="x",
            padx=8,
            pady=(4, 8)
        )

        # Make sure menu is visible
        self.control_menu.deiconify()
        self.control_menu.lift()
        self.control_menu.focus_force()

    # ======================================================
    # CLOSE CONTROL MENU
    # ======================================================

    def close_control_menu(self):

        if self.control_menu is not None:

            try:
                self.control_menu.destroy()
            except Exception:
                pass

            self.control_menu = None

    # ======================================================
    # RESTORE / MAXIMIZE
    # ======================================================

    def restore(self):

        self.close_control_menu()

        if not self.is_minimized:
            return

        self.is_minimized = False

        self.hide_arrow()

        x = self.winfo_x()
        y = self.winfo_y()

        # Hide minimized brain
        self.mini_frame.place_forget()

        # Restore window
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
    # UPDATE APP
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
    # STOP
    # ======================================================

    def stop(self):

        print("🔴 FloatingRecorder OFF clicked")
    
        # The Dashboard handles:
        # 1. stopping MemoryRecorder
        # 2. destroying this window
        # 3. clearing self.floating
    
        self.stop_callback()
    
        try:
    
            app = self.master
    
            app.deiconify()
            app.lift()
            app.focus_force()
    
        except Exception as e:
    
            print(
                f"⚠️ Could not restore main app: {e}"
            )

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

        # If menu is open, move it with recorder
        if self.control_menu is not None:

            try:

                menu_x = x + self.mini_width + 5
                menu_y = y - 5

                self.control_menu.geometry(
                    f"+{menu_x}+{menu_y}"
                )

            except Exception:
                pass
