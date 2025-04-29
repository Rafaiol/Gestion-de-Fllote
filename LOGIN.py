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
                "database": "gestion_de_fllote",
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
        self.title("Login")
        self.iconbitmap("Image_Assets/Logo.ico")
        self.geometry("400x600")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.configure(fg_color="#08090b")
        
        #ctk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("blue")
        
        
        
        # Initialize database
        self.db = DatabaseManager()
        
        self._create_widgets()
        self._create_layout()
        
    def load_icon(self, path, size):
            img = Image.open(path)
            return ctk.CTkImage(dark_image=img, size=size)
            
    def _create_widgets(self):
        self.logo_icon = self.load_icon("Image_Assets/Logo.png", size=(180, 180))
        self.logo_label=ctk.CTkLabel(self,text="",image=self.logo_icon )
        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#08090b",bg_color="#08090b",corner_radius =30)
        
        
        # Welcome text
        self.welcome_label = ctk.CTkLabel(
            self.main_frame,
            text="Bienvenue",
            font=("Host grotesk", 30, "bold"),
            text_color="white"
        )
        
        
        self.email_label = ctk.CTkLabel(
           self.main_frame,
           text="Nom Utilisateur :",
           font=("poppins", 17),
           anchor="w" 
        )

        # Email entry
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Nom Utilisateur",
            font=("poppins", 12),
            width=300,
            height=50,
            border_width=2,
            corner_radius=10,border_color=""
        )
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.configure(border_color="#534AE1"))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.configure(border_color=""))
        
        self.password_label = ctk.CTkLabel(
        self.main_frame,
        text="Mot de passe :",
        font=("poppins", 17),
        anchor="w"
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
            show="•",border_color=""
        )
        self.password_entry.bind('<FocusIn>', lambda e: self.password_entry.configure(border_color="#534AE1"))
        self.password_entry.bind('<FocusOut>', lambda e: self.password_entry.configure(border_color=""))
        # Remember me checkbox
       

       

        # Login button
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Entrer",
            font=("poppins", 18, "bold"),
            width=300,
            height=50,
            corner_radius=10,
            command=self._on_login
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
        self.logo_label.pack(side="top",pady=(20,0))
        # Place main frame
        self.main_frame.pack(expand=True, padx=40, pady=40 )
        
        # Layout widgets with proper spacing
        #self.welcome_label.pack(pady=(0, 30), anchor="w")
        self.email_label.pack(pady=(0, 5), anchor="w")
        self.username_entry.pack(pady=(0, 20))
        self.password_label.pack(pady=(0, 5), anchor="w")
        self.password_entry.pack(pady=(0, 20))
        self.show_password_check.pack(pady=(0, 10), anchor="w")  # Added anchor="w" here
        
        # Create a frame for remember me and forgot password
        
      
        
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
            cursor.execute("SELECT password_v, role,full_name FROM utilisateurs WHERE username = ?", (user,))
            user_data = cursor.fetchone()
            
            if user_data is None:
                CustomMessageBox.show_error("Login Failed", "L'utilisateur n'existe pas.")
                self.username_entry.configure(border_color="red")
                return

            # If user exists, then check password
            stored_password, user_role, full_name = user_data

            if stored_password == password:
                self._handle_successful_login(user,full_name,user_role)
                
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
       
    

    def _handle_successful_login(self, user: str,full_name :str,user_role :str):
        # Update last login timestamp
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE utilisateurs SET last_login = GETDATE() WHERE username = ?",
                (user ,)
            )
            self.db.connection.commit()
        CustomMessageBox.show_info("Succès", f"Bienvenue, {full_name}")
            
        # Destroy the login window
        self.destroy()
        from main import MainPage
        # Create and show the main application window
        main_app = MainPage(user_role = user_role, full_name = full_name)
        
        main_app.mainloop()
            
        

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




