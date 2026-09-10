import customtkinter as ctk
import threading
from ai.gemini import ask_jarvis
from ui.theme import BG, SURFACE, SURFACE_ALT, BORDER, BORDER_HOVER, TEXT, TEXT_MUTED, TEXT_SOFT, TEXT_DIM, TEXT_BRIGHT, ACCENT, ACCENT_HOVER


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
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.thinking = False
        self.thinking_step = 0
        self.typing_after_id = None
        self.thinking_prefix = ""

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
            text_color=TEXT,
            font=("Segoe UI Variable", 15),
            wrap="word",
            scrollbar_button_color=TEXT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        self.chat_box.pack(fill="both", expand=True, padx=2, pady=(0, 14))

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
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        input_frame.pack(fill="x", pady=(0, 2))

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask JARVIS anything...",
            height=44,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT,
            placeholder_text_color=TEXT_MUTED,
            font=("Segoe UI", 13)
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(14, 6), pady=4)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="➤",
            width=44,
            height=36,
            corner_radius=10,
            command=self.send_message,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=SURFACE,
            font=("Segoe UI", 15, "bold")
        )
        self.send_btn.pack(side="right", padx=(0, 5), pady=4)

    def send_message(self):
        question = self.entry.get().strip()

        if not question or self.thinking:
            return

        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n\nYOU\n{question}\n\n")

        # Save everything before the thinking indicator. During the animation
        # we redraw this same content and replace only the single indicator line.
        # This guarantees that the thinking message never gets duplicated.
        self.thinking_prefix = self.chat_box.get("1.0", "end-1c")
        self.chat_box.insert("end", "✦ JARVIS is thinking")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")

        self.thinking = True
        self.thinking_step = 0
        self.animate_thinking()

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True
        ).start()

    def animate_thinking(self):
        """Keep one thinking line in place and subtly animate only its icon."""
        if not self.thinking:
            return

        # The text stays exactly in the same place. Only the small sparkle
        # changes between two glyphs, creating a gentle wave/pulse effect.
        pulse = ("✦", "✧")[self.thinking_step % 2]
        text = f"{pulse} JARVIS is thinking"

        try:
            self.chat_box.configure(state="normal")
            self.chat_box.delete("1.0", "end")
            self.chat_box.insert("1.0", self.thinking_prefix + text)
            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
        except Exception:
            return

        self.thinking_step += 1
        self.after(420, self.animate_thinking)

    def get_answer(self, question):
        try:
            answer = ask_jarvis(question)
            answer = format_response(answer)

            print("=" * 50)
            print(answer)
            print("=" * 50)

        except Exception as e:
            answer = f"Sorry, I couldn't generate a response.\n\n{e}"

        self.after(0, self.show_answer, answer)

    def show_answer(self, answer):
        """Replace the single thinking indicator and reveal the response progressively."""
        self.thinking = False

        if self.typing_after_id is not None:
            try:
                self.after_cancel(self.typing_after_id)
            except Exception:
                pass
            self.typing_after_id = None

        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.insert("1.0", self.thinking_prefix)
        self.chat_box.insert("end", "✦ JARVIS\n")
        self.chat_box.configure(state="disabled")

        self.type_response(answer, 0)

    def type_response(self, answer, index):
        """Professional chatbot-style type-on response animation."""
        if index >= len(answer):
            self.typing_after_id = None
            self.send_btn.configure(state="normal")
            self.entry.configure(state="normal")
            self.entry.focus_set()
            return

        # Add a few characters at once so long Gemini responses animate
        # smoothly without taking an excessive amount of time.
        chunk_size = 2 if len(answer) > 500 else 1
        next_index = min(index + chunk_size, len(answer))
        chunk = answer[index:next_index]

        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", chunk)
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

        # Slightly faster around spaces/newlines, giving a natural typing rhythm.
        delay = 14 if chunk.endswith((" ", "\n")) else 22
        self.typing_after_id = self.after(
            delay,
            lambda: self.type_response(answer, next_index)
        )
