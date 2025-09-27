import tkinter as tk
from tkinter import ttk, messagebox

class SearchFilterTab:
    def __init__(self, parent, app):
        """
        parent: Frame where this tab is displayed
        app: reference to main application
        """
        self.parent = parent
        self.app = app

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create search and filter UI."""
        tk.Label(
            self.parent,
            text="Search & Filter Dataset",
            font=("Arial", 14, "bold"),
            fg="#2C3E50"
        ).pack(pady=10)

        # Search Entry
        search_frame = tk.Frame(self.parent)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search Item:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            search_frame,text="🔍 Search",font=("Arial", 11, "bold"),bg="#3498DB",fg="white",
            command=self.search_dataset
        ).pack(side=tk.LEFT, padx=5)

        # ✅ Reset Button
        tk.Button(
            search_frame,
            text="🔄 Reset",
            font=("Arial", 11, "bold"),
            bg="#E67E22",
            fg="white",
            command=self.reset_table
        ).pack(side=tk.LEFT, padx=5)

        # Results Table
        self.tree = ttk.Treeview(self.parent)
        self.tree.pack(fill="both", expand=True, pady=10)

    def search_dataset(self):
        """Filter dataset based on search text."""
        if self.app.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset in the Analysis tab first.")
            return

        search_text = self.search_entry.get().strip().lower()
        if not search_text:
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return

        # Clear old results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Define table columns
        self.tree["columns"] = list(self.app.dataset.columns)
        self.tree["show"] = "headings"
        for col in self.app.dataset.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        # ✅ FIXED filtering logic
        filtered_df = self.app.dataset[
            self.app.dataset.apply(
                lambda row: search_text in " ".join(map(str, row.values)).lower(),
                axis=1
            )
        ]

        # Insert filtered results
        for _, row in filtered_df.iterrows():
            self.tree.insert("", "end", values=list(row))

        if filtered_df.empty:
            messagebox.showinfo("No Results", "No matching items found.")

    def reset_table(self):
        """Show the full dataset again."""
        if self.app.dataset is None:
            return

        # Clear old results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Define table columns
        self.tree["columns"] = list(self.app.dataset.columns)
        self.tree["show"] = "headings"
        for col in self.app.dataset.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        # Insert all rows
        for _, row in self.app.dataset.iterrows():
            self.tree.insert("", "end", values=list(row))

        # Clear search box
        self.search_entry.delete(0, tk.END)

    # ✅ helper: return current search text
    def get_search_text(self):
        return self.search_entry.get().strip()
