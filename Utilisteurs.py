import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import pyodbc
from PIL import Image, ImageTk
import os


ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MainPage(ctk.CTkFrame):
    def load_icon(self, path, size):
         """Load and resize an icon."""
         img =  Image.open(path)
         img_resized = img.resize(size, Image.Resampling.LANCZOS)
         return ctk.CTkImage(img_resized) 
    def __init__(self, master=None,user_role=None, **kwargs):
        super().__init__(master, **kwargs)
        self.user_role = user_role
        self.pack(fill="both", expand=True)
        
        self.existing_button_frames = {}
        
        self.add_icon = self.load_icon("Image_Assets/Addition.png", size=(25, 25))
        self.filter_icon = self.load_icon("Image_Assets/sort.png", size=(25, 25))
        self.refresh_icon = self.load_icon("Image_Assets/Refresh.png", size=(25, 25))
        self.search_icon = self.load_icon("Image_Assets/search.png", size=(25, 25))
        self.supprimer_icon = self.load_icon("Image_Assets/trash.png", size=(20, 20))
        self.Update_icon = self.load_icon("Image_Assets/edit.png", size=(20, 20))
        self.Inspect_icon = self.load_icon("Image_Assets/search1.png", size=(20, 20))
        
        self.page_frame = ctk.CTkFrame(self, corner_radius=10,fg_color="#050505")
        self.page_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure(1, weight=1)
       
        
        
        
        self.buttons_frame = ctk.CTkFrame(self.page_frame, corner_radius=20,height=80,fg_color="transparent")
        self.buttons_frame.grid(row=0,column=0,columnspan=2, padx=10,pady=10,sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        
        self.right_buttons_frame = ctk.CTkFrame(self.page_frame,fg_color="transparent" ,corner_radius=0,width=100)
        self.right_buttons_frame.grid(row=1,column=1,padx=(3,3) ,pady=10,sticky="nsew")
  
        self.actions_label = ctk.CTkLabel(self.right_buttons_frame, text="Actions", font=("Poppins", 14, "bold"))
        self.actions_label.pack(fill="x")

    
    
        
        
        
# Database connection helper function
        def get_connection(): 
         try:
          return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'server=WIN-1QQFTLB3RC8;'
            'Database=gestion_de_fllote;'
            'Trusted_Connection=yes'
        )
         except pyodbc.Error as e:
          messagebox.showerror("Database Error", f"Failed to connect: {str(e)}")
          return None
        
        
        def start_add_mode(tree, tab):
            
                           
            # Create popup window
            popup = ctk.CTkToplevel()
            popup.title("Add New Record")
            popup.overrideredirect(True)
            popup.geometry("700x450")
            popup.resizable(False, False)
            popup.transient(tree.winfo_toplevel())  # Make popup transient to main window
            popup.grab_set()  # Make popup modal
            popup.focus_set()
        
                    # Create main frame with padding
            main_frame = ctk.CTkFrame(popup)
            main_frame.pack(expand=True, fill="both", padx=20, pady=20)

            # Grid configuration for responsive layout
            main_frame.grid_columnconfigure((0,1), weight=1)
            main_frame.grid_rowconfigure(4, weight=1)

            # Get vehicle data
            
            # Fields and entries
            fields = [ "Nom complet","Nom Utilisateur", "Mot de passe", "Role"]
            entries = []
            
            
            
            # Create entries with improved layout
            for i,field in enumerate(fields):
                row = i // 2  # Integer division for row number
                col = i % 2   # Column number (0 or 1)
                
                # Container frame for each field
                field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
                label = ctk.CTkLabel(field_frame, text=field + ":", font=("Helvetica", 18))
                label.pack(anchor="w", pady=(0, 2))
                
                
                    
                entry = ctk.CTkEntry(field_frame, font=("Helvetica", 13),placeholder_text=field, width=220,border_color="", height=40)
                entry.pack(fill="x")
                if field == "Role":
                    entry.configure(text="Technicien")
                entries.append(entry)
                   
            
            

            # Button frame
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky="e")

            def save_record(): 
                
                
                
                values = [entries[0].get().strip(),entries[1].get().strip(),entries[2].get().strip(),entries[3].get().strip()]
                
                if any(value == '' for value in values):
                    messagebox.showerror("Error", "Please fill all fields")
                    return
                
                query = "INSERT INTO utilisateurs (full_name,username, password_v,role) VALUES (?, ?, ?, ?)"
                try:
                    connection = get_connection()
                    cursor = connection.cursor()
                    cursor.execute(query, values)
                    connection.commit()
                    fetch_all_data(tree, tab)
                    messagebox.showinfo("Success", "Record added successfully")
                    popup.destroy()
                except pyodbc.Error as e:
                    messagebox.showerror("Database Error", f"Failed to add record:{str(e)}")

            # Create buttons
            ctk.CTkButton(button_frame, text="Cancel", width=100, height=30, command=popup.destroy).pack(side="right", padx=5)
            ctk.CTkButton(button_frame, text="Clear", width=100, height=30, command=lambda: [entry.delete(0, 'end') for entry in entries]).pack(side="right", padx=5)
            ctk.CTkButton(button_frame, text="Save", width=100, height=30, command=save_record).pack(side="right", padx=5)

            # Center popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
            y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
            popup.geometry(f"+{x}+{y}")
        
        def fetch_data(tree, query, params=()):
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute(query, params)
                data = cursor.fetchall()
                
                current_ids = {str(row[0]) for row in data}

                # Remove buttons for rows that no longer exist
                for vehicule_id in list(self.existing_button_frames.keys()):
                    if vehicule_id not in current_ids:
                        self.existing_button_frames[vehicule_id].destroy()
                        del self.existing_button_frames[vehicule_id]
                # Clear Treeview before inserting new data
                for item in tree.get_children():
                    tree.delete(item)
                
                # Insert fetched data into the Treeview
                for i, row in enumerate(data):
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    vehicule_id=row[0]
                    tree.insert('', 'end', values=[str(item) for item in row], tags=(tag,))
                    if vehicule_id not in self.existing_button_frames:
                        add_row_buttons(tree, vehicule_id)
                

                cursor.close()
                connection.close()
            except pyodbc.Error as e:
                print(f"Error: {e}")
        
        def add_row_buttons(tree, vehicule_id):
            """Dynamically add Update, Delete, and Inspect buttons next to each row."""
            if vehicule_id in self.existing_button_frames:
                return
            # Find the corresponding row in the Treeview
            row_id = None
            for item in tree.get_children():
                values = tree.item(item)['values']
                if values and str(values[0]) == str(vehicule_id):
                    row_id = item
                    break

            
            # Create a frame to hold the buttons
            row_button_frame = ctk.CTkFrame(self.right_buttons_frame, fg_color="transparent",height=40)
            row_button_frame.pack(fill="x",pady=4)  # Expand to fill the row

            # Create buttons inside this frame
            update_btn = ctk.CTkButton(row_button_frame, text="", fg_color="transparent",width=30,image=self.Update_icon,
                                    command=lambda: update_popup(tree, tab,row_id))
            delete_btn = ctk.CTkButton(row_button_frame, text="", fg_color="transparent",width=30,image=self.supprimer_icon ,
                                    command=lambda: delete_selected(tree, tab,row_id))
            
           
            # Pack buttons inside the frame
            update_btn.pack(side="left", padx=2)
            delete_btn.pack(side="left", padx=2)
            
            
            self.existing_button_frames[vehicule_id] = row_button_frame
        
       
        
        
            
            
            
        def filter_search(tree,*args):
                
                
            
            value = self.search_entry.get()
            query = f'''SELECT  id,full_name, username, password_v,role 
                    FROM utilisateurs
                     WHERE 
                    id LIKE ? OR 
                    full_name LIKE ? OR 
                    username LIKE ? OR 
                    password_v LIKE ? OR 
                    v,role LIKE ? '''
            params = (f"%{value}%",) * 5
            fetch_data(tree, query, params)
            
                
            
                            
                
