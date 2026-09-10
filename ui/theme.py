# Shared visual language for the Second Brain desktop UI.
# Each color is (light, dark), which CustomTkinter switches automatically
# when ctk.set_appearance_mode("Light"/"Dark") is called.

BG = ("#F5F7FB", "#05080F")
SURFACE = ("#FFFFFF", "#0B1220")
SURFACE_ALT = ("#EEF2F7", "#101A27")
BORDER = ("#D7DEE8", "#17212E")
BORDER_HOVER = ("#B8C5D6", "#243449")
TEXT = ("#172033", "#F4F7FB")
TEXT_MUTED = ("#64748B", "#71849A")
TEXT_SOFT = ("#475569", "#8294A9")
TEXT_DIM = ("#64748B", "#5F738C")
TEXT_BRIGHT = ("#172033", "#DCE8F5")
ACCENT = ("#087EA4", "#5BD7FF")
ACCENT_HOVER = ("#DCEAF0", "#26374B")
SUCCESS = ("#16834B", "#6EE7A8")
WARNING = ("#A16207", "#F6C76A")

FONT = "Segoe UI"


def panel(parent, **kwargs):
    """Create a panel using the shared theme palette."""
    return kwargs.pop("widget", None) or None
