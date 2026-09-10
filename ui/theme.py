# Shared visual language for the Second Brain desktop UI.
# Keep these values aligned with the Dashboard so every page feels like one app.

BG = "#05080F"
SURFACE = "#0B1220"
SURFACE_ALT = "#101A27"
BORDER = "#17212E"
BORDER_HOVER = "#243449"
TEXT = "#F4F7FB"
TEXT_MUTED = "#71849A"
TEXT_SOFT = "#8294A9"
TEXT_DIM = "#5F738C"
TEXT_BRIGHT = "#DCE8F5"
ACCENT = "#5BD7FF"
ACCENT_HOVER = "#26374B"
SUCCESS = "#6EE7A8"
WARNING = "#F6C76A"

FONT = "Segoe UI"


def panel(parent, **kwargs):
    """Create a panel using the dashboard's dark surface style."""
    return kwargs.pop("widget", None) or None