# Fetch all data
        def fetch_all_data(tree, tab):
            if not tab:
                print("Please enter a table name.")
                return
            query = """
                SELECT  id,full_name, username, password_v,role,last_login 
                        FROM utilisateurs
                        
                """
            fetch_data(tree, query)

        
        def delete_selected( tree, tab,row_id):
            '''selected_items = tree.selection()  # Get all selected items
            if not selected_items:
                messagebox.showwarning("Warning", "Please select at least one record to delete")
                return'''
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete", "Delete This record?"):
                return

            try:
                connection = get_connection()
                cursor = connection.cursor()
                
                # Delete all selected records
                current_values = tree.item(row_id)['values']
                
                record_id = current_values[0]  # Assuming first column is ID
                cursor.execute(f"DELETE FROM {tab} WHERE id = ?", (record_id,))
                
                # Remove associated button frame
                if record_id in self.existing_button_frames:
                    self.existing_button_frames[record_id].destroy()
                    del self.existing_button_frames[record_id]

                connection.commit()
                messagebox.showinfo("Success", f"Deleted {row_id} record")
                
                # Refresh data
                fetch_all_data(tree, tab)

            except pyodbc.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete records: {str(e)}")
            finally:
                if 'connection' in locals():
                    connection.close()
        def update_selected(tree, tab, entries,row_id):
         

            item_values = tree.item(row_id)['values']
            if not item_values:
                return

            record_id = item_values[0]  # Assuming the first column is the unique ID
            new_values = [entries[3].get().strip(),entries[4].get().strip(),entries[5].get().strip(),entries[6].get().strip(),entries[7].get().strip()]
            if any(value == '' for value in new_values):
                messagebox.showwarning("Warning", "Please fill all fields")
                return

            query = f"UPDATE {tab} SET  full_name = ?, username = ?,password_v = ?,role = ?"
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute(query, (*new_values, record_id))
                connection.commit()

                # Clear entry fields after successful update
                for entry in entries:
                    entry.delete(0, tk.END)

                # Refresh treeview
                fetch_all_data(tree, tab)
                print("Record updated successfully.")
            except pyodbc.Error as e:
                print(f"Error: {e}")
        def update_popup(tree, tab,row_id):
            current_values = tree.item(row_id)['values']
            glac_num = current_values[0]
            # Fetch complete data using existing pattern
            query = """SELECT full_name, username, password_v,role 
                    FROM utilisateurs
                    
                    WHERE utilisateurs = ?"""
            
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute(query, (glac_num,))
                full_data = cursor.fetchone()
            except pyodbc.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch data: {str(e)}")
                return
            finally:
                if connection:
                    connection.close()
            print("THIS THE ROW ID ",row_id)
            # Create popup window
            popup = ctk.CTkToplevel()
            popup.title("Update Record")
            popup.geometry("600x450")
            popup.resizable(False, False)
            popup.transient(tree.winfo_toplevel())  # Make popup transient to main window
            popup.grab_set()  # Make popup modal
            popup.focus_set()
            
            # Create main frame with padding
            main_frame = ctk.CTkFrame(popup)
            main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
            # Grid configuration for responsive layout
            main_frame.grid_columnconfigure((0,1), weight=1)
            main_frame.grid_rowconfigure(4, weight=1)

            # Fields and entries
            fields = ["Nom complet","Nom Utilisateur", "Mot de passe", "Role"]
            entries = []

            # Create entries with improved layout
            for i, field in enumerate(fields):
                row = i // 2  # Integer division for row number
                col = i % 2   # Column number (0 or 1)
                
                # Container frame for each field
                field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
                
                label = ctk.CTkLabel(field_frame, text=field + ":", font=("poppins", 18))
                label.pack(anchor="w", pady=(0, 2))
                
                entry = ctk.CTkEntry(field_frame,placeholder_text=field,border_color="", font=("poppins", 13), width=220,height=40)
                entry.pack(fill="x")
                
                entries.append(entry)
                
            # Populate entries with current values
            for entry, value in zip(entries, full_data):
                
                entry.delete(0, 'end')
                entry.insert(0, str(value))
                

            # Button frame at bottom right
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="e")

            def confirm_update():
                update_selected(tree, tab, entries,row_id)
                popup.destroy()

            # Create buttons
            cancel_btn = ctk.CTkButton(
                button_frame, 
                text="Annuler",
                font=("Helvetica", 11),
                width=100,
                height=30,
                command=popup.destroy
            )
            cancel_btn.pack(side="right", padx=10)

            confirm_btn = ctk.CTkButton(
                button_frame, 
                text="Affecter",
                font=("Helvetica", 11),
                width=100,
                height=30,
                command=confirm_update
            )
            confirm_btn.pack(side="right")

            # Center the popup on screen
            popup.update_idletasks()
            x = (self.winfo_screenwidth() - popup.winfo_width()) // 2
            y = (self.winfo_screenheight() - popup.winfo_height()) // 2
            popup.geometry(f"+{x}+{y}")
        
            
        

            
        tab = "utilisateurs"
        # Style
        style = ttk.Style()
        #style.theme_use("classic")
        style.configure("Treeview", background="#050505", foreground="#b3b3b3",rowheight=35, fieldbackground="#050505",
        borderwidth=0,
        font=('Poppins', 12))
        style.configure("Treeview.Heading",  background="#171717",rowheight=50, foreground="#cccccc",relief="flat",borderwidth=0,
    font=('Poppins', 14, 'bold'),
    padding=5)
        
        
        # Add alternating row colors
        style.map("Treeview", 
        background=[('selected', '#455e88')],  # Blue background when selected
        foreground=[('selected', '#cccccc')],
        font=[('selected',('Poppins', 12, 'bold'))] )       
