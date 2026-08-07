import customtkinter as ctk
import threading
import time

from vision.screenshot import capture_screen
from ai.gemini import (
    analyze_screen,
    ask_about_screen,
    save_context
)


class LiveContext(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#111827")

        self.build_ui()

    # ===================================================
    # UI
    # ===================================================

    def build_ui(self):

        # ---------- Header ----------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(fill="x", padx=20, pady=(20,10))

        title = ctk.CTkLabel(
            header,
            text="👁 Live Context",
            font=("Segoe UI",30,"bold"),
            text_color="#F2F6FF"
        )
        title.pack(side="left")

        self.status = ctk.CTkLabel(
            header,
            text="🟢 Ready",
            font=("Segoe UI",15)
        )
        self.status.pack(side="right")

        subtitle = ctk.CTkLabel(
            self,
            text="Analyze your current screen and chat with JARVIS about it.",
            font=("Segoe UI",15)
        )
        subtitle.pack(anchor="w", padx=22)

        # ---------- Main Area ----------

        body = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # ===================================================
        # LEFT PANEL
        # ===================================================

        left_panel = ctk.CTkFrame(
            body,
            corner_radius=15
        )

        left_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0,10)
        )

        left_title = ctk.CTkLabel(
            left_panel,
            text="📷 Current Screen",
            font=("Segoe UI",22,"bold")
        )

        left_title.pack(
            anchor="w",
            padx=20,
            pady=(18,10)
        )

        self.analysis_box = ctk.CTkTextbox(
            left_panel,
            font=("Consolas",14)
        )

        self.analysis_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0,20)
        )

        self.analysis_box.insert(
            "end",
            "Click 'Analyze Current Screen' to let JARVIS understand your desktop."
        )

        # ===================================================
        # RIGHT PANEL
        # ===================================================

        right_panel = ctk.CTkFrame(
            body,
            corner_radius=15
        )

        right_panel.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        right_title = ctk.CTkLabel(
            right_panel,
            text="💬 Chat with Current Screen",
            font=("Segoe UI",22,"bold")
        )

        right_title.pack(
            anchor="w",
            padx=20,
            pady=(18,10)
        )

        self.chat_box = ctk.CTkTextbox(
            right_panel,
            font=("Segoe UI",14)
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0,15)
        )

        self.chat_box.insert(
            "end",
            "🤖 JARVIS\n\n"
            "Analyze your screen first.\n"
            "Then ask unlimited questions about it.\n\n"
        )

        # ===================================================
        # Bottom Controls
        # ===================================================

        controls = ctk.CTkFrame(
            self,
            height=90,
            corner_radius=15
        )

        controls.pack(
            fill="x",
            padx=20,
            pady=(0,20)
        )

        self.refresh_btn = ctk.CTkButton(
            controls,
            text="📸 Analyze Current Screen",
            width=220,
            height=45,
            command=self.refresh_context,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        self.refresh_btn.pack(
            side="left",
            padx=20,
            pady=20
        )

        self.question_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Ask anything about this screen...",
            height=45
        )

        self.question_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,15),
            pady=20
        )

        self.ask_btn = ctk.CTkButton(
            controls,
            text="Send ➜",
            width=120,
            height=45,
            command=self.ask_screen_question,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        self.ask_btn.pack(
            side="right",
            padx=20,
            pady=20
        )

        # ===================================================
    # ANALYZE SCREEN
    # ===================================================

    def refresh_context(self):

        self.status.configure(
            text="🟡 Capturing Screen..."
        )

        self.analysis_box.delete("1.0", "end")

        self.analysis_box.insert(
            "end",
            "📸 Capturing your desktop...\n\n"
            "Please wait..."
        )

        threading.Thread(
            target=self.run_analysis,
            daemon=True
        ).start()


    def run_analysis(self):

        app = self.winfo_toplevel()

        # Hide app
        self.after(0, app.withdraw)

        time.sleep(0.8)

        image_path = capture_screen()

        # Restore app
        self.after(0, app.deiconify)

        result = analyze_screen(image_path)

        save_context(result)

        self.after(
            0,
            lambda: self.show_analysis(result)
        )


    def show_analysis(self, result):

        self.status.configure(
            text="🟢 Screen Ready"
        )

        self.analysis_box.delete(
            "1.0",
            "end"
        )

        self.analysis_box.insert(
            "end",
            result
        )

        self.chat_box.insert(
            "end",
            "🤖 JARVIS\n\n"
            "Screen analyzed successfully.\n"
            "You can now ask me anything about it.\n\n"
        )

        self.chat_box.see("end")    

        # ===================================================
    # CHAT
    # ===================================================

    def ask_screen_question(self):

        question = self.question_entry.get().strip()

        if question == "":
            return

        self.question_entry.delete(0, "end")

        self.chat_box.insert(
            "end",
            f"👤 You\n{question}\n\n"
        )

        self.chat_box.insert(
            "end",
            "🤖 JARVIS is thinking...\n\n"
        )

        self.chat_box.see("end")

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True
        ).start()


    def get_answer(self, question):

        try:

            answer = ask_about_screen(question)

        except Exception as e:

            answer = str(e)

        self.after(
            0,
            lambda: self.show_answer(answer)
        )


    def show_answer(self, answer):

        content = self.chat_box.get("1.0", "end")

        if "🤖 JARVIS is thinking..." in content:

            content = content.replace(
                "🤖 JARVIS is thinking...\n\n",
                ""
            )

            self.chat_box.delete(
                "1.0",
                "end"
            )

            self.chat_box.insert(
                "end",
                content
            )

        self.chat_box.insert(
            "end",
            f"🤖 JARVIS\n{answer}\n\n"
        )

        self.chat_box.see("end")    