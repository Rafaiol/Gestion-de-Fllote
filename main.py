import customtkinter as ctk
from PIL import Image, ImageTk
from vehicules import MainPage as VehiculesPage
from Glaciol import MainPage as GlaciolPage
from Liquide_de_frein import MainPage as Liquide_de_freinPage
from Huile_Moteur import MainPage as Huile_MoteurPage
from Chaine_de_distrubution import MainPage as Chaine_MoteurPage
from Courroie_Moteur import MainPage as Courroie_MoteurPage
from Historique_Reparation import MainPage as ReparationPage
from Utilisteurs import MainPage as UtilisteursPage
import pyodbc
import datetime
from tkinter import ttk
import tkinter as tk


# Set CustomTkinter Appearance and Theme
ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MainPage(ctk.CTk):
    def __init__(self,user_role = None ,full_name = None):
        super().__init__()
        self.geometry("800x600")
        self.title("Main Page")
        
        self.user_role = user_role
        self.full_name = full_name
        
        self.highlighted_vehicle_id = None
        self.highlighted_dates = {} # Counter for notifications
        self.highlighted_rows = {}
        
        self.nav_buttons = {}
        self.menu_icon = self.load_icon("Image_Assets/Menu.png", size=(25, 25))
        self.car_icon = self.load_icon("Image_Assets/front-car.png", size=(25, 25))
        self.Interventions_icon = self.load_icon("Image_Assets/service-de-reparation.png", size=(25, 25))
        self.Historique_Rep_icon = self.load_icon("Image_Assets/reparation-automobile.png", size=(25, 25))
        self.Utilisateur_icon = self.load_icon("Image_Assets/utilisateur.png", size=(25, 25))
        self.Utilisateur2_icon = self.load_icon("Image_Assets/utilisateur2.png", size=(30, 30))
        self.Rapports_icon = self.load_icon("Image_Assets/fichier-texte.png", size=(25, 25))
        self.close_icon = self.load_icon("Image_Assets/Close.ico", size=(25, 25))
        self.notification_icon = self.load_icon("Image_Assets/notification.png", size=(20, 20))
        self.notification_click_icon = self.load_icon("Image_Assets/notification_clicked.png", size=(20, 20))

        self.notification_frame = ctk.CTkFrame(self,height=45,fg_color="#08090b")
        self.notification_frame.pack(side="top" ,fill="x")
        self.notification_frame.pack_propagate(False)  # Prevents the frame from expanding
        
        # Navigation Menu Frame
        self.menu_frame = ctk.CTkFrame(self, width=150, corner_radius=0,fg_color="#08090b")
        self.menu_frame.pack(side="left", fill="y")

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=10,fg_color="#050505")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
       
        
        

        # Load Icons
        
        print(self.user_role)
        # Add Navigation Buttons
        self.add_nav_button("Véhicules","Véhicules", self.car_icon, self.show_véhicules_page)
        self.add_nav_button("Interventions","Interventions", self.Interventions_icon, self.show_Interventions_page)
        self.add_nav_button("Historique","Historique", self.Historique_Rep_icon, self.show_Historique_Rep_page)
        if  user_role != "technicien":
         self.add_nav_button("Utilisateurs", "Utilisateurs", self.Utilisateur_icon, self.show_Utilisateur_page)
        self.add_nav_button("Rapports","Rapports", self.Rapports_icon, self.show_Rapports_page)

        # Default Page
        self.show_véhicules_page()
        
        self.notification_btn = ctk.CTkButton(
            self.notification_frame, image=self.notification_icon,text="" ,width=40, height=30, corner_radius=10,
            command=self.show_notifications, fg_color="transparent",
            font=("Arial", 12, "bold")
        )
        self.full_name_btn = ctk.CTkButton(self.notification_frame,text=self.full_name,image = self.Utilisateur2_icon,compound="left",width=180,height=30,corner_radius=5,fg_color="transparent",font=("poppins",16,"bold"))
        self.full_name_btn.pack(side="right",pady=5)
        self.notification_btn.pack(side="right",pady=5)
        
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
        query_huile="""SELECT H.num_huile, v.vehicule_id, v.marque, v.type, v.Immatriculation, 
                H.Index_veh, H.Index_veh_old
            FROM Vehicule v
            INNER JOIN huile_moteur H ON v.vehicule_id = H.vehicule_id
            WHERE H.Index_veh - H.Index_veh_old >= 10000"""
        query_vehicule = """
        SELECT vehicule_id, marque, type, date_assurance, date_control_technique
        FROM Vehicule
        WHERE 
             date_assurance <= ? OR 
             date_control_technique <= ?
        """
        try:
            cursor = connection.cursor()
            cursor.execute(query_vehicule, (today, today))
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
                
                self.notifications.append(("vehicle",vehicule_id, notification_text))
            cursor.execute(query_huile)
            index_results = cursor.fetchall()
            for row in index_results:
                num_huile, vehicule_id, marque, type_, immatriculation, index_veh, index_veh_old = row
                notification_text = f"{marque} {type_} ({immatriculation}) - Oil change needed (Index: {index_veh})"
                self.notifications.append(("huile", num_huile, notification_text))
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
        target_x = self.notification_btn.winfo_rootx()-433  # 20px from right edge
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
        for notif_type, id_value, text in self.notifications:
            notif_btn = ctk.CTkButton(
                scrollable_frame, text=text, font=("poppins", 12),
                fg_color="transparent", hover_color="#555555",
                corner_radius=5, command=lambda t=notif_type, i=id_value: [self.go_to_vehicle(t, i), remove_notification((t, i))],
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

    def go_to_vehicle(self,notification_type, id_value):
            """Find, select, and highlight a vehicle in the Treeview."""
            if notification_type == "vehicle":
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
                tree.tag_configure("highlighted", foreground="#c80036", font=('poppins', 12,"bold"))  # Red highlight
                tree.tag_configure("normalrow", foreground="#b3b3b3")  # Default color
                if not hasattr(self, "highlighted_rows"):
                    self.highlighted_rows = {}

                # Iterate over Treeview rows to find the matching vehicule_id
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    print(f"Checking row: {values}")  # Debugging output

                    # Ensure matching ID (string vs int issue)
                    if values and str(values[0]) == str(id_value):  
                        tree.selection_set(item)  # Select the row
                        tree.focus(item)  # Focus on the row
                        tree.see(item)  # Scroll to it
                        tree.item(item, tags=("highlighted",))  # Apply red highlight
                        self.highlighted_row = item  # Save current highlighted row
                        
                        self.highlighted_rows[id_value] = item
                        
                        connection = self.get_connection()
                        cursor = connection.cursor()
                        cursor.execute(
                            "SELECT date_assurance, date_control_technique "
                            "FROM Vehicule WHERE vehicule_id = ?", 
                            (id_value,)
                        )
                        assurance_date, control_date = cursor.fetchone()
                        connection.close()
                        found = True
                        
                        print(f"Vehicle {id_value} found and highlighted.")
                        # Store highlighted vehicle's dates
                        break
                        
                if not found:
                    print(f"Vehicle {id_value} not found in table.")
                    return
                
                
                self.highlighted_vehicle_id = id_value
                self.highlighted_dates = {
                    'assurance': assurance_date,
                    'control': control_date
                }
            elif notification_type == "huile":
                # Handle oil change notification
                self.show_Interventions_page()
                self.notification_popup.destroy()
                self.update()
                # Get to the Huile Moteur page
                huile_page = self.content_frame.winfo_children()[0]
                
                
                
                if not huile_page or not hasattr(huile_page, "tree"):
                    print("Huile Moteur page or tree not found")
                    return
                    
                tree = huile_page.tree
                huile_page.fetch_all_data(tree, "huile_moteur")
                
                # Reset previous highlight if any
                if hasattr(self, "highlighted_huile_row") and self.highlighted_huile_row:
                    tree.item(self.highlighted_huile_row, tags=("normalrow",))
                    self.highlighted_huile_row = None

                # Configure tags
                tree.tag_configure("highlighted", foreground="#c80036", background="#333333", font=('poppins', 12, "bold"))
                tree.tag_configure("normalrow", foreground="#b3b3b3", background="#333333")

                # Find and highlight the row
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    if values and str(values[0]) == str(id_value):  # num_huile is first column
                        tree.selection_set(item)
                        tree.focus(item)
                        tree.see(item)
                        tree.item(item, tags=("highlighted",))
                        self.highlighted_huile_row = item
                        
                        # Update index_veh_old in database
                        connection = self.get_connection()
                        try:
                            cursor = connection.cursor()
                            cursor.execute(
                                "UPDATE huile_moteur SET Index_veh_old = Index_veh WHERE num_huile = ?",
                                (id_value,)
                            )
                            connection.commit()
                        finally:
                            connection.close()
                        break
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
        if key == "Utilisateurs" and self.user_role == "technicien":
          return
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
        
        button.pack(fill="x", pady=10, padx=10)
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
          
        vehicules_page =VehiculesPage(master=self.content_frame, user_role=self.user_role,fg_color="#050505")
        vehicules_page.pack(fill="both",expand=True)
        self.set_active_button("Véhicules")
          
          
          
    def show_Interventions_page(self):
        self.clear_content_frame()

        # Create a frame for the tab buttons
        tab_button_frame = ctk.CTkFrame(self.content_frame, fg_color="#050505")
        tab_button_frame.pack(side="top",anchor="center", padx=10, pady=10)

        # Create a frame for the tab content
        tab_content_frame = ctk.CTkFrame(self.content_frame, fg_color="#050505")
        tab_content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tab_buttons = {}
        default_fg_color = "#2b2b2b"  # Default button color
        highlight_color = "#534AE1"  # Highlight color
        # Function to switch tabs
        def switch_tab(tab_name):
            for button in tab_buttons.values():
                button.configure(fg_color=default_fg_color,font=("poppins", 14))
        
            # Highlight the selected button
            if tab_name in tab_buttons:
                tab_buttons[tab_name].configure(fg_color=highlight_color,font=("poppins", 14,"bold"))
                # Hide all frames
            for widget in tab_content_frame.winfo_children():
                widget.pack_forget()
            
            # Show the selected frame
            if tab_name == "Huile Moteur":
                Huile_frame.pack(fill="both", expand=True)
            elif tab_name == "Chaine de Distribution":
                Chaine_frame.pack(fill="both", expand=True)
            elif tab_name == "Courroie Moteur":
                Courroie_frame.pack(fill="both", expand=True)
            elif tab_name == "Glaciol":
                glaciol_frame.pack(fill="both", expand=True)
            elif tab_name == "Liquide de Frein":
                Liquide_frame.pack(fill="both", expand=True)

        # Create tab buttons
        tab_names = ["Huile Moteur", "Chaine de Distribution", "Courroie Moteur", "Glaciol", "Liquide de Frein"]
        for name in tab_names:
            button = ctk.CTkButton(
                tab_button_frame,
                text=name,
                height=30,
                font=("poppins", 14),  # Custom font
                fg_color="#2b2b2b",  # Background color
                hover_color="#534AE1",  # Hover color
                command=lambda n=name: switch_tab(n),  # Switch to the selected tab
            )
            button.pack(side="left", padx=5, pady=5)
            tab_buttons[name] = button
        # Create frames for each tab
        glaciol_frame = GlaciolPage(master=tab_content_frame,user_role=self.user_role, fg_color="#050505")
        Liquide_frame = Liquide_de_freinPage(master=tab_content_frame,user_role=self.user_role, fg_color="#050505")
        Huile_frame = Huile_MoteurPage(master=tab_content_frame,user_role=self.user_role , fg_color="#050505")
        Chaine_frame = Chaine_MoteurPage(master=tab_content_frame,user_role=self.user_role, fg_color="#050505")
        Courroie_frame = Courroie_MoteurPage(master=tab_content_frame,user_role=self.user_role, fg_color="#050505")

        # Show the first tab by default
        switch_tab("Huile Moteur")

        self.set_active_button("Interventions")
        

    def show_Historique_Rep_page(self):
        self.clear_content_frame()
        self.after(300, lambda: [
        Reparation_page :=ReparationPage(master=self.content_frame, user_role=self.user_role,fg_color="#050505"),
        Reparation_page.pack(fill="both",expand=True),
        self.set_active_button("Historique")])

    def show_Utilisateur_page(self):
        self.clear_content_frame()
        self.after(300, lambda: [
        Utilisateurs_page :=UtilisteursPage(master=self.content_frame, user_role=self.user_role,fg_color="#050505"),
        Utilisateurs_page.pack(fill="both",expand=True),
        self.set_active_button("Utilisateurs")])

    def show_Rapports_page(self):
        self.clear_content_frame()
        self.after(300, lambda: [
        self.set_active_button("Rapports")])
    
if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
