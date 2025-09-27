import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd


class AnalysisTab:
    def __init__(self, parent, app):
        """
        parent: the Frame where this tab is displayed
        app: reference to the main application (SmartMarketBasketApp)
        """
        self.parent = parent
        self.app = app
        self.dataset_loaded = False

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the UI for Analysis Tab."""
        tk.Label(
            self.parent,
            text="Analysis Tab - Load Dataset to Begin",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Button to load dataset
        tk.Button(
            self.parent,
            text="📂 Load Dataset",
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            command=self.load_dataset
        ).pack(pady=20)

        # Info label
        self.info_label = tk.Label(self.parent, text="", font=("Arial", 11), fg="#34495E")
        self.info_label.pack(pady=5)

    def load_dataset(self):
        """Prompt user to select dataset CSV file manually."""
        file_path = filedialog.askopenfilename(
            title="Select Dataset CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                self.app.dataset = pd.read_csv(file_path)
                self.dataset_loaded = True
                msg = f"✅ Loaded {len(self.app.dataset)} records successfully!"
                self.info_label.config(text=msg, fg="green")
                messagebox.showinfo("Dataset Loaded", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load dataset: {e}")
        else:
            messagebox.showwarning("No File Selected", "Please select a dataset to proceed.")
