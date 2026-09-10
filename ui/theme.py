# Shared visual language for the Second Brain desktop UI.
# Colors are tuples: (light_mode, dark_mode). CustomTkinter automatically
# selects the correct value when the appearance mode changes.

import customtkinter as ctk

BG = ("#FFFFFF", "#05080F")
SURFACE = ("#FFFFFF", "#0B1220")
SURFACE_ALT = ("#F4F4F4", "#101A27")
BORDER = ("#D6D6D6", "#17212E")
BORDER_HOVER = ("#000000", "#243449")
TEXT = ("#000000", "#F4F7FB")
TEXT_MUTED = ("#000000", "#71849A")
TEXT_SOFT = ("#000000", "#8294A9")
TEXT_DIM = ("#000000", "#5F738C")
TEXT_BRIGHT = ("#000000", "#DCE8F5")
ACCENT = ("#000000", "#5BD7FF")
ACCENT_HOVER = ("#222222", "#26374B")
SUCCESS = ("#000000", "#6EE7A8")
WARNING = ("#000000", "#F6C76A")

FONT = "Segoe UI"

# Legacy pages still contain some explicit dark hex values. Map those values
# to the shared light/dark palette when the appearance mode changes.
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
    "#1788B5": ("#222222", "#1788B5"),
    "#161B22": SURFACE,
    "#172536": BORDER,
    "#A9B7C7": TEXT,
    "#DC2626": ("#000000", "#DC2626"),
    "#B91C1C": ("#222222", "#B91C1C"),
}


def _theme_color(value):
    if isinstance(value, str):
        return LEGACY_PALETTE.get(value.upper()) or LEGACY_PALETTE.get(value)
    return None


def refresh_theme(root):
    """Apply the light/dark palette to existing widgets immediately."""
    light_mode = ctk.get_appearance_mode().lower() == "light"

    def walk(widget):
        try:
            # First convert legacy explicit colors to theme tuples.
            for option in (
                "fg_color",
                "text_color",
                "border_color",
                "hover_color",
                "button_color",
                "button_hover_color",
                "progress_color",
                "placeholder_text_color",
                "scrollbar_fg_color",
                "scrollbar_button_color",
                "scrollbar_button_hover_color",
                "dropdown_fg_color",
                "dropdown_hover_color",
                "dropdown_text_color",
            ):
                try:
                    current = widget.cget(option)
                    themed = _theme_color(current)
                    if themed is not None:
                        widget.configure(**{option: themed})
                except (AttributeError, TypeError, ValueError):
                    pass

            # Light mode is intentionally high-contrast: white surfaces,
            # black text, and black controls/scrollbars.
            if light_mode:
                if isinstance(widget, ctk.CTkButton):
                    try:
                        widget.configure(
                            fg_color="#000000",
                            hover_color="#222222",
                            text_color="#FFFFFF",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkOptionMenu):
                    try:
                        widget.configure(
                            fg_color="#000000",
                            button_color="#000000",
                            button_hover_color="#222222",
                            text_color="#FFFFFF",
                            dropdown_fg_color="#FFFFFF",
                            dropdown_hover_color="#EEEEEE",
                            dropdown_text_color="#000000",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkScrollbar):
                    try:
                        widget.configure(
                            fg_color="#FFFFFF",
                            button_color="#000000",
                            button_hover_color="#333333",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkSwitch):
                    try:
                        widget.configure(
                            text_color="#000000",
                            progress_color="#000000",
                            button_color="#FFFFFF",
                            button_hover_color="#DDDDDD",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkEntry):
                    try:
                        widget.configure(
                            text_color="#000000",
                            placeholder_text_color="#000000",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkTextbox):
                    try:
                        widget.configure(
                            text_color="#000000",
                            scrollbar_button_color="#000000",
                            scrollbar_button_hover_color="#333333",
                        )
                    except Exception:
                        pass

                elif isinstance(widget, ctk.CTkLabel):
                    try:
                        widget.configure(text_color="#000000")
                    except Exception:
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
