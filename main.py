import tkinter as tk
from app.modules.login import LoginPage
from app.modules.welcome import WelcomePage
from app.modules.dashboard import Dashboard


class SmartMarketBasketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Market Basket Analyzer")
        self.dataset = None  # Shared dataset for all features

        # Start with login page
        self.show_login_page()

    def show_login_page(self):
        """Display the login screen."""
        self.clear_window()
        LoginPage(self.root, self.show_welcome_page)

    def show_welcome_page(self):
        """After login, show welcome page."""
        self.clear_window()
        WelcomePage(self.root, self.show_dashboard)

    def show_dashboard(self):
        """Show the main dashboard for analysis."""
        self.clear_window()
        Dashboard(self.root, self)  # Pass reference to app so dashboard can access shared dataset

    def clear_window(self):
        """Remove all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = SmartMarketBasketApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
