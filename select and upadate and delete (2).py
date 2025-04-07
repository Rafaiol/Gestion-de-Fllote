import tkinter as tk
from tkinter import ttk
import pyodbc
import customtkinter as ctk
from tkinter import messagebox
import ttkbootstrap as bk
from ttkbootstrap.constants import * 
from ttkbootstrap.widgets import DateEntry


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


def start_add_mode(tree, tab, add_btn):
    
    # Create popup window
    popup = bk.Toplevel()
    popup.title("Add New Record")
    popup.geometry("700x400")
    popup.resizable(False, False)
    
    # Create main frame with padding
    main_frame = bk.Frame(popup, padding=20)
    main_frame.pack(expand=True, fill="both")

    # Fields for entries
    fields = ["Marque:", "Type:", "Immatriculation:", "Colour:", 
             "Mise On Circulation:", "Carburant:", "Service Utilisateur:", "Conducteur:"]
    entries = []

    # Create entries with labels in a grid layout
    for i, field in enumerate(fields):
        row = i // 2  # Integer division for row number
        col = i % 2   # Column number (0 or 1)
        
        # Container frame for each field
        field_frame = bk.Frame(main_frame,bootstyle="light", padding=10)
        field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        # Label above entry
        label = bk.Label(field_frame, text=field, font=("Helvetica", 11))
        label.pack(anchor="w", pady=(0, 2))
        
        # Entry field
         # Use DateEntry for "Mise On Circulation" field
        if field == "Mise On Circulation:":
            entry = DateEntry(field_frame, 
                            bootstyle="success",
                            firstweekday=0,
                            dateformat="%Y-%m-%d",
                            width=5,height=5)
        else:
            entry = bk.Entry(field_frame, font=("Helvetica", 11), width=35)
        entry.pack(fill="x")
        entries.append(entry)

    # Button frame
    button_frame = bk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky="e")

    def clear_entries():
        for entry in entries:
            entry.delete(0, 'end')

    def save_record():
        values = [entry.get().strip() for entry in entries]
        if any(value == '' for value in values):
            messagebox.showerror("Error", "Please fill all fields")
            return

        query = f"INSERT INTO {tab} (marque, type, Immatriculation, colour, [mise_on_circulation], carburant, [service_utilisateur], conducteur) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(query, values)
            connection.commit()
            
            # Refresh the treeview
            fetch_all_data(tree, tab)
            
            # Clear entries for new input
            clear_entries()
            
            messagebox.showinfo("Success", "Record added successfully")
            
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to add record: {str(e)}")

    # Create buttons
    cancel_btn = bk.Button(
        button_frame, 
        text="Cancel",
        bootstyle="secondary",
        command=popup.destroy,
        width=12
    )
    cancel_btn.pack(side="right", padx=5)

    clear_btn = bk.Button(
        button_frame, 
        text="Clear",
        bootstyle="warning",
        command=clear_entries,
        width=12
    )
    clear_btn.pack(side="right", padx=5)

    save_btn = bk.Button(
        button_frame, 
        text="Save",
        bootstyle="success",
        command=save_record,
        width=12
    )
    save_btn.pack(side="right", padx=5)

    # Center the popup on screen
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (300)
    y = (popup.winfo_screenheight() // 2) - (200)
    popup.geometry(f'+{x}+{y}')

def validate_add(tree, tab, item_id, add_btn):
    values = tree.item(item_id)['values']
    # Remove the first empty value (vehicule_id)
    values = values[1:] if values else []
    
    # Insert into database
    query = f"INSERT INTO {tab} (marque, type, Immatriculation, colour, [mise_on_circulation], carburant, [service_utilisateur], conducteur) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        
        # Refresh the treeview
        fetch_all_data(tree, tab)
        
        # Reset button
        add_btn.configure(text="Add New", command=lambda: start_add_mode(tree, tab, add_btn))
        
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Failed to add record: {str(e)}")
        tree.delete(item_id)

# Helper function to fetch and display data
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


# Fetch data by selected field and search value
def fetch_by_field(tree, tab, field, value):
    if not tab or not field:
        print("Please enter a table name and select a field.")
        return
    query = f"SELECT * FROM {tab} WHERE {field} LIKE ?"
    fetch_data(tree, query, (f"%{value}%",))


# Fetch all data
def fetch_all_data(tree, tab):
    if not tab:
        print("Please enter a table name.")
        return
    query = f"SELECT * FROM {tab}"
    fetch_data(tree, query)


# Add a new record to the database
def add_record(tab, entries):
    if not tab:
        print("Please enter a table name.")
        return
    values = [entry.get().strip() for entry in entries]
    if any(value == '' for value in values):
        print("Please fill in all fields.")
        return

    query = f"INSERT INTO {tab} (marque, type, Immatriculation, colour,[mise_on_circulation],carburant,[service_utilisateur],conducteur) VALUES (?, ?, ?, ?,?,?,?,?)"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()

        # Clear entry fields after successful addition
        for entry in entries:
            entry.delete(0, tk.END)

        print("Record added successfully.")
    except pyodbc.Error as e:
        print(f"Error: {e}")


# Delete the selected record
def delete_selected(tree, tab):
    selected_item = tree.selection()
    if not selected_item:
        print("No item selected.")
        return
    item_values = tree.item(selected_item)['values']
    if not item_values:
        return
    record_id = item_values[0]  # Assuming the first column is the unique ID

    query = f"DELETE FROM {tab} WHERE vehicule_id = ?"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (record_id,))
        connection.commit()
        tree.delete(selected_item)
        print("Record deleted successfully.")
    except pyodbc.Error as e:
        print(f"Error: {e}")
