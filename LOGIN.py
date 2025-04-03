import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import pyodbc
import bcrypt
from typing import Optional
import re
import logging
import json
import tkinter as tk
from tkinter import BOTH# Import tkinter for styling messagebox


class CustomMessageBox:  # Keep this class for consistent styling
    @staticmethod
    def show_error(title, message):
        root = tk.Tk()
        root.withdraw()
        root.option_add('*Dialog.msg.font', 'Helvetica 11')
        root.option_add('*Dialog.msg.background', '#2b2b2b')  # Dark background
        root.option_add('*Dialog.msg.foreground', 'white')    # White text
        root.option_add('*Dialog.Button.font', 'Helvetica 10 bold')
        root.option_add('*Dialog.Button.background', '#1f538d')  # Blue button
        root.option_add('*Dialog.Button.foreground', 'white')    # White button text
        messagebox.showerror(title, message)
        root.destroy()

    @staticmethod
    def show_info(title, message):  # Added show_info for other message types
        root = tk.Tk()
        root.withdraw()
        # Apply the same styling as error messages
        root.option_add('*Dialog.msg.font', 'Helvetica 11')
        root.option_add('*Dialog.msg.background', '#2b2b2b')
        root.option_add('*Dialog.msg.foreground', 'white')
        root.option_add('*Dialog.Button.font', 'Helvetica 10 bold')
        root.option_add('*Dialog.Button.background', '#1f538d')
        root.option_add('*Dialog.Button.foreground', 'white')
        messagebox.showinfo(title, message)
        root.destroy()


class DatabaseManager:
    def __init__(self, config_path: str = "config.json"):
        self.logger = logging.getLogger(__name__)
        self.connection: Optional[pyodbc.Connection] = None
        self.config = self._load_config(config_path)
        self._setup_database()

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "server": "WIN-1QQFTLB3RC8",
                "database": "partes_store",
                "trusted_connection": "yes"
            }

    def _setup_database(self) -> None:
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={self.config['server']};"
            f"DATABASE={self.config['database']};"
            f"Trusted_Connection={self.config['trusted_connection']};"
        )
        
        try:
            self.connection = pyodbc.connect(connection_string)
            
        except pyodbc.Error as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise

    

