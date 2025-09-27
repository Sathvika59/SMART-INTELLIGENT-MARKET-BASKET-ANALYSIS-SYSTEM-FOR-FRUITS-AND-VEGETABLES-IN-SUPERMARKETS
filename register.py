import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector


# ---------- MySQL Connection ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sathvika@123",
        database="mba_db"
    )

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")


class RegisterPage:
    def __init__(self, root, show_login):
        self.root = root
        self.show_login = show_login
        self.root.state("zoomed")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Background
        image_path = os.path.join(ASSETS_DIR, "register.jpg")
        bg_image = Image.open(image_path)
        self.bg_image_tk = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(1550, 800))
        bg_label = ctk.CTkLabel(self.root, image=self.bg_image_tk, text="")
        bg_label.place(relwidth=1, relheight=1)

        # Frame
        frame = ctk.CTkFrame(self.root, width=500, height=400, corner_radius=20, fg_color="white")
        frame.place(relx=0.55, rely=0.55, anchor="center")
        frame.pack_propagate(False)

        # Title
        ctk.CTkLabel(frame, text="  📝  Create New Account",
                     font=("Courier New", 23, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(frame, text="Register",
                     font=("Arial", 20, "bold"), text_color="green").pack(pady=(0, 20))

        # --- Username field with icon ---
        uname_frame = ctk.CTkFrame(frame, fg_color="transparent")
        uname_frame.pack(pady=12)

        ctk.CTkLabel(uname_frame, text="👤", font=("Arial", 18)).pack(side="left", padx=(0, 8))
        self.username_entry = ctk.CTkEntry(uname_frame, placeholder_text="Username",
                                           width=300, height=40, font=("Arial", 14))
        self.username_entry.pack(side="left")

        # --- Password field with icon + eye toggle ---
        pw_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pw_frame.pack(pady=12)

        ctk.CTkLabel(pw_frame, text="🔒", font=("Arial", 18)).pack(side="left", padx=(0, 8))
        self.password_entry = ctk.CTkEntry(pw_frame, placeholder_text="Password", show="*",
                                           width=300, height=40, font=("Arial", 14))
        self.password_entry.pack(side="left")

        self.show_pw = False
        self.eye_button = ctk.CTkButton(
            pw_frame, text="👁", width=25, height=25,
            fg_color="white", text_color="black",
            corner_radius=10,
            command=self.toggle_password
        )
        self.eye_button.place(in_=self.password_entry, relx=0.92, rely=0.5, anchor="center")

        # --- Register button ---
        create_btn = ctk.CTkButton(frame, text="Create Account", width=220, height=40,
                                   font=("Arial", 15, "bold"),
                                   fg_color="#4CAF50", hover_color="#388E3C",
                                   command=self.register_user)
        create_btn.pack(pady=20)

        # --- Back to Login ---
        back_btn = ctk.CTkButton(frame,
                                 text="⬅ Back to Login",
                                 font=("Arial", 13, "underline"),
                                 fg_color="transparent",
                                 text_color="blue",
                                 hover=False,
                                 command=self.show_login)
        back_btn.pack(pady=(10, 20))

    def toggle_password(self):
        """Show/Hide password"""
        if self.show_pw:
            self.password_entry.configure(show="*")
            self.eye_button.configure(text="👁")
        else:
            self.password_entry.configure(show="")
            self.eye_button.configure(text="🙈")
        self.show_pw = not self.show_pw

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username.strip() == "" or password.strip() == "":
            messagebox.showwarning("Input Error", "All fields are required")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login()
        except mysql.connector.Error as e:
            if e.errno == 1062:  # Duplicate entry
                messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
