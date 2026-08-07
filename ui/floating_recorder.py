import customtkinter as ctk


class FloatingRecorder(ctk.CTkToplevel):

    def __init__(self, parent, stop_callback):

        super().__init__(parent)

        self.stop_callback = stop_callback

        screen_width = self.winfo_screenwidth()

        x = screen_width - 220
        y = 40

        self.geometry(f"190x135+{x}+{y}")

        self.overrideredirect(True)

        self.attributes("-topmost", True)

        self.configure(fg_color="#202225")

        container = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        container.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

        title = ctk.CTkLabel(
            container,
            text="🧠 REC",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(8,2))

        self.status = ctk.CTkLabel(
            container,
            text="🟢 Recording",
            font=("Segoe UI", 11)
        )
        self.status.pack()

        self.current_app = ctk.CTkLabel(
            container,
            text="Waiting...",
            font=("Segoe UI", 10),
            wraplength=160
        )
        self.current_app.pack(pady=(2,6))

        stop_btn = ctk.CTkButton(
            container,
            text="⏹ OFF",
            width=90,
            height=28,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white",
            corner_radius=8,
            command=self.stop
        )
        stop_btn.pack(pady=(0,8))
    def update_app(self, app, title):

        text = f"{app}\n{title[:30]}"

        self.current_app.configure(
            text=text
        )

    def stop(self):

        self.stop_callback()

        app = self.master

        app.deiconify()   # Show the main window if it was hidden

        app.lift()        # Bring it to the front

        app.focus_force() # Give it focus

        self.destroy()