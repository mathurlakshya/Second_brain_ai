import datetime
import os

import mss

from config import SCREENSHOT_DIR

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def capture_screen():
    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    with mss.mss() as sct:
        sct.shot(output=filepath)
    return filepath
