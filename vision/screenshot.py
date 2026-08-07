import mss
import os
import datetime

SCREENSHOT_FOLDER = "screenshots"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


def capture_screen():

    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"

    filepath = os.path.join(SCREENSHOT_FOLDER, filename)

    with mss.mss() as sct:
        sct.shot(output=filepath)

    return filepath