class LoginForm(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # Configure window and theme
        self.title("Modern Login")
        self.geometry("400x600")
        #self.overrideredirect(1)
        self.wm_attributes("-transparentcolor", "grey")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        
        
        # Initialize database
        self.db = DatabaseManager()
        
        self._create_widgets()
        self._create_layout()
        self.background = self.load_icon("Image_Assets/background.jpg", size=(400, 600))
        frame_label = ctk.CTkLabel(self,bg_color='grey',text='',image=self.background)
        frame_label.pack(fill=BOTH,expand=True)
        
    def load_icon(self, path, size):
            """Load and resize an icon."""
            img = Image.open(path)
            img_resized = img.resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(img_resized, size=size)
    def _create_widgets(self):
        # Main frame
        #self.main_frame = ctk.CTkFrame(self, fg_color="transparent",bg_color="transparent",corner_radius =30)
        self.main_frame = ctk.CTkLabel(self, fg_color="transparent", text="", bg_color="transparent")

        # Welcome text
        self.welcome_label = ctk.CTkLabel(
            self.main_frame,
            text="Bienvenue",
            font=("Host grotesk", 40, "bold"),
            text_color="white",fg_color="transparent"
        )
        
        
        self.email_label = ctk.CTkLabel(
           self.main_frame,
           text="Nom Utilisateur :",
           font=("poppins", 17),
           anchor="w",fg_color="transparent"
        )

        # Email entry
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Nom Utilisateur",
            font=("poppins", 12),
            width=300,
            height=50,
            border_width=2,
            corner_radius=10,fg_color="transparent"
        )
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.configure(border_color="#561B8D"))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.configure(border_color=""))
        
        self.password_label = ctk.CTkLabel(
        self.main_frame,
        text="Mot de passe :",
        font=("poppins", 17),
        anchor="w",fg_color="transparent"
        )
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Mot de passe",
            font=("poppins", 12),
            width=300,
            height=50,
            border_width=2,
            corner_radius=10,
            show="•",fg_color="transparent"
        )
        self.password_entry.bind('<FocusIn>', lambda e: self.password_entry.configure(border_color="#561B8D"))
        self.password_entry.bind('<FocusOut>', lambda e: self.password_entry.configure(border_color=""))
        # Remember me checkbox
        self.remember_var = ctk.BooleanVar()
        self.remember_check = ctk.CTkCheckBox(
            self.main_frame,
            text="Remember me",
            variable=self.remember_var,
            font=("Helvetica", 12),
            corner_radius=6
        )

       

        # Login button
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Entrer",
            font=("poppins", 18, "bold"),
            width=300,
            height=50,
            corner_radius=10,
            command=self._on_login,fg_color="transparent"
        )

        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar()
        self.show_password_check = ctk.CTkCheckBox(
          self.main_frame,
          text="Voir le mot de passe",
          variable=self.show_password_var,
          font=("Helvetica", 12),
          corner_radius=6,
          command=self._toggle_password_visibility)

    def _create_layout(self):
        # Place main frame
        self.main_frame.pack(expand=True, padx=40, pady=40 )
        
        # Layout widgets with proper spacing
        self.welcome_label.pack(pady=(0, 30), anchor="w")
        self.email_label.pack(pady=(0, 5), anchor="w")
        self.username_entry.pack(pady=(0, 20))
        self.password_label.pack(pady=(0, 5), anchor="w")
        self.password_entry.pack(pady=(0, 20))
        self.show_password_check.pack(pady=(0, 20), anchor="w")  # Added anchor="w" here
        
        # Create a frame for remember me and forgot password
        options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 30))
        
        self.remember_check.pack(side="left", in_=options_frame)
      
        
        self.login_button.pack(pady=(0, 20))
        #self.signup_button.pack()
        
        
    def _on_login(self):
        user = self.username_entry.get()
        password = self.password_entry.get()

        if not self._validate_input(user, password):
            return

        try:
           with self.db.connection.cursor() as cursor:
            # First check if user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user,))
            user_exists = cursor.fetchone()[0]
            
            if not user_exists:
                CustomMessageBox.show_error("Login Failed", "L'utilisateur n'existe pas.")
                self.username_entry.configure(border_color="red")
                return

            # If user exists, then check password
            cursor.execute("SELECT password_v FROM users WHERE username = ?", (user,))
            stored_password = cursor.fetchone()[0]

            if stored_password == password:
                self._handle_successful_login(user)
            else:
                CustomMessageBox.show_error("Login Failed", "Mot de passe incorrect.")
                self.password_entry.configure(border_color="red")

        except pyodbc.Error as e:
           self.logger.error(f"Login error: {str(e)}")
           CustomMessageBox.show_error("Database Error", "An error occurred during login.")
    def _validate_input(self, user: str, password: str) -> bool:
        user_pattern =  r'^[a-zA-Z]+$' 

        if not re.match(user_pattern, user):
            CustomMessageBox.show_error("Invalid user", "Le nom d'utilisateur doit contenir uniquement des lettres.")
            self.username_entry.configure(border_color="red")
            return False
        else:
            self._clear_entry_error(self.username_entry)
        if len(password) < 8 or len(password) > 16 :
            CustomMessageBox.show_error("Invalid Password", "Le mot de passe doit comporter entre 8 et 16 caractères.")
            self.password_entry.configure(border_color="red")
            return False
        else:
            self._clear_entry_error(self.password_entry)
            

        return True        
       
    

    def _handle_successful_login(self, user: str):
        # Update last login timestamp
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET last_login = GETDATE() WHERE username = ?",
                (user ,)
            )
            self.db.connection.commit()
            
        # TODO: Implement remember me functionality
        if self.remember_var.get():
            pass
            
        # Navigate to main application
        self.destroy()  # For this example, just close the window

    def _handle_failed_login(self):
        # Show error message to user
        pass


    
    def _toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")
    def _show_entry_error(self, entry):
        entry.configure(border_color="red")

    def _clear_entry_error(self, entry):
        entry.configure(border_color="")
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = LoginForm()
    app.mainloop()




