import customtkinter as ctk
import threading
from ai.gemini import ask_jarvis


def format_response(text):
    replacements = {
        "# Summary": "🧠 SUMMARY",
        "# Error": "❌ ERROR",
        "# Recommendation": "💡 RECOMMENDATION",
        "# Code": "💻 CODE",
        "# File": "📄 FILE",
        "# Commands": "⌨️ COMMANDS",
        "# Notes": "📝 NOTES",
        "# Important": "⚠ IMPORTANT",
        "##": "",
        "###": ""
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("**", "")

    text = text.replace(
        "```python",
        "\n────────────────────────────\n🐍 Python Code\n────────────────────────────\n"
    )

    text = text.replace(
        "```",
        "\n────────────────────────────\n"
    )

    return text


class ChatPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0
        )

        self.build_ui()

    def build_ui(self):
        print("ChatPanel Loaded Successfully!")

        # ---------- RESPONSE CANVAS ----------
        self.chat_box = ctk.CTkTextbox(
            self,
            height=320,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            text_color="#D6E0EB"
        )

        self.chat_box.configure(
            font=("Segoe UI Variable", 15),
            wrap="word"
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=(0, 14)
        )

        self.chat_box.insert(
            "end",
            """✦  Welcome back.

JARVIS is connected to your Second Brain.

Ask me about your memories, your current work,
or anything happening on your computer.

"""
        )

        self.chat_box.configure(state="disabled")

        # ---------- FLOATING COMMAND BAR ----------
        input_frame = ctk.CTkFrame(
            self,
            fg_color="#0B121C",
            corner_radius=14,
            border_width=1,
            border_color="#1B2A3B"
        )
        input_frame.pack(
            fill="x",
            pady=(0, 2)
        )

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask JARVIS anything...",
            height=44,
            fg_color="transparent",
            border_width=0,
            text_color="#EDF4FB",
            placeholder_text_color="#61758B",
            font=("Segoe UI", 13)
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(14, 6),
            pady=4
        )

        self.entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="➤",
            width=44,
            height=36,
            corner_radius=10,
            command=self.send_message,
            fg_color="#1C9ED1",
            hover_color="#1788B5",
            text_color="white",
            font=("Segoe UI", 15, "bold")
        )

        self.send_btn.pack(
            side="right",
            padx=(0, 5),
            pady=4
        )

    def send_message(self):
        question = self.entry.get().strip()

        if question == "":
            return

        self.chat_box.configure(state="normal")

        self.chat_box.insert(
            "end",
            f"\n\nYOU\n{question}\n\n"
        )

        self.chat_box.insert(
            "end",
            "JARVIS is thinking...\n"
        )

        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

        self.entry.delete(0, "end")

        self.send_btn.configure(state="disabled")

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True
        ).start()

    def get_answer(self, question):
        try:
            answer = ask_jarvis(question)
            answer = format_response(answer)

            print("=" * 50)
            print(answer)
            print("=" * 50)

        except Exception as e:
            answer = f"Sorry, I couldn't generate a response.\n\n{e}"

        def update():
            self.chat_box.configure(state="normal")

            content = self.chat_box.get("1.0", "end")

            content = content.replace(
                "JARVIS is thinking...\n",
                ""
            )

            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("1.0", content)

            self.chat_box.insert(
                "end",
                f"\nJARVIS\n{answer}\n"
            )

            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
            self.send_btn.configure(state="normal")
            self.entry.focus_set()

        self.after(0, update)
