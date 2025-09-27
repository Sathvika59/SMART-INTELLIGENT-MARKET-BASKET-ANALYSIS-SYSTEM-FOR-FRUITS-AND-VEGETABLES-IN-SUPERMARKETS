import tkinter as tk
from PIL import Image, ImageTk
import os

class WelcomePage:
    def __init__(self, root, on_continue):
        self.root = root
        self.on_continue = on_continue

        self.root.title("Welcome - Smart Market Basket Analyzer")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "welcom.jpg")

        self.original_bg = Image.open(image_path)
        self.bg_image = self.original_bg.resize((1600, 800))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # ✅ Canvas
        self.canvas = tk.Canvas(self.root, width=1600, height=900, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        self.canvas.image = self.bg_photo  # prevent garbage collection

        # -------------------------
        # Card 1: Title + Subtitle
        # -------------------------
        title_text = "Smart Market Basket Analysis System\nFor Fruits and Vegetables in Supermarkets"
        self._draw_card_with_text(
            850, 200,
            title_text,
            ("Arial", 26, "bold"),
            card_fill="#FFFFFF"
        )

        # -------------------------
        # Card 2: Tagline
        # -------------------------
        tagline = "Unlock Insights • Identify Trends • Boost Sales"
        self._draw_card_with_text(
            850, 360,
            tagline,
            ("Arial", 15, "italic", "bold"),
            card_fill="#FFFFFF",
            text_fill="purple"
        )

        # ✅ Continue Button
        btn = tk.Button(
            root,
            text="Continue →",
            font=("Arial", 14, "bold"),
            bg="#27AE60",
            fg="white",
            padx=30,
            pady=10,
            command=self.on_continue
        )
        self.canvas.create_window(850, 460, window=btn)

        # -------------------------
        # Metrics Cards in One Row
        # -------------------------
        metrics = [
            ("Support", "Indicates how frequently\nan itemset appears in the dataset.", "#FADBD8"),
            ("Confidence", "Measures how often items\nin Y appear in transactions containing X.", "#D5F5E3"),
            ("Lift", "Shows how much more likely\nitem Y is purchased with X than alone.", "#D6EAF8"),
            ("F1 Score","Combines precision and recall\nto balance accuracy measurement.", "#FDEBD0"),
        ]

        card_width = 280
        gap = 80
        total_width = len(metrics) * card_width + (len(metrics) - 1) * gap

        center_x = 800
        start_x = center_x - total_width // 2 + card_width // 2
        y_pos = 600

        for i, (title, desc, color) in enumerate(metrics):
            x_pos = start_x + i * (card_width + gap)
            self._draw_card_with_text(
                x_pos, y_pos,
                f"{title}\n{desc}",
                ("Arial", 12, "bold"),
                card_fill=color,
                text_fill="black"
            )

    def _create_rounded_rect(self, x1, y1, x2, y2, r=20, fill="#fff", shadow=True):
        """Draw rounded rectangle with optional shadow"""
        if shadow:
            self.canvas.create_rectangle(
                x1+5, y1+5, x2+5, y2+5,
                fill="#cccccc", outline="", width=0
            )

        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.canvas.create_polygon(
            points, smooth=True, splinesteps=100,
            fill=fill, outline=""
        )

    def _draw_card_with_text(self, x, y, text, font, card_fill="#FFFFFF", text_fill="black"):
        """Draw rounded card with centered text"""
        temp_text = self.canvas.create_text(x, y, text=text, font=font, justify="center")
        bbox = self.canvas.bbox(temp_text)
        self.canvas.delete(temp_text)

        if bbox:
            x1, y1, x2, y2 = bbox
            padding_x, padding_y = 15, 15

            # Rounded rectangle card with shadow
            self._create_rounded_rect(
                x1 - padding_x, y1 - padding_y,
                x2 + padding_x, y2 + padding_y,
                r=20, fill=card_fill, shadow=True
            )

            # Text
            self.canvas.create_text(x, y, text=text, font=font, fill=text_fill, justify="center")


if __name__ == "__main__":
    def go_next():
        print("Continue clicked!")

    root = tk.Tk()
    app = WelcomePage(root, go_next)
    root.mainloop()
