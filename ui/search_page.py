import customtkinter as ctk

from ai.gemini import ask_memory_chat

class SearchPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#111827")



        title = ctk.CTkLabel(
            self,
            text="🧠 Memory Assistant",
            font=("Segoe UI", 30, "bold"),
            text_color="#9DB1C7"
        )

        title.pack(pady=(20,5))

        subtitle = ctk.CTkLabel(
            self,
            text="Ask JARVIS anything about your past work, coding sessions, files or browsing history.",
            font=("Segoe UI",15)
        )

        subtitle.pack(pady=(0,20))

        title.pack(pady=(25,10))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Search memories..."
        )

        self.entry.pack(
            fill="x",
            padx=30
        )

        self.entry.bind(
            "<Return>",
            lambda e:self.run_search()
        )

        button = ctk.CTkButton(
            self,
            text="Search",
            command=self.run_search,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        button.pack(pady=15)

        self.chat_box = ctk.CTkTextbox(
            self,
            font=("Segoe UI",15),
            corner_radius=15
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(10,15)
        )

        self.chat_box.insert(
            "end",
            "🤖 JARVIS\n\nHello! I remember your previous work.\n\nAsk me anything about your memories.\n\n"
        )
        input_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        input_frame.pack(
            fill="x",
            padx=20,
            pady=(0,20)
        )
        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask about your memories..."
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,10)
        )
        button = ctk.CTkButton(
            input_frame,
            text="➜",
            width=55,
            command=self.run_search,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        button.pack(
            side="right"
        )
    def run_search(self):

        question = self.entry.get().strip()

        if not question:
            return

        self.chat_box.insert(
            "end",
            f"\n👤 YOU\n\n{question}\n\n"
        )

        self.entry.delete(0, "end")

        self.chat_box.insert(
            "end",
            "🤖 JARVIS\n\nThinking...\n\n"
        )

        self.chat_box.see("end")

        answer = ask_memory_chat(question)

        self.chat_box.delete("end-3l", "end")

        self.chat_box.insert(
            "end",
            f"{answer}\n\n"
        )

        self.chat_box.insert(
            "end",
            "────────────────────────────────────────────\n\n"
        )

        self.chat_box.see("end")