# Update the selected record
def update_selected(tree, tab, entries):
        selected_item = tree.selection()
        if not selected_item:
            print("No item selected.")
            return

        item_values = tree.item(selected_item)['values']
        if not item_values:
            return

        record_id = item_values[0]  # Assuming the first column is the unique ID
        new_values = [entry.get().strip() for entry in entries]
        if any(value == '' for value in new_values):
            print("Please fill in all fields.")
            return

        query = f"UPDATE {tab} SET marque = ?, type = ?, Immatriculation = ?, colour = ?,[mise_on_circulation] = ?, carburant = ?,[service_utilisateur] = ?, conducteur = ? WHERE vehicule_id = ?"
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
        print("No item selected.")
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
    fields = ["Marque:", "Type:", "Immatriculation:", "Colour:", 
             "Mise On Circulation:", "Carburant:", "Service Utilisateur:", "Conducteur:"]
    entries = []

    # Create entries with improved layout
    for i, field in enumerate(fields):
        row = i // 2  # Integer division for row number
        col = i % 2   # Column number (0 or 1)
        
        # Container frame for each field
        field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        label = ctk.CTkLabel(field_frame, text=field, font=("Helvetica", 11))
        label.pack(anchor="w", pady=(0, 2))
        
        entry = ctk.CTkEntry(field_frame, font=("Helvetica", 11), width=220,height=30)
        entry.pack(fill="x")
        entries.append(entry)

    # Populate entries with current values
    current_values = tree.item(selected_item)['values']
    for i, entry in enumerate(entries):
        entry.insert(0, str(current_values[i+1]))  # i+1 to skip ID

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
    x = (popup.winfo_screenwidth() // 2) - (300)
    y = (popup.winfo_screenheight() // 2) - (300)
    popup.geometry(f'600x600+{x}+{y}')

def on_tree_select(event, tree, update_entries):
    selected_item = tree.selection()
    if selected_item:
        # Get the values of the selected row
        values = tree.item(selected_item)['values']
        
        # Clear existing entries
        for entry in update_entries:
            entry.delete(0, tk.END)
            
        # Populate entries with selected row data
        for i, value in enumerate(values[1:], 0):
            update_entries[i].insert(0, str(value))

# Main function to display UI
def select():
    try:
        tab = table_entr.get().strip()
        if not tab:
          messagebox.showerror("Error", "Please enter a table name")
          return

        # Create a new window for displaying results
        top = tk.Toplevel(root)
        top.state('zoomed')  # This makes it full screen
        top.title("Data Viewer")
        top.configure(bg="#140036")
        top.resizable(False, False)  # Prevents window resizing

        top.grid_rowconfigure(0, weight=0)  # For buttons row
        top.grid_rowconfigure(1, weight=1)  # For treeview
        top.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)  # For all columns 
        # Style
        style = ttk.Style()
        style.theme_use("xpnative")
        style.configure("Treeview", background="white", foreground="black",rowhight=25, fieldbackground="white",bordercolor="#dee2e6",
    borderwidth=1,
    font=('Segoe UI', 10))
        style.configure("Treeview.Heading",  background="#f8f9fa", foreground="#212529",relief="flat",
    font=('Segoe UI', 11, 'bold'),
    padding=5)
        style.map("Treeview", background=[("selected", "#0d6efd")],foreground=[("selected", "white")])
        style.configure('TButton', 
                padding=5,
                background='#8E55C3',
                foreground='white',
                borderwidth=0,
                focuscolor='none'
            )
        
        # Add alternating row colors
        style.map("Treeview", 
          background=[('selected', '#347AB7')],  # Blue background when selected
          foreground=[('selected', 'white')])        
# Add this updated style configuration before creating the Treeview

      
       
# Hover and selection effects
        

        style.map("Treeview.Heading",
    background=[('active', '#e6e6e6')],
    relief=[('pressed', 'flat'), ('!pressed', 'flat')]
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
    top,
    columns=("col1", "col2", "col3", "col4", "col5", "col6", "col7", "col8", "col9"),
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
        "col7": None,
        "col8": None,
        "col9": None
}   
        column_headings = {
    "col1": "Vehicle ID",
    "col2": "Marque",
    "col3": "Type", 
    "col4": "Immatriculation",
    "col5": "Colour",
    "col6": "Mise On Circulation",
    "col7": "Carburant",
    "col8": "Service Utilisateur",
    "col9": "Conducteur"
}
        
       
        def treeview_sort_column(tree, col, tab):
    # Get the field name corresponding to the column
           field = column_headings[col]
    
    # Toggle sort direction
           if sort_direction[col] is None or sort_direction[col] == 'DESC':
             sort_direction[col] = 'ASC'
           else:
             sort_direction[col] = 'DESC' if sort_direction[col] == 'ASC' else 'ASC'
    
    # Construct and execute SQL query with ORDER BY
           query = f"SELECT * FROM {tab} ORDER BY {field} {sort_direction[col]}"
           fetch_data(tree, query)
    
# Set column headings and properties
        for col, heading in column_headings.items():
           tree.heading(col, text=heading, anchor=tk.CENTER,command=lambda c=col: treeview_sort_column(tree, c, tab))
           tree.column(col, anchor=tk.CENTER, width=150, minwidth=100)

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

# Create scrollbars
        '''
        v_scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(top, orient="horizontal", command=tree.xview, style="Horizontal.TScrollbar")
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)'''
        v_scrollbar = ttk.Scrollbar(
    top,
    orient="vertical",
    command=tree.yview,
    
)

        h_scrollbar = ttk.Scrollbar(
    top,
    orient="horizontal",
    command=tree.xview,
    
)

# Configure the tree to use the scrollbars
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

# Grid layout for scrollbars
        tree.grid(row=1, column=0, columnspan=8, sticky="nsew", padx=10, pady=10)
        v_scrollbar.grid(row=1, column=8, sticky="ns", pady=10)
        h_scrollbar.grid(row=2, column=0, columnspan=8, sticky="ew", padx=10)

 
         
        # Search by dropdown and entry
        search_label = bk.Label(top, text="Search Field:", font=("Helvetica", 12))
        search_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        field_combo = bk.Combobox(top, font=("Helvetica", 12), state="readonly")
        field_combo['values'] = ("Search by....","vehicule_id", "marque", "type", "Immatriculation", "colour", "mise_on_circulation", "carburant", "service_utilisateur", "conducteur")
        field_combo.current(0)
        field_combo.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        search_entry = bk.Entry(top, font=("Helvetica", 12))
        search_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        search_btn=bk.Button(top, text="Search", bootstyle="primary", command=lambda: fetch_by_field(tree, tab, field_combo.get(), search_entry.get()))
        search_btn.grid(row=0, column=4, padx=5, pady=5, sticky='w')
        display_btn=bk.Button(top, text="Displa All", bootstyle="info", command=lambda: fetch_all_data(tree, tab))
        display_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        # Buttons for Delete and Update
        delete_btn=bk.Button(top, text="Delete Selected", bootstyle="danger", command=lambda: delete_selected(tree, tab))
        delete_btn.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        add_btn = bk.Button(top, text="Add New", bootstyle="success", command=lambda: start_add_mode(tree, tab, add_btn))
        add_btn.grid(row=0, column=7, padx=5, pady=5, sticky='w')


        update_btn=bk.Button(top, text="Update Selected", bootstyle="warning", command=lambda: update_popup(tree, tab))
        update_btn.grid(row=0, column=6, padx=5, pady=5, sticky='w')
        

        
         

        # Fetch initial data
        fetch_all_data(tree, tab)
    except pyodbc.Error as e:
        print(f"Error: {e}")

def validate_add(tree, tab, item_id, add_btn):
    values = tree.item(item_id)['values']
    if not values or len(values) < 8:
        messagebox.showerror("Error", "Please fill all required fields")
        return
# Main application
root = bk.Window()
root.title("Database Operations")
root.geometry("500x200")
root.configure(bg="#140036")

# Table Entry
table_entr = bk.Entry(root, font=("Helvetica", 14))
table_entr.grid(row=0, column=0, padx=20, pady=10)

# Select Button
select_butn=bk.Button(root, text="Select Table",bootstyle="primary", command=select)
select_butn.grid(row=1, column=0, padx=20, pady=10)

root.mainloop()
