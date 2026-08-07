import customtkinter as ctk
import threading
from ai.gemini import ask_jarvis


class ChatPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.build_ui()

    def build_ui(self):
        
        print("ChatPanel Loaded Successfully!")

        title = ctk.CTkLabel(
            self,
            text="💬 JARVIS ",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(10, 5))

        # Chat history
        self.chat_box = ctk.CTkTextbox(
            self,
            height=320,
            corner_radius=20,
            border_width=1
        )
        self.chat_box.configure(
            font=("Segoe UI", 15)
        )
        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.chat_box.insert(
            "end",
            "🧠 JARVIS:\nHello! I'm your AI assistant.\n\n"
        )

        self.chat_box.configure(state="disabled")

        # Bottom input frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask JARVIS anything..."
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 10),
            pady=10
        )

        self.entry.bind("<Return>", lambda event: self.send_message())

        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=100,
            command=self.send_message,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        send_btn.pack(
            side="right",
            padx=(0, 10),
            pady=10
        )

    def send_message(self):

        question = self.entry.get().strip()

        if question == "":
            return

        self.chat_box.configure(state="normal")

        self.chat_box.insert(
            "end",
            f"👤 You:\n{question}\n\n"
        )

        self.chat_box.insert(
            "end",
            "🧠 JARVIS is thinking...\n\n"
        )

        self.chat_box.see("end")

        self.chat_box.configure(state="disabled")

        self.entry.delete(0, "end")

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True
        ).start()

    def get_answer(self, question):

        answer = ask_jarvis(question)

        def update():

            self.chat_box.configure(state="normal")

            # Remove the "thinking" line
            content = self.chat_box.get("1.0", "end")
            content = content.replace("🧠 JARVIS is thinking...\n\n", "")

            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("1.0", content)

            self.chat_box.insert(
                "end",
                f"🧠 JARVIS:\n{answer}\n\n"
            )

            self.chat_box.see("end")

            self.chat_box.configure(state="disabled")

        self.after(0, update)