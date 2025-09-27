import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector
from app.modules.register import RegisterPage


# ---------- MySQL Connection ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sathvika@123",
        database="mba_db"
    )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")


class LoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success

        self.root.state("zoomed")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Background
        image_path = os.path.join(ASSETS_DIR, "login.jpg")
        bg_image = Image.open(image_path)
        self.bg_image_tk = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(1600, 800))
        bg_label = ctk.CTkLabel(self.root, image=self.bg_image_tk, text="")
        bg_label.place(relwidth=1, relheight=1)

        # Frame
        frame = ctk.CTkFrame(self.root, width=500, height=400, corner_radius=20, fg_color="white")
        frame.place(relx=0.50, rely=0.55, anchor="center")
        frame.pack_propagate(False)

        # Title
        ctk.CTkLabel(frame, text="🔐 Smart Market Basket Analyzer",
                     font=("Courier New", 23, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(frame, text="Login",
                     font=("Arial", 20, "bold"), text_color="green").pack(pady=(0, 20))

        # --- Username field with icon ---
        uname_frame = ctk.CTkFrame(frame, fg_color="transparent")
        uname_frame.pack(pady=12)

        ctk.CTkLabel(uname_frame, text="👤", font=("Arial", 18)).pack(side="left", padx=(0, 8))
        self.username_entry = ctk.CTkEntry(uname_frame, placeholder_text="Username",
                                           width=320, height=40, font=("Arial", 14))
        self.username_entry.pack(side="left")

        # --- Password field with icon + eye toggle ---
        pw_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pw_frame.pack(pady=12)

        # Lock icon (left side)
        ctk.CTkLabel(pw_frame, text="🔒", font=("Arial", 18)).pack(side="left", padx=(0, 8))

        # Password entry (leave space for eye icon on right)
        self.password_entry = ctk.CTkEntry(pw_frame, placeholder_text="Password", show="*",
                                           width=320, height=40, font=("Arial", 14))
        self.password_entry.pack(side="left")

        # Overlay 👁 inside password box (absolute placement)
        self.show_pw = False
        self.eye_button = ctk.CTkButton(
            pw_frame, text="👁", width=25, height=25,
            fg_color="white", text_color="black",
            corner_radius=10,
            command=self.toggle_password
        )

        # Place it inside the entry (slightly shifted to the right side)
        self.eye_button.place(in_=self.password_entry, relx=0.92, rely=0.5, anchor="center")

        # --- Login button ---
        login_btn = ctk.CTkButton(frame, text="Login", width=220, height=40,
                                  font=("Arial", 15, "bold"),
                                  fg_color="#4CAF50", hover_color="#388E3C",
                                  command=self.check_login)
        login_btn.pack(pady=20)

        # --- Register button ---
        register_btn = ctk.CTkButton(frame,
                                     text="New user?     Register here",
                                     font=("Arial", 13, "underline"),
                                     fg_color="transparent",
                                     text_color="blue",
                                     hover=False,
                                     command=self.show_register)
        register_btn.pack(pady=(10, 20))

    def toggle_password(self):
        """Show/Hide password"""
        if self.show_pw:
            self.password_entry.configure(show="*")
            self.eye_button.configure(text="👁")
        else:
            self.password_entry.configure(show="")
            self.eye_button.configure(text="🙈")
        self.show_pw = not self.show_pw

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Login Successful", f"Welcome {username}!")
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_register(self):
        self.clear_window()
        RegisterPage(self.root, self.reload_login)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def reload_login(self):
        self.clear_window()
        LoginPage(self.root, self.on_login_success)
