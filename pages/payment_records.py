import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import platform
import os
import subprocess
import pandas as pd

class PaymentRecordsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Payment Records")
        
        # Set dialog size
        dialog_width = 1000
        dialog_height = 600
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position for center of screen
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # Set size and position
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_header()
        self.create_filters()
        self.create_payment_table()
        self.create_action_buttons()
        self.load_payments()
    
    def create_header(self):
        # Title
        title = ttk.Label(self,
                         text="Payment Records",
                         style="Title.TLabel")
        title.pack(pady=10)
    
    def create_filters(self):
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date = ttk.Entry(filter_frame, width=10)
        self.from_date.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=(20, 5))
        self.to_date = ttk.Entry(filter_frame, width=10)
        self.to_date.pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame,
                               textvariable=self.search_var,
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Filter button
        filter_btn = ttk.Button(filter_frame,
                              text="Filter",
                              style="Modern.TButton",
                              command=self.apply_filters)
        filter_btn.pack(side=tk.LEFT, padx=20)
    
    def create_payment_table(self):
        # Table frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("PaymentTable.Treeview.Heading",
                       background='gray85',
                       font=("Helvetica", 10, "bold"),
                       padding=5)
        style.configure("PaymentTable.Treeview",
                       font=("Helvetica", 10),
                       rowheight=30)
        
        # Create Treeview
        columns = ("date", "student", "amount", "receipt")
        self.payment_tree = ttk.Treeview(table_frame,
                                       columns=columns,
                                       show="headings",
                                       style="PaymentTable.Treeview")
        
        # Configure columns with exact widths
        column_configs = {
            "date": {
                "width": 180, "minwidth": 150, "stretch": True, 
                "anchor": "center", "text": "Payment Date"
            },
            "student": {
                "width": 300, "minwidth": 200, "stretch": True, 
                "anchor": "center", "text": "Student Name"
            },
            "amount": {
                "width": 200, "minwidth": 150, "stretch": True, 
                "anchor": "center", "text": "Amount"
            },
            "receipt": {
                "width": 200, "minwidth": 150, "stretch": True, 
                "anchor": "center", "text": "Receipt Number"
            }
        }
        
        # Apply configurations and set up sorting
        for col, config in column_configs.items():
            self.payment_tree.heading(
                col, 
                text=config["text"],
                anchor=config["anchor"],
                command=lambda c=col: self.sort_treeview(c)
            )
            self.payment_tree.column(
                col,
                width=config["width"],
                minwidth=config["minwidth"],
                stretch=config["stretch"],
                anchor=config["anchor"]
            )
        
        # Add alternating row colors
        style.configure("PaymentTable.Treeview", 
                       background="white",
                       fieldbackground="white",
                       selectbackground="#0078D7",
                       selectforeground="white")
        
        self.payment_tree.tag_configure('oddrow', background='#F5F5F5')
        
        # Add horizontal and vertical scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame,
                                   orient=tk.VERTICAL,
                                   command=self.payment_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame,
                                   orient=tk.HORIZONTAL,
                                   command=self.payment_tree.xview)
        
        self.payment_tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Pack widgets with proper spacing
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Enable column resizing by dragging
        self.payment_tree.bind('<Motion>', self.check_resize_cursor)
        self.payment_tree.bind('<Button-1>', self.start_resize)
        self.payment_tree.bind('<B1-Motion>', self.do_resize)
        self.payment_tree.bind('<ButtonRelease-1>', self.end_resize)
        
        # Bind double-click to view receipt
        self.payment_tree.bind("<Double-1>", self.view_receipt)
        
        # Initialize sorting variables
        self.sort_column = None
        self.sort_reverse = False
    
    def check_resize_cursor(self, event):
        """Change cursor when over column divider"""
        region = self.payment_tree.identify_region(event.x, event.y)
        if region == "separator":
            self.payment_tree.configure(cursor="sb_h_double_arrow")
        else:
            self.payment_tree.configure(cursor="")
    
    def start_resize(self, event):
        """Start column resize operation"""
        region = self.payment_tree.identify_region(event.x, event.y)
        if region == "separator":
            self.resize_column = self.payment_tree.identify_column(event.x)
            self.resize_x = event.x
    
    def do_resize(self, event):
        """Handle column resize drag"""
        if hasattr(self, 'resize_column'):
            diff = event.x - self.resize_x
            x = self.payment_tree.column(self.resize_column, "width") + diff
            if x > 50:  # Minimum column width
                self.payment_tree.column(self.resize_column, width=x)
                self.resize_x = event.x
    
    def end_resize(self, event):
        """End column resize operation"""
        if hasattr(self, 'resize_column'):
            del self.resize_column
            del self.resize_x
    
    def sort_treeview(self, col):
        """Sort treeview when column header is clicked"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        items = [(self.payment_tree.set(item, col), item) 
                 for item in self.payment_tree.get_children('')]
        
        # Custom sorting for amount column
        if col == "amount":
            items.sort(key=lambda x: float(x[0].replace('₦', '').replace(',', '')), 
                      reverse=self.sort_reverse)
        # Custom sorting for date column
        elif col == "date":
            items.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y %H:%M'), 
                      reverse=self.sort_reverse)
        else:
            items.sort(reverse=self.sort_reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.payment_tree.move(item, '', index)
            # Reapply alternating row colors
            tags = ('oddrow',) if index % 2 else ()
            self.payment_tree.item(item, tags=tags)
    
    def create_action_buttons(self):
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Export button
        export_btn = ttk.Button(button_frame,
                              text="Export to Excel",
                              style="Modern.TButton",
                              command=self.export_to_excel)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Print button
        print_btn = ttk.Button(button_frame,
                             text="Print Records",
                             style="Modern.TButton",
                             command=self.print_records)
        print_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(button_frame,
                             text="Close",
                             style="Modern.TButton",
                             command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def export_to_excel(self):
        try:
            # Try importing required packages
            try:
                import pandas as pd
                import openpyxl
            except ImportError:
                messagebox.showerror("Missing Dependencies", 
                                   "Please install required packages:\n\n"
                                   "pip install pandas openpyxl")
                return
            
            # Get all payments
            payments = self.app.db.get_all_payments()
            
            # Create DataFrame
            df = pd.DataFrame(payments)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"payment_records_{timestamp}.xlsx"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            # Ensure exports directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Export to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            messagebox.showinfo("Success", 
                              f"Records exported successfully to:\n{filepath}")
            
            # Open the file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
                
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Failed to export records: {str(e)}\n\n"
                               "Please ensure you have installed required packages:\n"
                               "pip install pandas openpyxl")
    
    def print_records(self):
        try:
            # Try importing required packages
            try:
                import pandas as pd
                import openpyxl
            except ImportError:
                messagebox.showerror("Missing Dependencies", 
                                   "Please install required packages:\n\n"
                                   "pip install pandas openpyxl")
                return
            
            # First export to Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"payment_records_{timestamp}.xlsx"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            # Create DataFrame
            payments = self.app.db.get_all_payments()
            df = pd.DataFrame(payments)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            # Print the file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['lpr', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath, 'print')
            else:  # Linux
                subprocess.run(['lpr', filepath])
                
            messagebox.showinfo("Success", "Records sent to printer")
            
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Failed to print records: {str(e)}\n\n"
                               "Please ensure you have installed required packages:\n"
                               "pip install pandas openpyxl")
    
    def load_payments(self):
        # Clear existing items
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        # Get all payments
        payments = self.app.db.get_all_payments()
        
        # Add to treeview with alternating colors
        for i, payment in enumerate(payments):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values with proper spacing
            values = (
                # Center-aligned date
                datetime.strptime(payment['payment_date'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M'),
                # Center-aligned name
                payment['student_name'].center(40),
                # Right-aligned amount with padding
                f"₦{payment['amount']:,.2f}".rjust(15),
                # Center-aligned receipt number
                payment['receipt_number'].center(20)
            )
            
            self.payment_tree.insert("", "end", values=values, tags=tags)
    
    def apply_filters(self):
        # TODO: Implement filters
        pass
    
    def view_receipt(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
        
        try:
            receipt_number = self.payment_tree.item(selected[0])['values'][3]
            receipt = self.app.db.get_receipt_by_number(receipt_number)
            
            if not receipt:
                messagebox.showerror("Error", "Receipt record not found in database")
                return
            
            if not os.path.exists(receipt['filepath']):
                messagebox.showerror("Error", 
                                   f"Receipt file not found at: {receipt['filepath']}")
                return
            
            # Open receipt file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', receipt['filepath']])
            elif platform.system() == 'Windows':
                os.startfile(receipt['filepath'])
            else:  # Linux
                subprocess.run(['xdg-open', receipt['filepath']])
            
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Failed to open receipt: {str(e)}\n\n"
                               f"Details: {type(e).__name__}") 