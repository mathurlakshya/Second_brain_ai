from vision.screenshot import capture_screen
from ai.gemini import analyze_screen
from services.app_state import AppState


class ContextManager:

    def update_context(self):

        image = capture_screen()

        summary = analyze_screen(image)

        AppState.latest_screenshot = image
        AppState.latest_summary = summary
        AppState.latest_context = {
            "image": image,
            "summary": summary
        }

        return summary