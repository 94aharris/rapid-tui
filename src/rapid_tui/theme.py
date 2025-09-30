"""Centralized theme configuration for RAPID TUI."""

from dataclasses import dataclass


@dataclass
class Theme:
    """Theme configuration for the application."""

    # Colors
    primary: str = "$primary"
    secondary: str = "$secondary"
    accent: str = "$accent"
    error: str = "$error"
    warning: str = "$warning"
    success: str = "$success"

    # Spacing
    spacing_small: int = 1
    spacing_medium: int = 2
    spacing_large: int = 4

    # Sizing
    container_width_small: int = 60
    container_width_medium: int = 70
    container_width_large: int = 80
    button_min_width: int = 16

    # Typography
    title_style: str = "bold"
    subtitle_style: str = "italic"

    def to_css_vars(self) -> str:
        """Convert theme to CSS variables."""
        return f"""
        :root {{
            --spacing-small: {self.spacing_small};
            --spacing-medium: {self.spacing_medium};
            --spacing-large: {self.spacing_large};
            --container-width-small: {self.container_width_small};
            --container-width-medium: {self.container_width_medium};
            --container-width-large: {self.container_width_large};
        }}
        """


# Default theme instance
default_theme = Theme()

# Dark theme variant
dark_theme = Theme(
    primary="cyan",
    secondary="blue",
    accent="green",
    error="red",
    warning="yellow",
    success="green",
)
