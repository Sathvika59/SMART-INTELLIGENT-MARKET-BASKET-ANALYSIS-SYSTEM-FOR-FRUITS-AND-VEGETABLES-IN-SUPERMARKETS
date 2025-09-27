import tkinter as tk
from tkinter import messagebox


class AlertsTab:
    def __init__(self, parent, app):
        """
        parent: the Frame where this tab is displayed
        app: reference to the main application (SmartMarketBasketApp)
        """
        self.parent = parent
        self.app = app

        # Default threshold for low-selling items
        self.threshold = 10

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the UI for Alerts Tab."""
        tk.Label(
            self.parent,
            text="Low-Selling Item Alerts",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Threshold input
        tk.Label(self.parent, text="Low-selling threshold (sales count):", font=("Arial", 11)).pack(pady=5)
        self.threshold_entry = tk.Entry(self.parent, font=("Arial", 11))
        self.threshold_entry.insert(0, str(self.threshold))
        self.threshold_entry.pack(pady=5)

        # Button to generate alerts
        tk.Button(
            self.parent,
            text="⚠️ Generate Alerts",
            font=("Arial", 12, "bold"),
            bg="#E74C3C",
            fg="white",
            command=self.generate_alerts
        ).pack(pady=15)

        # Alerts display
        self.alerts_text = tk.Text(self.parent, wrap="word", height=15, width=60, state="disabled")
        self.alerts_text.pack(padx=10, pady=10)

    def generate_alerts(self):
        """Generate low-selling item alerts based on threshold."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        try:
            self.threshold = int(self.threshold_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for the threshold.")
            return

        # Count sales per item
        item_counts = self.app.dataset["Item"].value_counts()

        # Find low-selling items
        low_selling = item_counts[item_counts < self.threshold]

        # Display alerts
        self.alerts_text.config(state="normal")
        self.alerts_text.delete("1.0", "end")
        if low_selling.empty:
            self.alerts_text.insert("end", "✅ No low-selling items found.\n")
        else:
            for item, count in low_selling.items():
                self.alerts_text.insert("end", f"⚠️ {item} — only {count} sales\n")
        self.alerts_text.config(state="disabled")
# Alerts handling module placeholder
