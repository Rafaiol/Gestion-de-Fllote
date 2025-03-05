import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import pyodbc
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MainPage(ctk.CTkFrame):
    def load_icon(self, path, size):
         """Load and resize an icon."""
         img =  Image.open(path)
         img_resized = img.resize(size, Image.Resampling.LANCZOS)
         return ImageTk.PhotoImage(img_resized) 
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)
        '''
        self.geometry("800x600")
        self.title("Vehiculs Page")'''
        self.add_icon = self.load_icon("Image_Assets/Addition.png", size=(25, 25))
        self.filter_icon = self.load_icon("Image_Assets/filtre.png", size=(25, 25))
        self.refresh_icon = self.load_icon("Image_Assets/Refresh.png", size=(25, 25))
        self.search_icon = self.load_icon("Image_Assets/search.png", size=(25, 25))
        self.supprimer_icon = self.load_icon("Image_Assets/supprimer.png", size=(25, 25))
        
        self.page_frame = ctk.CTkFrame(self, corner_radius=10)
        self.page_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure(1, weight=1)
       
        
        
        
        self.buttons_frame = ctk.CTkFrame(self.page_frame, corner_radius=20,height=80)
        self.buttons_frame.grid(row=0,column=0,columnspan=2, padx=10,pady=10,sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        
        self.right_buttons_frame = ctk.CTkFrame(self.page_frame,fg_color="red" ,corner_radius=5,width=100,height=40)
        self.right_buttons_frame.grid(row=1,column=1,padx=(3,3) ,pady=10,sticky="nsew")
        
        
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
        def get_vehicles():
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT vehicule_id,marque, type, Immatriculation FROM véhicule")
                vehicules = cursor.fetchall()
                return [f"{vehicule[2]}" for vehicule in vehicules], vehicules
            except pyodbc.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch vehicles: {str(e)}")
                return [], []

        
        def start_add_mode(tree, tab,add_button):
            def on_vehicule_select(selected_vehicle):
                        global vehicule_id
                        for vehicule in vehicle_data:   
                            if vehicule[2] == selected_vehicle:
                                entries[2].configure(state="normal")  # Enable entry temporarily
                                entries[2].delete(0, 'end')
                                entries[2].insert(0, vehicule[1])
                                entries[2].configure(state="readonly")  # Set back to readonly
                                
                                entries[3].configure(state="normal")
                                entries[3].delete(0, 'end')
                                entries[3].insert(0, vehicule[3])
                                entries[3].configure(state="readonly")  # Immatriculation
                        return vehicule[0]
                                
            # Create popup window
            popup = ctk.CTkToplevel()
            popup.title("Add New Record")
            popup.geometry("700x400")
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
            fields = ["Numero de Glaciol", "Type:","Marque", "Immatriculation", "Date de Glaciol", "Litre"]
            entries = []
            vehicle_names, vehicle_data = get_vehicles()
            
            
            # Create entries with improved layout
            for i,field in enumerate(fields):
                row = i // 2  # Integer division for row number
                col = i % 2   # Column number (0 or 1)
                
                # Container frame for each field
                field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
                label = ctk.CTkLabel(field_frame, text=field + ":", font=("Helvetica", 18))
                label.pack(anchor="w", pady=(0, 2))
                
                if field == "Type:":
                    type_combo = ctk.CTkComboBox(field_frame,
                                        values=vehicle_names,
                                        font=("poppins", 13),
                                        width=220,
                                        height=30,
                                        corner_radius=8,
                                        border_width=2, 
                                        state="readonly",
                                        command=on_vehicule_select,)
                    
                    type_combo.pack(fill="x")
                    entries.append(type_combo)
                    type_combo.bind('<FocusIn>', lambda : type_combo.configure(border_color="#561B8D"))
                    
                    
                    
                else:
                    entry = ctk.CTkEntry(field_frame, font=("Helvetica", 13),placeholder_text=field, width=220,border_color="", height=40)
                    entry.pack(fill="x")
                    entries.append(entry)
                    if not fields[i] in ["Marque","Type", "Immatriculation"]:
                        entry.bind('<FocusIn>', lambda e, entry=entry: entry.configure(border_color="#561B8D"))
                        entry.bind('<FocusOut>', lambda e, entry=entry: entry.configure(border_color=""))
                
            
            
            

            # Button frame
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky="e")

            def save_record(): 
                vehicule_id = on_vehicule_select(type_combo.get())
                print(vehicule_id)
                values = [entries[0].get().strip(),vehicule_id,entries[4].get().strip(),entries[5].get().strip() ]
                if any(value == '' for value in values):
                    messagebox.showerror("Error", "Please fill all fields")
                    return
                
                query = "INSERT INTO Glaciol (Num_glaciol,vehicule_id,date_glac, litre) VALUES (?, ?, ?, ?)"
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

            # Clear Treeview before inserting new data
            for item in tree.get_children():
                tree.delete(item)

            # Insert fetched data into the Treeview
            for i, row in enumerate(data):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                tree.insert('', 'end', values=[str(item) for item in row], tags=(tag,))
            # Add striped row colors
            tree.tag_configure('oddrow', background="#f0f0f0")
            tree.tag_configure('evenrow', background="white")


            cursor.close()
            connection.close()
         except pyodbc.Error as e:
            print(f"Error: {e}")
        
        def fetch_by_field(tree, tab):
         
         top=ctk.CTkToplevel()
         top.title("Update Record")
         top.geometry("600x100")
         top.resizable(False, False)
         top.transient(tree.winfo_toplevel())  # Make popup transient to main window
         top.grab_set()  # Make popup modal
         top.focus_set()
         field_mapping = {
                "Search by...": None,
                "Marque": "marque", 
                "Véhicle Type": "type",
                "Immatriculation": "Immatriculation",
                "Date Glaciol": "date_glac",
                "Litre": "litre",
                
            }
         entry = ctk.CTkEntry(top)
         entry.grid(row=0, column=0, pady=10,sticky="ew",ipadx=150)
         entry.bind('<FocusIn>', lambda e, entry=entry: entry.configure(border_color="#561B8D"))
         entry.bind('<FocusOut>', lambda e, entry=entry: entry.configure(border_color=""))
         field_combo = ctk.CTkComboBox(top, font=("Helvetica", 12), state="readonly",
                                       values=list(field_mapping.keys()))
         field_combo.set("search by...")
         field_combo.grid(row=0, column=1, pady=10, sticky='ew')
         search_btn = ctk.CTkButton(top, text="Search", command=lambda :search(field_combo.get(),entry.get()))
         search_btn.grid(row=1, column=0, pady=10, padx=10, sticky='n',columnspan=2,ipadx=50)
         def search(field,value):
                    if field == "Search by...":
                        messagebox.showwarning("Warning", "Please select a search field")
                    else:
                        db_field = field_mapping[field]
                        query = f'''SELECT g.num_glaciol, v.marque, v.type, v.Immatriculation,g.date_glac,g.litre  
                        FROM véhicule v
                        INNER JOIN glaciol g ON v.vehicule_id = g.vehicule_id WHERE {db_field} LIKE ?'''
                        fetch_data(tree, query, (f"%{value}%",))
                        top.destroy()
        
        def filter_by_field(tree,tab):
            filt=ctk.CTkToplevel(fg_color=("gray85", "gray20"))
            filt.attributes('-alpha', 0.95)
            filt.title("Update Record")
            filt.geometry("600x100")
            filt.resizable(False, False)
            filt.transient(tree.winfo_toplevel())  # Make popup transient to main window
            filt.grab_set()  # Make popup modal
            filt.focus_set()
            field_mapping = {
                "Search by...": None,
                
                "Marque": "marque", 
                "Vehicle Type": "type",
                "Immatriculation": "Immatriculation",
                "Date de Glaciol": "date_glac",
                "Litre":"litre"
            }
            def on_entry_change(*args):
              display_field = field_combo.get()
              
        
              if display_field == "Search by...":
                messagebox.showwarning("Warning", "Please select a search field")
                return
              if display_field in field_mapping and field_mapping[display_field]:
                db_field = field_mapping[display_field]  # Get actual field name
                value = entry.get()
                query = f'''SELECT  g.num_glaciol,v.marque, v.type, v.Immatriculation,g.date_glac,g.litre  
                        FROM véhicule v
                        INNER JOIN glaciol g ON v.vehicule_id = g.vehicule_id WHERE {db_field} LIKE ?'''
                fetch_data(tree, query, (f"%{value}%",))
            entry = ctk.CTkEntry(filt)
            entry.grid(row=0, column=0, pady=10,sticky="ew",ipadx=150)
            entry.bind('<FocusIn>', lambda e, entry=entry: entry.configure(border_color="#561B8D"))
            entry.bind('<FocusOut>', lambda e, entry=entry: entry.configure(border_color=""))
            field_combo = ctk.CTkComboBox(filt, font=("Helvetica", 12), state="readonly",
                                        values=list(field_mapping.keys()))
            field_combo.set("search by...")
            field_combo.grid(row=0, column=1, pady=10, sticky='ew')
            entry.bind('<KeyRelease>', on_entry_change)
            
            
                            
                
