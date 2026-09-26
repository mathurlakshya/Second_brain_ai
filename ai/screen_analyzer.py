from ai.gemini import analyze_screen as _analyze_screen


def analyze_screen(image_path):
    """Cloud screen analysis on explicit user request.

    This module is intentionally not used by the memory recorder. Recording,
    OCR, storage and search remain local; Gemini is only an on-demand
    intelligence feature.
    """
    return _analyze_screen(image_path)
