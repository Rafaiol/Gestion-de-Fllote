import customtkinter as ctk
from PIL import Image, ImageTk
from vehicules import MainPage as VehiculesPage
from Glaciol import MainPage as GlaciolPage
import pyodbc
import datetime
from tkinter import ttk
import tkinter as tk


# Set CustomTkinter Appearance and Theme
ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MainPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Main Page")
        
        
        self.highlighted_vehicle_id = None
        self.highlighted_dates = {} # Counter for notifications
        self.highlighted_rows = {}
        
        self.nav_buttons = {}
        self.menu_icon = self.load_icon("Image_Assets/Menu.png", size=(25, 25))
        self.car_icon = self.load_icon("Image_Assets/front-car.png", size=(25, 25))
        self.Interventions_icon = self.load_icon("Image_Assets/Interventions.png", size=(25, 25))
        self.update_icon = self.load_icon("Image_Assets/Update.ico", size=(25, 25))
        self.call_icon = self.load_icon("Image_Assets/Contact.ico", size=(25, 25))
        self.about_icon = self.load_icon("Image_Assets/About.ico", size=(25, 25))
        self.close_icon = self.load_icon("Image_Assets/Close.ico", size=(25, 25))
        self.notification_icon = self.load_icon("Image_Assets/notification.png", size=(20, 20))
        self.notification_click_icon = self.load_icon("Image_Assets/notification_clicked.png", size=(20, 20))

        self.notification_frame = ctk.CTkFrame(self,height=35,fg_color="#08090b")
        self.notification_frame.pack(side="top" ,fill="x")
        self.notification_frame.pack_propagate(False)  # Prevents the frame from expanding
        
        # Navigation Menu Frame
        self.menu_frame = ctk.CTkFrame(self, width=150, corner_radius=0,fg_color="#08090b")
        self.menu_frame.pack(side="left", fill="y")

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=10,fg_color="#050505")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
       
        
        

        # Load Icons
        

        # Add Navigation Buttons
        self.add_nav_button("Véhicules","Véhicules", self.car_icon, self.show_véhicules_page)
        self.add_nav_button("Interventions","Interventions", self.Interventions_icon, self.show_Interventions_page)
        self.add_nav_button("Update","Update", self.update_icon, self.show_update_page)
        self.add_nav_button("Contact","Contact", self.call_icon, self.show_call_page)
        self.add_nav_button("About","About", self.about_icon, self.show_about_page)

        # Default Page
        self.show_véhicules_page()
        
        self.notification_btn = ctk.CTkButton(
            self.notification_frame, image=self.notification_icon,text="" ,width=40, height=30, corner_radius=10,
            command=self.show_notifications, fg_color="transparent",
            font=("Arial", 12, "bold")
        )
        self.notification_btn.pack(side="right",padx=10,pady=5)
        # Add this line to check notifications when the app starts
        self.check_notifications()
        
        # Set up periodic checking (every 60000 ms = 1 minute)
        self.after(30000, self.periodic_check)
        self.set_active_button("Véhicules")
    def periodic_check(self):
        """Check for notifications periodically"""
        self.check_notifications()
        self.after(30000, self.periodic_check)  # Schedule next check
    
    def get_connection(self):
        """Connect to the database."""
        try:
            return pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'server=WIN-1QQFTLB3RC8;'
                'Database=gestion_de_fllote;'
                'Trusted_Connection=yes'
            )
        except pyodbc.Error as e:
            print(f"Database Error: {str(e)}")
            return None

    def check_notifications(self):
        """Fetch vehicles with due dates and update the notification count."""
        connection = self.get_connection()
        if not connection:
            return

        today = datetime.date.today().strftime('%Y-%m-%d')
        query = """
        SELECT vehicule_id, marque, type, date_assurance, date_control_technique
        FROM véhicule
        WHERE 
             date_assurance <= ? OR 
             date_control_technique <= ?
        """
        try:
            cursor = connection.cursor()
            cursor.execute(query, (today, today))
            results = cursor.fetchall()

            # Update the notification list
            self.notifications = []
            today_date = datetime.date.today()
            for row in results:
                vehicule_id, marque, type_, assurance_date, control_date = row
                notification_text = f"{marque} {type_}  - "
                
                if assurance_date <= today_date:
                    status = "EXPIRED" if assurance_date < today_date else "Expiring Today"
                    notification_text += f"Assurance {status} "
                    
                if control_date <= today_date:
                    status = "OVERDUE" if control_date < today_date else "Due Today"
                    notification_text += f"| Control Technique {status}"
                
                self.notifications.append((vehicule_id, notification_text))

        finally:  
            connection.close()    
        if len(self.notifications)>0 :
                self.notification_btn.configure(image=self.notification_click_icon,
                                        text=f"",
                                        font=("Arial", 12))
        else:
                self.notification_btn.configure(image=self.notification_icon,
                                        text="",
                                        font=("Arial", 12))
          

    def show_notifications(self):
        """Show a styled dropdown-like notification panel."""
        if hasattr(self, "notification_popup") and self.notification_popup.winfo_exists():
            self.notification_popup.destroy()
            return

        if len(self.notifications)== 0:
            self.notification_btn.configure(image=self.notification_icon)
            return

        # Create a small popup window
        self.notification_popup = ctk.CTkToplevel(self)
          
        self.notification_popup.overrideredirect(True)
        self.notification_popup.attributes("-topmost", True)
        self.notification_popup.fg_color = ("#2b2b2b", "#2b2b2b")
        self.notification_popup.configure(corner_radius=15)   
        
        window_width = 450  # Adjust to match your notification size
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Final position (right edge, centered vertically)
        target_x = self.notification_btn.winfo_rootx()-435  # 20px from right edge
        target_y = self.notification_btn.winfo_rooty() + self.notification_btn.winfo_height()-25  # Vertical center
        
        # Start position (fully off-screen right)
        current_x = screen_width -85
        current_y = target_y
        fade_alpha = 0.0     
        
        def close_notification_popup():
         if hasattr(self, "notification_popup") and self.notification_popup.winfo_exists():
            self.notification_popup.destroy()
            if len(self.notifications) > 0:
                self.notification_btn.configure(image=self.notification_click_icon)
            else:
                self.notification_btn.configure(image=self.notification_icon)
        def check_click_outside(event):
         try:
            if (self.notification_popup.winfo_containing(event.x_root, event.y_root) is None and
                not self.notification_popup.winfo_containing(event.x_root, event.y_root)):
                close_notification_popup()
         except:
            pass
        self.notification_popup.bind("<FocusOut>", lambda e: fade_out())
        self.bind("<Button-1>", check_click_outside)

        
        
        self.notification_popup.focus_set()
        # Create a scrollable frame
        frame = ctk.CTkFrame(self.notification_popup,fg_color="#333333",corner_radius=30
        )
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        

        # Scrollable list of notifications
        #canvas = tk.Canvas(frame, bg="#2C2F33", highlightthickness=0, height=220)
        
        
        #scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(frame, fg_color="transparent")
        scrollable_frame.pack(side="left", fill="both", expand=True)
        self.notification_popup.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
        self.notification_popup.attributes("-alpha", 0.01)
        '''scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")'''
        def slide_in():
            nonlocal current_x, fade_alpha
            if current_x > target_x:
                current_x -= 30  # Animation speed
                fade_alpha = min(fade_alpha + 0.05, 1.0)  # Fade in
                self.notification_popup.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
                self.notification_popup.attributes("-alpha", fade_alpha)
                self.notification_popup.after(15, slide_in)
            else:
                self.notification_popup.attributes("-alpha", 1.0)

        def fade_out():
            def animate():
                nonlocal current_x, fade_alpha
                if fade_alpha > 0:
                    current_x += 20  # Move right
                    fade_alpha = max(fade_alpha - 0.05, 0)  # Fade out
                    self.notification_popup.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
                    self.notification_popup.attributes("-alpha", fade_alpha)
                    self.notification_popup.after(20, animate)
                else:
                    self.notification_popup.destroy()
            animate()
        
        def remove_notification(vehicule_id):
            """Remove notification from list and decrease count."""
            self.notifications = [notif for notif in self.notifications if notif[0] != vehicule_id]
            
            

            # Close the dropdown if all notifications are gone
            if len(self.notifications) == 0:
                self.notification_popup.destroy()
                self.notification_btn.configure(image=self.notification_icon)
                

        
        # Populate notifications
        for vehicule_id, text in self.notifications:
            notif_btn = ctk.CTkButton(
                scrollable_frame, text=text, font=("poppins", 12),
                fg_color="transparent", hover_color="#555555",
                corner_radius=5, command=lambda v=vehicule_id: [self.go_to_vehicle(v),remove_notification(v)],
                anchor="w", width=220,height=50
            )
            notif_btn.pack(fill="x", pady=2, padx=5)

        # Close button
        self.notification_popup.protocol("WM_DELETE_WINDOW", lambda: [
        self.notification_popup.destroy(),
        self.unbind("<Button-1>")
         ])
        def check_click(event):
            x = event.x_root
            y = event.y_root
            win_x = self.notification_popup.winfo_x()
            win_y = self.notification_popup.winfo_y()
            win_width = self.notification_popup.winfo_width()
            win_height = self.notification_popup.winfo_height()
            
            if not (win_x <= x <= win_x + win_width and
                    win_y <= y <= win_y + win_height):
                fade_out()

        self.notification_popup.bind("<Button-1>", check_click)
        slide_in()  # Start the animation

    def go_to_vehicle(self, vehicule_id):
            """Find, select, and highlight a vehicle in the Treeview."""
            self.show_véhicules_page()
            self.notification_popup.destroy()
            
            # Ensure VehiculesPage is loaded in the content frame
            if not hasattr(self, "content_frame") or not self.content_frame.winfo_children():
                print("Vehicle page not loaded yet.")
                return

            vehicle_page = self.content_frame.winfo_children()[0]  # Get VehiculesPage instance

            # Ensure the instance has a Treeview
            if not hasattr(vehicle_page, "tree"):
                print("Treeview not found in vehicle page. Check if self.tree is set in vehicules.py.")
                return

            tree = vehicle_page.tree  # Access the Treeview widget
            found = False
            assurance_date = None  # Initialize variables
            control_date = None

            # Reset previous highlight if any
            if hasattr(self, "highlighted_row") and self.highlighted_row:
                tree.item(self.highlighted_row, tags=("normalrow",))
                self.highlighted_row = None

            # Ensure the Treeview has correct tag configurations
            tree.tag_configure("highlighted", foreground="#c80036",background="#333333", font=('poppins', 12,"bold"))  # Red highlight
            tree.tag_configure("normalrow", foreground="#b3b3b3",background="#333333")  # Default color
            if not hasattr(self, "highlighted_rows"):
                self.highlighted_rows = {}

            # Iterate over Treeview rows to find the matching vehicule_id
            for item in tree.get_children():
                values = tree.item(item)['values']
                print(f"Checking row: {values}")  # Debugging output

                # Ensure matching ID (string vs int issue)
                if values and str(values[0]) == str(vehicule_id):  
                    tree.selection_set(item)  # Select the row
                    tree.focus(item)  # Focus on the row
                    tree.see(item)  # Scroll to it
                    tree.item(item, tags=("highlighted",))  # Apply red highlight
                    self.highlighted_row = item  # Save current highlighted row
                    
                    self.highlighted_rows[vehicule_id] = item
                    
                    connection = self.get_connection()
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT date_assurance, date_control_technique "
                        "FROM véhicule WHERE vehicule_id = ?", 
                        (vehicule_id,)
                    )
                    assurance_date, control_date = cursor.fetchone()
                    connection.close()
                    found = True
                    
                    print(f"Vehicle {vehicule_id} found and highlighted.")
                     # Store highlighted vehicle's dates
                    break
                    
            if not found:
                print(f"Vehicle {vehicule_id} not found in table.")
                return
            
            
            self.highlighted_vehicle_id = vehicule_id
            self.highlighted_dates = {
                'assurance': assurance_date,
                'control': control_date
            }

    def check_highlight(self):
        """Re-check highlighted vehicle status after updates"""
        for vehicule_id in list(self.highlighted_rows.keys()):
            try:
                self.go_to_vehicle(vehicule_id)
            except Exception as e:
                print(f"Error highlighting {vehicule_id}: {str(e)}")
                del self.highlighted_rows[vehicule_id]
    def load_icon(self, path, size):
        """Load and resize an icon."""
        img = Image.open(path)
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img_resized)

    def add_nav_button(self,key, text, icon, command):
        """Create a navigation button."""
        button = ctk.CTkButton(
            self.menu_frame,
            text=text,
            image=icon,
            compound="left",
            fg_color="transparent",
            text_color="white",
            hover_color="#534AE1",
            command=command,
            anchor="w",
            font=("Helvetica", 14, "bold"),
        )
        button.pack(fill="x", pady=5, padx=10)
        self.nav_buttons[key] = button
    def set_active_button(self,key):
        # Reset all buttons to default color
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")
        # Set the active button's color
        if key in self.nav_buttons:
            self.nav_buttons[key].configure(fg_color="#534AE1") 
    def clear_content_frame(self):
        """Clear all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    def show_véhicules_page(self):
          self.clear_content_frame()
          vehicules_page=VehiculesPage(master=self.content_frame,main_app=self,fg_color="#050505")
          vehicules_page.pack(fill="both",expand=True)
          self.set_active_button("Véhicules")
          
          
    def show_Interventions_page(self):
        self.clear_content_frame()
        glaciol_frame = GlaciolPage(master=self.content_frame,fg_color="#050505")
        glaciol_frame.page_frame.pack(fill="both", expand=True)
        self.set_active_button("Interventions")
        

    def show_update_page(self):
        self.clear_content_frame()
        label = ctk.CTkLabel(self.content_frame, text="Update Page", font=("Arial", 16))
        label.pack(pady=20)

    def show_call_page(self):
        self.clear_content_frame()
        label = ctk.CTkLabel(self.content_frame, text="Call Page", font=("Arial", 16))
        label.pack(pady=20)

    def show_about_page(self):
        self.clear_content_frame()
        label = ctk.CTkLabel(self.content_frame, text="About Page", font=("Arial", 16))
        label.pack(pady=20)
    
if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
