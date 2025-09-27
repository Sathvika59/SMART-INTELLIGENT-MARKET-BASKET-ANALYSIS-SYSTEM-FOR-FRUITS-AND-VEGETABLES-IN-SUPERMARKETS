import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt


class VisualizationsTab:
    def __init__(self, parent, app):
        """
        parent: the Frame where this tab is displayed
        app: reference to the main application (SmartMarketBasketApp)
        """
        self.parent = parent
        self.app = app

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the UI for Visualizations Tab."""
        tk.Label(
            self.parent,
            text="Visualizations Tab",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Button to show a sample chart
        tk.Button(
            self.parent,
            text="📊 Show Item Frequency Chart",
            font=("Arial", 12, "bold"),
            bg="#2980B9",
            fg="white",
            command=self.show_item_frequency
        ).pack(pady=20)

    def show_item_frequency(self):
        """Show a bar chart of item frequencies from the dataset."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        # Count frequency of each item
        item_counts = self.app.dataset["Item"].value_counts().head(10)

        # Plot chart
        plt.figure(figsize=(8, 5))
        item_counts.plot(kind="bar", color="skyblue")
        plt.title("Top 10 Items by Frequency")
        plt.xlabel("Item")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

