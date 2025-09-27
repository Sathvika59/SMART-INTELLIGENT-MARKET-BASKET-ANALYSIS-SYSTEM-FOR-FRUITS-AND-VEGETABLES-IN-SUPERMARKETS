import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import calendar
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# App utilities (assumed to exist in your project structure)
from app.utils.apriori_engine import run_apriori, preprocess_for_apriori  # noqa: F401
from app.utils.chart_utils import (
    plot_top_items,
    plot_support_confidence,
    plot_seasonal_sales_trends,
    plot_category_share,
)
from app.modules.db_utils import save_to_mysql


class Dashboard:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.dataset = None
        self.rules_df = None
        self.itemsets_df = None

        # Controls / state
        self.category_filter_var = tk.StringVar(value="Both")
        self.search_var = tk.StringVar()
        self.month_var = tk.StringVar()

        # Search/export state
        self.last_search_term = None
        self.last_filtered_rules = None

        self.create_ui()

    # -------------------------
    # UI
    # -------------------------
    def create_ui(self):
        self.root.title("Smart Market Basket Analyzer - Dashboard")
        try:
            self.root.state("zoomed")
        except Exception:
            # On some platforms zoomed may not exist; ignore
            pass

        # Toolbar
        toolbar = tk.Frame(self.root, bg="#2C3E50", height=50)
        toolbar.pack(fill="x")

        # Load dataset button
        self.load_btn = tk.Button(
            toolbar,
            text="📂 Load Dataset",
            bg="#3498DB",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.load_dataset,
        )
        self.load_btn.pack(side="left", padx=5, pady=5)

        # Category Filter Dropdown
        tk.Label(
            toolbar,
            text="Category:",
            fg="white",
            bg="#2C3E50",
            font=("Arial", 11, "bold"),
        ).pack(side="left", padx=5)

        category_dropdown = ttk.Combobox(
            toolbar, textvariable=self.category_filter_var, state="readonly", width=12
        )
        category_dropdown["values"] = ("Fruits", "Vegetables", "Both")
        category_dropdown.pack(side="left", padx=5)
        category_dropdown.current(2)  # Default = Both
        category_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_rules())

        # Search controls
        tk.Label(
            toolbar, text="Search Item:", fg="white", bg="#2C3E50", font=("Arial", 11, "bold")
        ).pack(side="left")
        tk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side="left", padx=5)
        self.search_btn = tk.Button(
            toolbar,
            text="🔍 Search",
            bg="#27AE60",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.search_item,
        )
        self.search_btn.pack(side="left", padx=5, pady=5)

        # Visualize button
        self.visualize_btn = tk.Button(
            toolbar,
            text="📊 Visualize",
            bg="#F39C12",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.show_visualizations,
        )
        self.visualize_btn.pack(side="left", padx=5, pady=5)

        # Export to MySQL
        self.mysql_export_btn = tk.Button(
            toolbar,
            text="📅 Export to MySQL",
            bg="#1ABC9C",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.export_to_mysql,
        )
        self.mysql_export_btn.pack(side="left", padx=5, pady=5)

        # Month Dropdown
        self.month_menu = ttk.Combobox(toolbar, textvariable=self.month_var, state="readonly", width=18)
        self.month_menu.pack(side="left", padx=5)
        self.month_menu.bind("<<ComboboxSelected>>", self.show_month_insights)

        # Clear month selection
        clear_btn = ttk.Button(toolbar, text="Reset", command=self.clear_month_selection)
        clear_btn.pack(side="left", padx=5)

        # Predict button
        self.predict_btn = tk.Button(
            toolbar,
            text="📈 Predict Next Month",
            bg="#8E44AD",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.predict_next_month,
        )
        self.predict_btn.pack(side="left", padx=5, pady=5)

        # Reset Dashboard button
        self.reset_btn = tk.Button(
            toolbar,
            text="🗑 Reset Dashboard",
            bg="#E74C3C",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.reset_dashboard,
        )
        self.reset_btn.pack(side="left", padx=5, pady=5)

        # Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.itemsets_frame = tk.Frame(self.notebook)
        self.rules_frame = tk.Frame(self.notebook)
        self.chart_frame = tk.Frame(self.notebook)  # Monthly insights chart

        self.notebook.add(self.itemsets_frame, text="Frequent Itemsets")
        self.notebook.add(self.rules_frame, text="Association Rules")
        self.notebook.add(self.chart_frame, text="Monthly Insights")

        # Tables
        self.itemsets_tree = ttk.Treeview(self.itemsets_frame)
        self.itemsets_tree.pack(fill="both", expand=True)

        self.rules_tree = ttk.Treeview(self.rules_frame)
        self.rules_tree.pack(fill="both", expand=True)
        self.add_threshold_controls()

        # Bottom Alert + Seasonal
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        self.alerts_frame = tk.LabelFrame(bottom_frame, text="🔔 Alerts", fg="red", font=("Arial", 12, "bold"))
        self.alerts_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.alerts_text = tk.Text(self.alerts_frame, height=8, wrap="word", state="disabled")
        self.alerts_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.seasonal_frame = tk.LabelFrame(
            bottom_frame, text="🌸 Seasonal Insights", fg="green", font=("Arial", 12, "bold")
        )
        self.seasonal_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.seasonal_text = tk.Text(self.seasonal_frame, height=8, wrap="word", state="disabled")
        self.seasonal_text.pack(fill="both", expand=True, padx=5, pady=5)

    def add_threshold_controls(self):
        """Add sliders for Support, Confidence, Lift thresholds."""
        control_frame = tk.Frame(self.rules_frame)
        control_frame.pack(fill="x", pady=5)

        # Support slider
        tk.Label(control_frame, text="Min Support").pack(side="left", padx=5)
        self.support_var = tk.DoubleVar(value=0.02)
        tk.Scale(
            control_frame,
            variable=self.support_var,
            from_=0.005,
            to=0.5,
            resolution=0.005,
            orient="horizontal",
            length=200,
            command=lambda e: self.update_rules(),
        ).pack(side="left", padx=5)

        # Confidence slider
        tk.Label(control_frame, text="Min Confidence").pack(side="left", padx=5)
        self.conf_var = tk.DoubleVar(value=0.4)
        tk.Scale(
            control_frame,
            variable=self.conf_var,
            from_=0.1,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            length=200,
            command=lambda e: self.update_rules(),
        ).pack(side="left", padx=5)

        # Lift slider
        tk.Label(control_frame, text="Min Lift").pack(side="left", padx=5)
        self.lift_var = tk.DoubleVar(value=0.9)
        tk.Scale(
            control_frame,
            variable=self.lift_var,
            from_=0.5,
            to=5.0,
            resolution=0.05,
            orient="horizontal",
            length=200,
            command=lambda e: self.update_rules(),
        ).pack(side="left", padx=5)

    # -------------------------
    # Data loading & Apriori
    # -------------------------
    def load_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Select Dataset CSV", filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return
        try:
            # Load CSV
            self.dataset = pd.read_csv(file_path)
            self.app.dataset = self.dataset

            # Ensure required columns
            required_cols = {"TransactionID", "Item", "Variety", "Category", "Date"}
            if not required_cols.issubset(self.dataset.columns):
                raise ValueError(
                    f"Dataset must contain columns: {', '.join(sorted(required_cols))}"
                )

            # Parse Date → Month (explicit format)
            self.dataset["Date"] = pd.to_datetime(self.dataset["Date"], format="%d-%m-%Y", errors="coerce")
            invalid_dates = self.dataset["Date"].isna().sum()
            self.dataset["Month"] = self.dataset["Date"].dt.strftime("%B")

            # Update Month Dropdown with placeholder first
            months_unique = self.dataset["Month"].dropna().unique()
            months_sorted = sorted(months_unique, key=lambda m: pd.to_datetime(m, format="%B"))
            months_sorted.insert(0, "-- Select Month --")
            self.month_menu["values"] = months_sorted
            self.month_menu.current(0)

            # Run Apriori + Alerts + Seasonal Insights (use sliders)
            self.run_apriori_analysis(
                min_support=self.support_var.get(),
                min_confidence=self.conf_var.get(),
                min_lift=self.lift_var.get(),
            )
            self.generate_alerts()
            self.show_seasonal_insights()

            # Success Message
            extra = (
                f" (Note: {invalid_dates} rows had invalid dates and were skipped)"
                if invalid_dates
                else ""
            )
            messagebox.showinfo(
                "Dataset Loaded", f"Loaded {len(self.dataset)} records successfully!{extra}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {e}")

    def run_apriori_analysis(self, min_support=None, min_confidence=None, min_lift=None):
        if self.dataset is None or self.dataset.empty:
            messagebox.showwarning(
                "Warning", "No dataset loaded. Please upload or generate data first."
            )
            return

        # Use slider values if provided, else current slider defaults
        min_support = min_support if min_support is not None else self.support_var.get()
        min_confidence = min_confidence if min_confidence is not None else self.conf_var.get()
        min_lift = min_lift if min_lift is not None else self.lift_var.get()

        try:
            # Pass current month as season hint
            current_month_name = calendar.month_name[pd.Timestamp.today().month]
            self.itemsets_df, self.rules_df = run_apriori(
                self.dataset,
                category_mode=self.category_filter_var.get(),
                min_support=min_support,
                min_confidence=min_confidence,
                min_lift=min_lift,
                current_season=current_month_name,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run Apriori: {e}")
            return

        if self.itemsets_df is None:
            self.itemsets_df = pd.DataFrame()
        if self.rules_df is None:
            self.rules_df = pd.DataFrame()

        if self.itemsets_df.empty or self.rules_df.empty:
            messagebox.showinfo(
                "No Results",
                "No frequent itemsets or rules found with the given thresholds.",
            )
            # Refresh empty tables
            self.display_table(self.itemsets_tree, self.itemsets_df)
            self.display_table(self.rules_tree, self.rules_df)
            return

        # Normalize antecedents/consequents to sets and build explanations
        self.rules_df = self.rules_df.copy()
        self.rules_df["antecedents"] = self.rules_df["antecedents"].apply(
            lambda x: set(x) if not isinstance(x, set) else x
        )
        self.rules_df["consequents"] = self.rules_df["consequents"].apply(
            lambda x: set(x) if not isinstance(x, set) else x
        )

        # Compute F1 for each rule (precision already = confidence)
        transactions = self._transactions_as_sets()
        n_transactions = len(transactions) if transactions else 1

        # Precompute support for consequents
        def support_of_itemset(itemset):
            if not itemset:
                return 0.0
            count = sum(1 for t in transactions if itemset.issubset(t))
            return count / n_transactions

        supports_cache = {}

        f1_list = []
        for _, r in self.rules_df.iterrows():
            prec = float(r.get("confidence", 0.0))
            sup_xy = float(r.get("support", 0.0))
            cons = r["consequents"] if isinstance(r["consequents"], set) else set(r["consequents"])
            key = tuple(sorted(cons))
            if key in supports_cache:
                sup_y = supports_cache[key]
            else:
                sup_y = support_of_itemset(cons)
                supports_cache[key] = sup_y
            rec = sup_xy / sup_y if sup_y > 0 else 0.0
            if prec + rec > 0:
                f1 = 2 * (prec * rec) / (prec + rec)
            else:
                f1 = 0.0
            f1_list.append(f1)

        self.rules_df["F1"] = f1_list

        def make_expl(r):
            return (
                "Customers who buy {antecedents} also buy {consequents} ({confidence}% likelihood)".format(
                    antecedents=", ".join(map(str, r["antecedents"])),
                    consequents=", ".join(map(str, r["consequents"])),
                    confidence=f"{r['confidence'] * 100:.1f}",
                )
            )

        self.rules_df["Explanation"] = self.rules_df.apply(make_expl, axis=1)

        # Display results (include F1)
        cols = ["antecedents", "consequents", "support", "confidence", "lift", "F1", "Explanation"]

        self.display_table(self.itemsets_tree, self.itemsets_df)
        self.display_table(self.rules_tree, self.rules_df[cols])

    def update_rules(self):
        """Re-run Apriori whenever sliders are adjusted"""
        self.run_apriori_analysis(
            min_support=self.support_var.get(),
            min_confidence=self.conf_var.get(),
            min_lift=self.lift_var.get(),
        )

    # -------------------------
    # Insights & Prediction
    # -------------------------
    def show_month_insights(self, event=None):
        month = self.month_var.get()

        # Skip placeholder
        if month == "-- Select Month --":
            messagebox.showinfo("No Selection", "Please select a valid month.")
            return

        if self.dataset is None:
            messagebox.showwarning("No Data", "Please load a dataset first.")
            return

        # Filter data for selected month
        month_data = self.dataset[self.dataset["Month"] == month]
        if month_data.empty:
            messagebox.showinfo("No Data", f"No transactions found for {month}")
            return

        # Apply category filter
        category = self.category_filter_var.get()
        if category.lower() == "fruits":
            month_data = month_data[
                month_data["Category"].str.lower().str.contains("fruit")
            ]
        elif category.lower() == "vegetables":
            month_data = month_data[
                month_data["Category"].str.lower().str.contains("vegetable")
            ]
        # "Both" → no further filtering

        if month_data.empty:
            messagebox.showinfo(
                "No Data", f"No transactions found for {category} in {month}"
            )
            return

        # Top 10 items
        item_counts = Counter(month_data["Item"]).most_common(10)
        items, counts = zip(*item_counts) if item_counts else ([], [])

        fig, ax = plt.subplots(figsize=(6, 4))
        if items:
            ax.bar(range(len(items)), counts)
            ax.set_title(f"Top 10 Selling Items in {month}")
            ax.set_ylabel("Quantity Sold")
            ax.set_xticks(range(len(items)))
            ax.set_xticklabels(items, rotation=45, ha="right")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")

        plt.tight_layout()

        # Clear old chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Display new chart
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_month_selection(self):
        """Reset dropdown to placeholder and clear chart."""
        if self.month_menu.cget("values"):
            self.month_menu.current(0)  # Reset to "-- Select Month --"
        for widget in self.chart_frame.winfo_children():
            widget.destroy()  # Clear chart area

    def predict_next_month(self):
        """Predict high demand items for the next month and plot inside Monthly Insights tab."""
        if self.dataset is None or self.dataset.empty:
            messagebox.showwarning("No Data", "Please load a dataset first.")
            return
        if not self.month_var.get() or self.month_var.get() == "-- Select Month --":
            messagebox.showwarning("Select Month", "Please select a month first.")
            return

        # Build months list in calendar order
        months = sorted(
            self.dataset["Month"].dropna().unique(), key=lambda m: pd.to_datetime(m, format="%B")
        )
        if not months:
            messagebox.showinfo("Prediction", "No month data available.")
            return

        selected_month = self.month_var.get()
        # Ensure selected month exists in months (robustness)
        if selected_month not in months:
            # Maybe user typed different casing; try to find a match by lowercase
            lower_map = {m.lower(): m for m in months}
            sel_lower = selected_month.lower()
            if sel_lower in lower_map:
                selected_month = lower_map[sel_lower]
            else:
                messagebox.showinfo("Prediction", f"Selected month '{self.month_var.get()}' is not available in dataset.")
                return

        try:
            current_month_index = months.index(selected_month)
        except ValueError:
            messagebox.showinfo("Prediction", f"Selected month '{selected_month}' not found in data.")
            return

        next_month = months[(current_month_index + 1) % len(months)]
        next_month_data = self.dataset[self.dataset["Month"] == next_month]

        # Apply category filter on prediction as well
        category = self.category_filter_var.get()
        if category.lower() == "fruits":
            next_month_data = next_month_data[
                next_month_data["Category"].str.lower().str.contains("fruit")
            ]
        elif category.lower() == "vegetables":
            next_month_data = next_month_data[
                next_month_data["Category"].str.lower().str.contains("vegetable")
            ]

        item_counts = Counter(next_month_data["Item"]).most_common(5)

        if not item_counts:
            messagebox.showinfo("Prediction", f"No data available for {next_month}.")
            return

        # --- Build the bar chart ---
        items, counts = zip(*item_counts)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(items, counts,color="orange", width=0.5)
        ax.set_title(f"Predicted High-Demand Items for {next_month}")
        ax.set_ylabel("Sales Count")
        ax.set_xlabel("Items")
        ax.set_xticklabels(items, rotation=45, ha="right")
        plt.tight_layout()

        # --- Display inside the Monthly Insights chart area (clear previous chart) ---
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Make Monthly Insights tab active so user sees the result
        try:
            idx = self.notebook.index(self.chart_frame)
            self.notebook.select(idx)
        except Exception:
            # If index lookup fails, ignore
            pass

    def reset_dashboard(self):
        """Clear all dashboard contents to allow fresh dataset loading."""
        # Clear dataset and rules
        self.dataset = None
        self.rules_df = None
        self.itemsets_df = None
        self.app.dataset = None

        # Clear tables
        self.display_table(self.itemsets_tree, pd.DataFrame())
        self.display_table(self.rules_tree, pd.DataFrame())

        # Clear Alerts
        self.alerts_text.config(state="normal")
        self.alerts_text.delete("1.0", "end")
        self.alerts_text.config(state="disabled")

        # Clear Seasonal Insights
        self.seasonal_text.config(state="normal")
        self.seasonal_text.delete("1.0", "end")
        self.seasonal_text.config(state="disabled")

        # Clear Monthly Insights chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Reset month dropdown
        self.month_menu["values"] = ["-- Select Month --"]
        self.month_menu.current(0)

        # Reset category dropdown
        self.category_filter_var.set("Both")

        # Clear search field
        self.search_var.set("")

        messagebox.showinfo("Dashboard Reset", "Dashboard has been cleared. You can now load another dataset.")

    # -------------------------
    # Search & Tables
    # -------------------------
    def search_item(self):
        if self.rules_df is None or self.rules_df.empty:
            messagebox.showwarning("No Rules", "Run Apriori first to get rules.")
            return

        search_term = (self.search_var.get() or "").strip().lower()

        # If no term, show all
        if not search_term:
            cols = ["antecedents", "consequents", "support", "confidence", "lift", "F1", "Explanation"]
            self.display_table(self.rules_tree, self.rules_df[cols])
            self.last_search_term = None
            self.last_filtered_rules = self.rules_df
            return

        # Normalize function → ignore variety for matching
        def normalize_item(item):
            if not isinstance(item, str):
                return ""
            return item.lower().split("-")[0].strip()

        # Filter rules where antecedents or consequents contain search term
        filtered_rules = self.rules_df[
            self.rules_df["antecedents"].apply(
                lambda ants: any(search_term in normalize_item(a) for a in ants)
            )
            |
            self.rules_df["consequents"].apply(
                lambda cons: any(search_term in normalize_item(c) for c in cons)
            )
        ]

        if filtered_rules.empty:
            messagebox.showinfo("No Matches", f"No rules found for '{search_term}'.")
            self.last_search_term = None
            self.last_filtered_rules = None
            return

        # Rebuild explanation with full Item + Variety names
        filtered_rules = filtered_rules.copy()
        filtered_rules["Explanation"] = filtered_rules.apply(
            lambda r: (
                "Customers who buy {antecedents} also buy {consequents} ({confidence}% likelihood)".format(
                    antecedents=", ".join(sorted(map(str, r["antecedents"]))),
                    consequents=", ".join(sorted(map(str, r["consequents"]))),
                    confidence=f"{r['confidence'] * 100:.1f}",
                )
            ),
            axis=1,
        )

        cols = ["antecedents", "consequents", "support", "confidence", "lift", "F1", "Explanation"]

        self.display_table(self.rules_tree, filtered_rules[cols])

        # Save filtered rules & term for export
        self.last_search_term = search_term
        self.last_filtered_rules = filtered_rules

    def display_table(self, tree, df: pd.DataFrame):
        tree.delete(*tree.get_children())
        cols = list(df.columns) if not df.empty else []
        tree["columns"] = cols
        tree["show"] = "headings"

        def format_value(val):
            if isinstance(val, (frozenset, set)):
                return ", ".join(sorted(list(val)))
            return val

        df2 = df.copy()
        for col in cols:
            df2[col] = df2[col].apply(format_value)

        for col in cols:
            tree.column(
                col,
                width=220 if col in ["antecedents", "consequents", "itemsets", "Explanation"] else 120,
                anchor="center",
            )
            tree.heading(col, text=col)
        for _, row in df2.iterrows():
            tree.insert("", "end", values=list(row))

    # -------------------------
    # Visualizations & Alerts
    # -------------------------
    def show_visualizations(self):
        if self.dataset is None:
            messagebox.showwarning("No Dataset", "Please load a dataset first.")
            return
        if "Item" in self.dataset.columns:
            plot_top_items(self.dataset["Item"].value_counts())
        if self.rules_df is not None and not self.rules_df.empty:
            plot_support_confidence(self.rules_df)
        plot_seasonal_sales_trends(self.dataset)
        plot_category_share(self.dataset)

    def generate_alerts(self):
        if self.dataset is None:
            return

        self.alerts_text.config(state="normal")
        self.alerts_text.delete("1.0", "end")

        # 🔹 Low sales alert
        if "Item" in self.dataset.columns and not self.dataset.empty:
            low_selling_item = self.dataset["Item"].value_counts().idxmin()
            self.alerts_text.insert(
                "end", f"- Low sales alert: {low_selling_item} is selling the least.\n"
            )

        # 🔹 Bundle Offer Alert
        if self.rules_df is not None and not self.rules_df.empty:
            # Pick top rule (by F1 if available, else first)
            if "F1" in self.rules_df.columns:
                top_rule = self.rules_df.sort_values("F1", ascending=False).iloc[0]
            elif "fuzzy_score" in self.rules_df.columns:
                top_rule = self.rules_df.sort_values("fuzzy_score", ascending=False).iloc[0]
            else:
                top_rule = self.rules_df.iloc[0]

            # Combine antecedents + consequents into one list
            bundle_items = sorted(list(top_rule["antecedents"]) + list(top_rule["consequents"]))
            bundle_text = " + ".join(map(str, bundle_items))

            # Confidence level interpretation
            conf = top_rule["confidence"]
            if conf >= 0.7:
                conf_text = "High Confidence"
            elif conf >= 0.5:
                conf_text = "Medium Confidence"
            else:
                conf_text = "Low Confidence"

            # Insert alert
            self.alerts_text.insert(
                "end",
                f"- Bundle Offer: {bundle_text} - {conf_text}\n"
            )

        self.alerts_text.config(state="disabled")

    def show_seasonal_insights(self):
        if self.dataset is None or self.dataset.empty:
            return
        if "Date" not in self.dataset.columns:
            self.seasonal_text.config(state="normal")
            self.seasonal_text.delete("1.0", "end")
            self.seasonal_text.insert("end", "No 'Date' column found for seasonal analysis.")
            self.seasonal_text.config(state="disabled")
            return
        # Parse dates using explicit format to avoid warnings
        self.dataset["Date"] = pd.to_datetime(self.dataset["Date"], format="%d-%m-%Y", errors="coerce")
        self.dataset["MonthNum"] = self.dataset["Date"].dt.month
        current_month = pd.Timestamp.today().month
        month_name = calendar.month_name[current_month]
        month_data = self.dataset[self.dataset["MonthNum"] == current_month]
        fruits = (
            month_data[month_data["Category"].str.lower() == "fruit"]["Item"].value_counts().head(3).index.tolist()
        )
        vegetables = (
            month_data[month_data["Category"].str.lower() == "vegetable"]["Item"].value_counts().head(3).index.tolist()
        )
        self.seasonal_text.config(state="normal")
        self.seasonal_text.delete("1.0", "end")
        self.seasonal_text.insert(
            "end", f"🗕 Suggested Fruits/Vegetables for {month_name}:\n"
        )
        self.seasonal_text.insert("end", "🍎 Fruits:\n")
        for fruit in fruits:
            self.seasonal_text.insert("end", f"   ➡ {fruit}\n")
        self.seasonal_text.insert("end", "🥕 Vegetables:\n")
        for veg in vegetables:
            self.seasonal_text.insert("end", f"   ➡ {veg}\n")
        self.seasonal_text.config(state="disabled")

    # =========================
    # Helper(s)
    # =========================
    def _transactions_as_sets(self):
        """Return list of transaction-item sets for evaluation."""
        if self.dataset is None:
            return []
        return list(self.dataset.groupby("TransactionID")["Item"].apply(set).tolist())

    # -------------------------
    # Export
    # -------------------------
    def export_to_mysql(self):
        if not hasattr(self, "last_filtered_rules") or self.last_filtered_rules is None or self.last_filtered_rules.empty:
            messagebox.showwarning("No Data", "Please search and filter rules first.")
            return

        # Save filtered rules
        success, msg = save_to_mysql(
            self.itemsets_df,
            self.last_filtered_rules,
            searched_item=self.last_search_term,
        )

        if success:
            messagebox.showinfo("Saved", msg)
        else:
            messagebox.showerror("Error", f"MySQL Save Failed: {msg}")
