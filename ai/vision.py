from ai.gemini import analyze_screen


def analyze_image(image_path):
    """Backward-compatible alias for explicit cloud screen analysis."""
    return analyze_screen(image_path)
