import tkinter as tk
from tkinter import messagebox, ttk


class ReportsTab:
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
        """Create the UI for Reports Tab."""
        tk.Label(
            self.parent,
            text="Reports Tab",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Button to show dataset preview
        tk.Button(
            self.parent,
            text="📄 Show Dataset Preview",
            font=("Arial", 12, "bold"),
            bg="#8E44AD",
            fg="white",
            command=self.show_dataset_preview
        ).pack(pady=20)

        # Button to show dataset statistics
        tk.Button(
            self.parent,
            text="📊 Show Dataset Statistics",
            font=("Arial", 12, "bold"),
            bg="#16A085",
            fg="white",
            command=self.show_dataset_statistics
        ).pack(pady=10)

    def show_dataset_preview(self):
        """Display first 20 rows of dataset in a table."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        preview_win = tk.Toplevel(self.parent)
        preview_win.title("Dataset Preview")

        tree = ttk.Treeview(preview_win)
        tree.pack(fill="both", expand=True)

        # Define columns
        tree["columns"] = list(self.app.dataset.columns)
        tree["show"] = "headings"

        for col in self.app.dataset.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Insert first 20 rows
        for _, row in self.app.dataset.head(20).iterrows():
            tree.insert("", "end", values=list(row))

    def show_dataset_statistics(self):
        """Display basic statistics of the dataset."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        stats_win = tk.Toplevel(self.parent)
        stats_win.title("Dataset Statistics")

        stats_text = tk.Text(stats_win, wrap="word", width=80, height=20)
        stats_text.pack(padx=10, pady=10)

        stats_text.insert("end", str(self.app.dataset.describe(include="all")))
        stats_text.config(state="disabled")
# Reports tab module placeholder
