import customtkinter as ctk
import sqlite3


class AnalyticsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#111827")

        title = ctk.CTkLabel(
            self,
            text="📊 Productivity Analytics",
            font=("Segoe UI",30,"bold"),
            text_color=("white")
        )

        title.pack(pady=(25,20))

        stats = ctk.CTkFrame(self)

        stats.pack(fill="x", padx=20)

        self.memories = self.create_card(
            stats,
            "🧠 Memories",
            0,
            0
        )

        self.apps = self.create_card(
            stats,
            "💻 Apps Used",
            0,
            1
        )

        self.latest = self.create_card(
            stats,
            "🕒 Latest",
            "-",
            2
        )

        self.refresh = ctk.CTkButton(
            self,
            text="Refresh Analytics",
            command=self.load_data,
            fg_color="#00CFFF",
            hover_color="#00A6FF",
            text_color="white"
        )

        self.refresh.pack(pady=20)

        self.box = ctk.CTkTextbox(
            self,
            height=450
        )

        self.box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.load_data()

    def create_card(self,parent,title,value,column):

        card = ctk.CTkFrame(parent,width=220,height=120)

        card.grid(row=0,column=column,padx=20)

        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI",18,"bold")
        ).pack(pady=(18,5))

        label = ctk.CTkLabel(
            card,
            text=str(value),
            font=("Segoe UI",26)
        )

        label.pack()

        return label

    def load_data(self):

        conn = sqlite3.connect("second_brain.db")

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM memories")

        total = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(DISTINCT app_name)
        FROM memories
        """)

        apps = cursor.fetchone()[0]

        cursor.execute("""
        SELECT timestamp
        FROM memories
        ORDER BY id DESC
        LIMIT 1
        """)

        latest = cursor.fetchone()

        conn.close()

        self.memories.configure(text=str(total))

        self.apps.configure(text=str(apps))

        self.latest.configure(
            text=latest[0][-8:] if latest else "-"
        )

        self.box.delete("1.0","end")

        self.box.insert(
            "end",
f"""
TODAY'S SUMMARY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Total Memories

{total}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 Applications Used

{apps}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕒 Latest Activity

{latest[0] if latest else "None"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        )