# Add this updated style configuration before creating the Treeview

    
    
# Hover and selection effects
        

        style.map("Treeview.Heading",
    background=[('active', '#333333')],
    relief=[('pressed', 'groove'), ('!pressed', 'groove')]
    )



# Modern scrollbar styling
        


# Then modify your Treeview creation to use the custom style:
        
        tree = ttk.Treeview(
    self.page_frame,
    columns=("col1", "col2", "col3", "col4", "col5", "col6"),
    show='headings',
    style="Treeview",
    selectmode="extended"
    )
        sort_direction = {
        "col1": None,
        "col2": None, 
        "col3": None,
        "col4": None,
        "col5": None,
        
        
    }   
        column_headings = {
    "col1": "ID",
    "col2": "Nom Complet",
    "col3": "Nom Utilisateur", 
    "col4": "Mot de passe",
    "col5": "Role",
    "col6": "Dernière Entrée",
        
    }
        ord_column_headings = {
    "col1": "id",
    "col2": "full_name",
    "col3": "username", 
    "col4": "password_v",
    "col5": "role",
    "col6": "last_login",
    }
    
        def treeview_sort_column(tree, col, tab):
    # Get the field name corresponding to the column
            field = ord_column_headings[col]
    
    # Toggle sort direction
            if sort_direction[col] is None or sort_direction[col] == 'DESC':
               sort_direction[col] = 'ASC'
            else:
               sort_direction[col] = 'DESC' 
    
    # Construct and execute SQL query with ORDER BY
            query = f"""
            SELECT id,full_name, username, password_v,role
                        FROM utilisateurs
                        
            ORDER BY {field} {sort_direction[col]}"""
            fetch_data(tree, query)
    
