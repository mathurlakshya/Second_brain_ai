import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback
        self.is_minimized = False

        screen_width = self.winfo_screenwidth()

        x = screen_width - 220
        y = 40

        self.geometry(f"190x135+{x}+{y}")

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.configure(fg_color="#202225")

        # ==================================================
        # NORMAL RECORDER
        # ==================================================

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

        self.title.pack(side="left")

        # Minimize
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

        # Status
        self.status = ctk.CTkLabel(
            self.container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )

        self.status.pack()

        # Current app
        self.current_app = ctk.CTkLabel(
            self.container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )

        self.current_app.pack(
            pady=(2, 6)
        )

        # OFF button
        self.stop_btn = ctk.CTkButton(
            self.container,
            text="⏹ OFF",
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

        self.mini_size = 48

        self.mini_frame = ctk.CTkFrame(
            self,
            width=self.mini_size,
            height=self.mini_size,
            corner_radius=24,
            fg_color="#202225"
        )

        self.mini_frame.pack_propagate(False)

        self.mini_brain = ctk.CTkLabel(
            self.mini_frame,
            text="🧠",
            font=("Segoe UI Emoji", 18),
            width=self.mini_size,
            height=self.mini_size
        )

        self.mini_brain.pack(
            fill="both",
            expand=True
        )

        # Side arrow
        self.arrow_button = ctk.CTkButton(
            self,
            text="›",
            width=18,
            height=30,
            corner_radius=8,
            fg_color="#30343A",
            hover_color="#444950",
            font=("Segoe UI", 18, "bold"),
            command=self.show_mini_menu
        )

        # Menu
        self.mini_menu = ctk.CTkFrame(
            self,
            width=130,
            height=90,
            corner_radius=10,
            fg_color="#202225"
        )

        self.maximize_btn = ctk.CTkButton(
            self.mini_menu,
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

        self.mini_stop_btn = ctk.CTkButton(
            self.mini_menu,
            text="🔴 OFF",
            height=30,
            corner_radius=7,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
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

        for widget in [
            self,
            self.container,
            self.header,
            self.title,
            self.mini_frame,
            self.mini_brain
        ]:
            widget.bind(
                "<Button-1>",
                self.start_move
            )

            widget.bind(
                "<B1-Motion>",
                self.do_move
            )

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

    # ==================================================
    # MINIMIZE
    # ==================================================

    def minimize(self):

        if self.is_minimized:
            return
    
        self.is_minimized = True
    
        x = self.winfo_x()
        y = self.winfo_y()
    
        self.container.pack_forget()
    
        self.mini_frame.place(
            x=0,
            y=0
        )
    
        self.geometry(
            f"{self.mini_size}x{self.mini_size}+{x}+{y}"
        )
    
        self.hide_arrow()
    def restore(self):

        if not self.is_minimized:
            return
    
        self.close_mini_menu()
    
        self.is_minimized = False
    
        x = self.winfo_x()
        y = self.winfo_y()
    
        self.mini_frame.place_forget()
    
        self.geometry(
            f"190x135+{x}+{y}"
        )
    
        self.container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

    def show_arrow(self, event=None):

        if not self.is_minimized:
            return
    
        self.arrow_button.place(
            x=30,
            y=8
        )
    
        self.arrow_button.lift()
    def hide_arrow_later(self, event=None):

        if self.mini_menu.winfo_ismapped():
            return

        self.after(
            500,
            self.hide_arrow
        )

    def hide_arrow(self):

        try:
            self.arrow_button.place_forget()
        except Exception:
            pass

    # ==================================================
    # MINI MENU
    # ==================================================

    def show_mini_menu(self):

        if not self.is_minimized:
            return

        self.arrow_button.place_forget()

        self.mini_menu.place(
            x=-135,
            y=0
        )
        self.mini_menu.lift()

    def close_mini_menu(self):

        try:
            self.mini_menu.place_forget()
        except Exception:
            pass

    # ==================================================
    # UPDATE CURRENT APPLICATION
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

        self.stop_callback()

        app = self.master

        app.deiconify()
        app.lift()
        app.focus_force()

        self.destroy()

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
