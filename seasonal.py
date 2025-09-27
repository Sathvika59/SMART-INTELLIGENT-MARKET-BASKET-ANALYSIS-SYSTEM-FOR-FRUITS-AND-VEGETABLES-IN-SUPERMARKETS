import tkinter as tk
from tkinter import messagebox
import datetime


class SeasonalTab:
    def __init__(self, parent, app):
        """
        parent: the Frame where this tab is displayed
        app: reference to the main application (SmartMarketBasketApp)
        """
        self.parent = parent
        self.app = app

        # Seasonal mapping
        self.season_mapping = {
            "Summer": ["Mango", "Watermelon", "Muskmelon", "Cucumber"],
            "Winter": ["Apple", "Orange", "Guava", "Spinach", "Carrot", "Cauliflower"],
            "Rainy": ["Lychee", "Plum"],
            "All": ["Banana", "Tomato", "Onion", "Potato", "Brinjal", "Capsicum", "Papaya"]
        }

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the UI for Seasonal Recommendations."""
        tk.Label(
            self.parent,
            text="Seasonal Fruit & Vegetable Recommendations",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Button to show recommendations
        tk.Button(
            self.parent,
            text="🌱 Show Recommendations",
            font=("Arial", 12, "bold"),
            bg="#F39C12",
            fg="white",
            command=self.show_recommendations
        ).pack(pady=20)

        # Display area
        self.text_area = tk.Text(self.parent, wrap="word", height=15, width=60, state="disabled")
        self.text_area.pack(padx=10, pady=10)

    def show_recommendations(self):
        """Show seasonal recommendations based on current month."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        # Determine current month and season
        month = datetime.datetime.now().month
        if month in [3, 4, 5, 6]:
            season = "Summer"
        elif month in [11, 12, 1, 2]:
            season = "Winter"
        elif month in [7, 8, 9, 10]:
            season = "Rainy"
        else:
            season = "All"

        # Get recommendations
        recommended_items = self.season_mapping.get(season, [])
        all_time_items = self.season_mapping["All"]

        # Display
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", f"📅 Current Season: {season}\n\n")
        self.text_area.insert("end", "🌟 Recommended Items for this Season:\n")
        for item in recommended_items:
            self.text_area.insert("end", f"   • {item}\n")

        self.text_area.insert("end", "\n🍅 Items Available All Year:\n")
        for item in all_time_items:
            self.text_area.insert("end", f"   • {item}\n")

        self.text_area.config(state="disabled")
# Seasonal fruit tagging module placeholder
