import json
import os
from pathlib import Path

class ThemeManager:
    def __init__(self):
        self.themes = {}
        self.current_theme = None
        self.theme_dir = Path(__file__).parent / "definitions"
        self.theme_dir.mkdir(exist_ok=True)
        self.load_themes()

    def load_themes(self):
        """Load all theme definitions from the themes directory."""
        for theme_file in self.theme_dir.glob("*.json"):
            try:
                with open(theme_file, "r") as f:
                    theme_data = json.load(f)
                    self.themes[theme_data["name"]] = theme_data
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")

    def get_theme(self, theme_name):
        """Get a specific theme by name."""
        return self.themes.get(theme_name)

    def get_theme_names(self):
        """Get list of available theme names."""
        return sorted(list(self.themes.keys()))

    def get_current_theme(self):
        """Get the current theme data."""
        return self.themes.get(self.current_theme)

    def set_current_theme(self, theme_name):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return self.themes[theme_name]
        return None

    def create_theme(self, theme_data):
        """Create a new theme."""
        if "name" not in theme_data:
            raise ValueError("Theme must have a name")
        
        theme_file = self.theme_dir / f"{theme_data['name'].lower().replace(' ', '_')}.json"
        with open(theme_file, "w") as f:
            json.dump(theme_data, f, indent=4)
        
        self.themes[theme_data["name"]] = theme_data
        return theme_data 