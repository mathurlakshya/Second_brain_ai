# Shared visual language for the Second Brain desktop UI.
# Each color is (light, dark), which CustomTkinter switches automatically
# when ctk.set_appearance_mode("Light"/"Dark") is called.

import customtkinter as ctk

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

# Legacy pages contain a few explicit hex colors. Mapping them to theme tuples
# lets those widgets follow the Light/Dark switch without rebuilding the UI.
LEGACY_PALETTE = {
    "#05080F": BG,
    "#0B1220": SURFACE,
    "#101A27": SURFACE_ALT,
    "#17212E": BORDER,
    "#243449": BORDER_HOVER,
    "#F4F7FB": TEXT,
    "#7F91A8": TEXT_MUTED,
    "#71849A": TEXT_MUTED,
    "#8294A9": TEXT_SOFT,
    "#5F738C": TEXT_DIM,
    "#DCE8F5": TEXT_BRIGHT,
    "#C7D3E0": TEXT_BRIGHT,
    "#D6E0EB": TEXT_SOFT,
    "#EDF4FB": TEXT,
    "#61758B": TEXT_MUTED,
    "#0B121C": SURFACE,
    "#1B2A3B": BORDER,
    "#182332": SURFACE_ALT,
    "#26374B": ACCENT_HOVER,
    "#111B27": BORDER,
    "#1C9ED1": ACCENT,
    "#1788B5": ("#066B8A", "#1788B5"),
}


def _theme_color(value):
    if isinstance(value, str):
        return LEGACY_PALETTE.get(value.upper()) or LEGACY_PALETTE.get(value)
    return None


def refresh_theme(root):
    """Refresh explicit legacy colors after an appearance-mode change."""
    def walk(widget):
        try:
            for option in (
                "fg_color",
                "text_color",
                "border_color",
                "hover_color",
                "button_color",
                "button_hover_color",
                "progress_color",
                "placeholder_text_color",
                "scrollbar_button_color",
                "scrollbar_button_hover_color",
            ):
                try:
                    current = widget.cget(option)
                    themed = _theme_color(current)
                    if themed is not None:
                        widget.configure(**{option: themed})
                except (AttributeError, TypeError, ValueError):
                    pass
        except Exception:
            pass

        try:
            for child in widget.winfo_children():
                walk(child)
        except Exception:
            pass

    walk(root)


def panel(parent, **kwargs):
    """Create a panel using the shared theme palette."""
    return kwargs.pop("widget", None) or None