# Fetch all data
        def fetch_all_data(tree, tab):
            if not tab:
                print("Please enter a table name.")
                return
            query = """
                SELECT  g.num_glaciol, v.marque, v.type, v.Immatriculation,g.date_glac,g.litre  
                        FROM véhicule v
                        INNER JOIN glaciol g ON v.vehicule_id = g.vehicule_id
                """
            fetch_data(tree, query)

        
        def delete_selected(tree, tab):
          selected_item = tree.selection()
          if not selected_item:
            print("No item selected.")
            return
          item_values = tree.item(selected_item)['values']
          if not item_values:
            return
          record_id = item_values[0]  # Assuming the first column is the unique ID

          query = f"DELETE FROM {tab} WHERE num_glaciol = ?"
          try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (record_id,))
            connection.commit()
            tree.delete(selected_item)
            print("Record deleted successfully.")
          except pyodbc.Error as e:
            print(f"Error: {e}")
        def update_selected(tree, tab, entries):
         selected_item = tree.selection()
         if not selected_item:
            print("No item selected.")
            return

         item_values = tree.item(selected_item)['values']
         if not item_values:
            return

         record_id = item_values[0]  # Assuming the first column is the unique ID
         new_values = [entries[0].get().strip(),entries[4].get().strip(),entries[5].get().strip()]
         if any(value == '' for value in new_values):
            messagebox.showwarning("Warning", "Please fill all fields")
            return

         query = f"UPDATE {tab} SET num_glaciol = ?, date_glac = ?, litre = ? WHERE num_glaciol = ?"
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
        def update_popup(tree, tab):
         selected_item = tree.selection()
         if not selected_item:
           messagebox.showwarning("Warning", "Please select a field to update")
           return
    # Create popup window
         popup = ctk.CTkToplevel()
         popup.title("Update Record")
         popup.geometry("600x400")
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
         fields = ["Numero de Glaciol","Marque", "Type", "Immatriculation", "Date Glaciol", "Litre"]
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
            if not fields[i] in ["Marque","Type", "Immatriculation"]:
                entry.bind('<FocusIn>', lambda e, entry=entry: entry.configure(border_color="#561B8D"))
                entry.bind('<FocusOut>', lambda e, entry=entry: entry.configure(border_color=""))
        
        # Populate entries with current values
         current_values = tree.item(selected_item)['values']
         for i, entry in enumerate(entries):
            entry.insert(0, str(current_values[i]))  # i+1 to skip ID
            if fields[i] in ["Marque:","Type:", "Immatriculation:"]:
              entry.configure(state="readonly")
        # Button frame at bottom right
         button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
         button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="e")

         def confirm_update():
            update_selected(tree, tab, entries)
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
        
        tab = "Glaciol"
        # Style
        style = ttk.Style()
        
        style.configure("Treeview", background="white", foreground="black",rowhight=5, fieldbackground="white",bordercolor="#dee2e6",
        borderwidth=8,
        font=('Segoe UI', 14))
        style.configure("Treeview.Heading",  background="#f8f9fa", foreground="#212529",relief="flat",
    font=('Segoe UI', 11, 'bold'),
    padding=5)
        style.map("Treeview", background=[("selected", "#0d6efd")],foreground=[("selected", "white")])
        
        # Add alternating row colors
        style.map("Treeview", 
        background=[('selected', '#347AB7')],  # Blue background when selected
        foreground=[('selected', 'white')])        
