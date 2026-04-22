"""
Theme manager for light/dark mode switching
"""
import json
import os
from app.config import UIConfig


class ThemeManager:
    """Manages application theme (light/dark) with persistence"""
    
    THEME_FILE = os.path.join(os.path.expanduser("~"), ".retailman_theme.json")
    
    def __init__(self):
        self.current_theme = self.load_theme()
        self.callbacks = []  # Callbacks to notify when theme changes
    
    def load_theme(self) -> str:
        """Load theme from file, default to dark"""
        try:
            if os.path.exists(self.THEME_FILE):
                with open(self.THEME_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get("theme", "dark")
        except Exception:
            pass
        return "dark"
    
    def save_theme(self, theme: str):
        """Save theme to file"""
        try:
            with open(self.THEME_FILE, 'w') as f:
                json.dump({"theme": theme}, f)
        except Exception:
            pass
    
    def get_colors(self) -> dict:
        """Get color palette for current theme"""
        if self.current_theme == "dark":
            return UIConfig.DARK_COLORS
        else:
            return UIConfig.LIGHT_COLORS
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.save_theme(self.current_theme)
        self.notify_callbacks()
    
    def set_theme(self, theme: str):
        """Set specific theme"""
        if theme in ("dark", "light"):
            self.current_theme = theme
            self.save_theme(self.current_theme)
            self.notify_callbacks()
    
    def register_callback(self, callback):
        """Register callback to be notified on theme change"""
        self.callbacks.append(callback)
    
    def notify_callbacks(self):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(self.current_theme)
            except Exception:
                pass
    
    def is_dark(self) -> bool:
        """Check if current theme is dark"""
        return self.current_theme == "dark"


# Global theme manager instance
theme_manager = ThemeManager()
