from memory.recorder import get_active_window
from database.database import save_memory
import datetime
import time

while True:

    app, title = get_active_window()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_memory(app, title, now)

    print(app)
    print(title)
    print(now)

    print("-" * 50)

    time.sleep(5)