# Set column headings and properties
        for col, heading in column_headings.items():
            tree.heading(col, text=heading, anchor=tk.W,command=lambda c=col: treeview_sort_column(tree, c, tab))
            if col == "col1":
                tree.column(col, anchor=tk.W, width=60, minwidth=60)
            elif col == "col5":
                tree.column(col, anchor=tk.W, width=80, minwidth=80)
            else:
                tree.column(col, anchor=tk.W, width=180, minwidth=100)

 

# Configure horizontal scrollbar style
       
# Add these lines for alternating row colors
        tree.tag_configure('oddrow', background='#08090b')
        tree.tag_configure('evenrow', background='#050505')


      

        

# Configure the tree to use the scrollbars
        

# Grid layout for scrollbars
        tree.grid(row=1, column=0,  padx=(20,3), pady=5, sticky="nsew")
       
        # Fetch initial data
        fetch_all_data(tree, tab)
        
        self.search_entry=ctk.CTkEntry(self.buttons_frame,corner_radius=20,border_width=1,border_color="",placeholder_text="Search")
        self.search_entry.grid(row=0, column=0, pady=10,padx=(0,320),sticky="w",ipadx=150)
        self.search_entry.bind('<FocusIn>', lambda e, entry=self.search_entry: entry.configure(border_color="#561B8D"))
        self.search_entry.bind('<FocusOut>', lambda e, entry=self.search_entry: entry.configure(border_color=""))
        self.search_entry.bind('<KeyRelease>', lambda e: filter_search(tree))
        
        self.add_button = ctk.CTkButton(self.buttons_frame,width=25,height=25,text="Ajouter",image=self.add_icon,fg_color="#534ae1",corner_radius=30,compound="left",command=lambda: start_add_mode(tree, tab, ))
        self.add_button.grid(row=0, column=1, padx=10, pady=10,sticky="e")
        
        
        
        

        self.refresh_button = ctk.CTkButton(self.buttons_frame,width=30 ,text="Refresh",image=self.refresh_icon,compound="left",fg_color="transparent",corner_radius=30,command=lambda: fetch_all_data(tree, tab))
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10)
        
        
        
         
        
        
        