# Add this updated style configuration before creating the Treeview

    
    
# Hover and selection effects
        

        style.map("Treeview.Heading",
    background=[('active', '#e6e6e6')],
    relief=[('pressed', 'groove'), ('!pressed', 'groove')]
    )



# Modern scrollbar styling
        style.configure("Treeview.Scrollbar",
    troughcolor="#f0f0f0",
    background="#c1c1c1",
    borderwidth=0,
    relief="flat"
)


# Then modify your Treeview creation to use the custom style:
        
        tree = ttk.Treeview(
    self.page_frame,
    columns=("col1", "col2", "col3", "col4", "col5", "col6","col7"),
    show='headings',
    style="Treeview"
    )
        sort_direction = {
        "col1": None,
        "col2": None, 
        "col3": None,
        "col4": None,
        "col5": None,
        "col6": None,
        
    }   
        column_headings = {
    "col1": "Numero",
    "col2": "Marque",
    "col3": "Type", 
    "col4": "Immatriculation",
    "col5": "Date de Glaciol",
    "col6": "Litre",
    "col7":"Actions    "
    }
        ord_column_headings = {
    "col1": "num_glaciol",
    "col2": "Marque",
    "col3": "Type", 
    "col4": "Immatriculation",
    "col5": "date_glac",
    "col6": "litre",
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
            SELECT g.num_glaciol, v.marque, v.type, v.Immatriculation,g.date_glac,g.litre  
                        FROM véhicule v
                        INNER JOIN glaciol g ON v.vehicule_id = g.vehicule_id
            ORDER BY {field} {sort_direction[col]}"""
            fetch_data(tree, query)
    
# Set column headings and properties
        for col, heading in column_headings.items():
            tree.heading(col, text=heading, anchor=tk.CENTER,command=lambda c=col: treeview_sort_column(tree, c, tab))
            tree.column(col, anchor=tk.W, width=150, minwidth=100)

        style.configure("Vertical.TScrollbar",
    background="#c1c1c1",
    troughcolor="#f0f0f0",
    width=16,
    )

# Configure horizontal scrollbar style
        style.configure("Horizontal.TScrollbar",
    background="#c1c1c1", 
    troughcolor="#f0f0f0",
    width=16,
    
    )
# Add these lines for alternating row colors
        tree.tag_configure('oddrow', background='#f9f9f9')
        tree.tag_configure('evenrow', background='#ffffff')


        v_scrollbar = ttk.Scrollbar(
    self.page_frame,
    orient="vertical",
    command=tree.yview,
    
    )

        h_scrollbar = ttk.Scrollbar(
    self.page_frame,
    orient="horizontal",
    command=tree.xview,
    
    )
        

# Configure the tree to use the scrollbars
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

# Grid layout for scrollbars
        tree.grid(row=1, column=0,  padx=(20,3), pady=5, sticky="nsew")
        v_scrollbar.grid(row=1, column=8, sticky="ns", pady=10)
        h_scrollbar.grid(row=2, column=0, columnspan=8, sticky="ew", padx=20)

        # Fetch initial data
        fetch_all_data(tree, tab)
        
         
        self.add_button = ctk.CTkButton(self.buttons_frame,width=25,height=25,text="",image=self.add_icon,fg_color="green",command=lambda: start_add_mode(tree, tab, self.add_button))
        self.add_button.grid(row=0, column=0, padx=10, pady=10,sticky="w")
        
        self.search_button = ctk.CTkButton(self.buttons_frame, width=25,height=25,text="",image=self.search_icon,compound="left", command=lambda: fetch_by_field(tree, tab))
        self.search_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.update_button = ctk.CTkButton(self.buttons_frame, text="Update",command=lambda: update_popup(tree, tab))
        self.update_button.grid(row=0, column=3, padx=10, pady=10)
        
        self.filter_button = ctk.CTkButton(self.buttons_frame,width=25,height=25,text="",image=self.filter_icon,compound="left",fg_color="gray", command=lambda: filter_by_field(tree, tab))
        self.filter_button.grid(row=0, column=4, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.buttons_frame,width=25,height=25,text="",image=self.supprimer_icon,compound="left",fg_color="red", command=lambda: delete_selected(tree, tab))
        self.delete_button.grid(row=0, column=5, padx=10, pady=10)
        
        self.refresh_button = ctk.CTkButton(self.buttons_frame, text="Refresh",command=lambda: fetch_all_data(tree, tab))
        self.refresh_button.grid(row=0, column=1, padx=10, pady=10)
        
        
        
         
        
        
        






'''

if __name__ == "__main__":
    app = MainPage()

    app.mainloop()'''
