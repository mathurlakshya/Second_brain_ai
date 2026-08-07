import customtkinter as ctk
import sqlite3


class MemoryPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#111827")

        title = ctk.CTkLabel(
            self,
            text="🧠 Memory History",
            font=("Segoe UI", 28, "bold"),
            text_color="#F2F6FF"
        )
        title.pack(pady=(20,10))

        self.refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Refresh",
            command=self.load_memories,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        self.refresh_btn.pack(pady=(0,15))

        self.memory_box = ctk.CTkTextbox(
            self,
            height=500
        )

        self.memory_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.load_memories()

    def load_memories(self):

        self.memory_box.delete("1.0","end")

        conn = sqlite3.connect("second_brain.db")

        cursor = conn.cursor()

        cursor.execute("""
        SELECT timestamp,
               app_name,
               window_title
        FROM memories
        ORDER BY id DESC
        LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()

        if not rows:

            self.memory_box.insert(
                "end",
                "No memories recorded yet."
            )

            return

        for timestamp, app, title in rows:

            self.memory_box.insert(
                "end",
                f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕒 {timestamp}

💻 {app}

📄 {title}

"""
            )