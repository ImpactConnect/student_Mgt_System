import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.constants import PROGRAMMES
import platform
import os
import subprocess

class PaymentHistoryPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main layout
        self.create_header()
        self.create_stats_section()
        self.create_filters()
        self.create_payment_table()
        self.load_payments()
        
    def create_header(self):
        # Header with back button and title
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button
        back_btn = ttk.Button(header_frame,
                            text="← Back",
                            command=self.app.show_home_page)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # Title
        title = ttk.Label(header_frame,
                         text="Payment History",
                         style="Title.TLabel")
        title.pack(pady=10)
    
    def create_stats_section(self):
        # Stats frame
        stats_frame = ttk.LabelFrame(self, text="Payment Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Get system background color
        system_bg = self.winfo_toplevel().cget('bg')
        
        # Get statistics from database
        stats = self.app.db.get_payment_statistics()
        
        # Create grid of stats with styling
        stats_data = [
            # First row - Financial stats
            [
                {
                    "title": "Total Programme Fees",
                    "value": f"₦{stats['total_fees']:,.2f}",
                    "title_color": "#1976D2",  # Blue
                    "value_color": "#1565C0"   # Darker blue
                },
                {
                    "title": "Total Revenue",
                    "value": f"₦{stats['total_revenue']:,.2f}",
                    "title_color": "#2E7D32",  # Green
                    "value_color": "#1B5E20"   # Darker green
                },
                {
                    "title": "Total Outstanding",
                    "value": f"₦{stats['total_outstanding']:,.2f}",
                    "title_color": "#C62828",  # Red
                    "value_color": "#B71C1C",   # Darker red
                    "has_button": True  # Flag to add button
                }
            ],
            # Second row - Performance stats
            [
                {
                    "title": "Collection Rate",
                    "value": f"{stats['collection_rate']:.1f}%",
                    "title_color": "#7B1FA2",  # Purple
                    "value_color": "#6A1B9A"   # Darker purple
                },
                {
                    "title": "Total Students",
                    "value": str(stats['total_students']),
                    "title_color": "#F57C00",  # Orange
                    "value_color": "#EF6C00"   # Darker orange
                },
                {
                    "title": "Fully Paid Students",
                    "value": str(stats['fully_paid_students']),
                    "title_color": "#00838F",  # Cyan
                    "value_color": "#006064"   # Darker cyan
                }
            ]
        ]
        
        # Create each row of stats
        for row_idx, row in enumerate(stats_data):
            for col_idx, stat in enumerate(row):
                frame = ttk.Frame(stats_frame)
                frame.grid(row=row_idx*2, column=col_idx, padx=10, pady=5, sticky="nsew")
                
                # Title label with custom color
                title_label = tk.Label(frame,
                                     text=stat["title"],
                                     font=("Helvetica", 10),
                                     fg=stat["title_color"],
                                     bg=system_bg)
                title_label.pack(anchor="center")
                
                # Value label with custom color and bold font
                value_label = tk.Label(frame,
                                     text=stat["value"],
                                     font=("Helvetica", 12, "bold"),
                                     fg=stat["value_color"],
                                     bg=system_bg)
                value_label.pack(anchor="center")
                
                # Add Outstanding Payments button if this is the Total Outstanding stat
                if stat.get("has_button"):
                    ttk.Button(frame,
                              text="View Details",
                              command=self.show_outstanding_payments).pack(pady=(5, 0))
                
            # Add separator between rows (except after last row)
            if row_idx < len(stats_data) - 1:
                separator = ttk.Separator(stats_frame, orient="horizontal")
                separator.grid(row=row_idx*2 + 1, column=0, columnspan=3, 
                             sticky="ew", pady=10, padx=5)
        
        # Configure grid columns
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)
    
    def create_filters(self):
        # Filters frame
        filters_frame = ttk.LabelFrame(self, text="Filters", padding=10)
        filters_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Left frame for date filters
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date range filters
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date = ttk.Entry(date_frame, width=12)
        self.from_date.pack(side=tk.LEFT, padx=(0, 20))
        self.from_date.insert(0, "YYYY-MM-DD")
        self.from_date.bind("<FocusIn>", lambda e: self.from_date.delete(0, tk.END))
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
        self.to_date = ttk.Entry(date_frame, width=12)
        self.to_date.pack(side=tk.LEFT, padx=(0, 20))
        self.to_date.insert(0, "YYYY-MM-DD")
        self.to_date.bind("<FocusIn>", lambda e: self.to_date.delete(0, tk.END))
        
        # Right frame for other filters
        filter_frame = ttk.Frame(filters_frame)
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Programme filter
        ttk.Label(filter_frame, text="Programme:").pack(side=tk.LEFT, padx=(0, 5))
        self.programme_var = tk.StringVar(value="All")
        programme_combo = ttk.Combobox(filter_frame,
                                     textvariable=self.programme_var,
                                     values=["All"] + PROGRAMMES,
                                     state="readonly",
                                     width=30)
        programme_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Search box
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame,
                               textvariable=self.search_var,
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Buttons frame
        button_frame = ttk.Frame(filters_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Apply filters button
        ttk.Button(button_frame,
                   text="Apply Filters",
                   command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        
        # Clear filters button
        ttk.Button(button_frame,
                   text="Clear Filters",
                   command=self.clear_filters).pack(side=tk.LEFT, padx=5)
        
        # Export button
        ttk.Button(button_frame,
                   text="Export to Excel",
                   command=self.export_payments).pack(side=tk.LEFT, padx=5)
    
    def apply_filters(self):
        try:
            # Validate dates if provided
            from_date = None
            to_date = None
            if self.from_date.get() and self.from_date.get() != "YYYY-MM-DD":
                from_date = datetime.strptime(self.from_date.get(), '%Y-%m-%d')
            if self.to_date.get() and self.to_date.get() != "YYYY-MM-DD":
                to_date = datetime.strptime(self.to_date.get(), '%Y-%m-%d')
            
            self.load_payments(from_date, to_date)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
    
    def clear_filters(self):
        self.from_date.delete(0, tk.END)
        self.from_date.insert(0, "YYYY-MM-DD")
        self.to_date.delete(0, tk.END)
        self.to_date.insert(0, "YYYY-MM-DD")
        self.programme_var.set("All")
        self.search_var.set("")
        self.load_payments()
    
    def export_payments(self):
        try:
            filepath = self.app.db.export_payments_to_excel(
                programme=self.programme_var.get() if self.programme_var.get() != "All" else None,
                search_term=self.search_var.get(),
                from_date=self.from_date.get() if self.from_date.get() != "YYYY-MM-DD" else None,
                to_date=self.to_date.get() if self.to_date.get() != "YYYY-MM-DD" else None
            )
            
            messagebox.showinfo("Success", f"Payments exported successfully to:\n{filepath}")
            
            # Open the exported file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export payments: {str(e)}")
    
    def create_payment_table(self):
        # Create Treeview with style
        style = ttk.Style()
        style.configure("PaymentHistory.Treeview.Heading",
                       background='gray85',
                       font=("Helvetica", 10, "bold"),
                       padding=5)
        style.configure("PaymentHistory.Treeview",
                       font=("Helvetica", 10),
                       rowheight=30)
        
        # Create Treeview
        columns = ("date", "student", "amount", "receipt")
        self.payment_tree = ttk.Treeview(self,
                                       columns=columns,
                                       show="headings",
                                       style="PaymentHistory.Treeview")
        
        # Configure columns
        column_configs = {
            "date": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Payment Date"
            },
            "student": {
                "width": 200, "minwidth": 200, "stretch": True,
                "anchor": "w", "text": "Student Name"
            },
            "amount": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "e", "text": "Amount"
            },
            "receipt": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Receipt Number"
            }
        }
        
        # Apply configurations
        for col, config in column_configs.items():
            self.payment_tree.heading(
                col,
                text=config["text"],
                anchor=config["anchor"]
            )
            self.payment_tree.column(
                col,
                width=config["width"],
                minwidth=config["minwidth"],
                stretch=config["stretch"],
                anchor=config["anchor"]
            )
        
        # Add alternating row colors
        self.payment_tree.tag_configure('oddrow', background='#F5F5F5')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self,
                                orient=tk.VERTICAL,
                                command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view receipt
        self.payment_tree.bind("<Double-1>", self.view_receipt)
    
    def load_payments(self, from_date=None, to_date=None):
        # Clear existing items
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        # Get all payments
        payments = self.app.db.get_all_payments()
        
        # Apply filters
        programme_filter = self.programme_var.get()
        search_term = self.search_var.get().lower()
        
        filtered_payments = []
        for payment in payments:
            # Programme filter
            if programme_filter != "All" and payment['programme'] != programme_filter:
                continue
            
            # Search filter
            if search_term and search_term not in payment['student_name'].lower() and \
               search_term not in payment.get('programme', '').lower():
                continue
            
            # Date filter
            payment_date = datetime.strptime(payment['payment_date'], '%Y-%m-%d %H:%M:%S')
            if from_date and payment_date.date() < datetime.strptime(from_date, '%Y-%m-%d').date():
                continue
            if to_date and payment_date.date() > datetime.strptime(to_date, '%Y-%m-%d').date():
                continue
            
            filtered_payments.append(payment)
        
        # Add to treeview with alternating colors
        for i, payment in enumerate(filtered_payments):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values
            values = (
                datetime.strptime(payment['payment_date'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M'),
                payment['student_name'],
                f"₦{payment['amount']:,.2f}",
                payment['receipt_number']
            )
            
            self.payment_tree.insert("", "end", values=values, tags=tags)
    
    def view_receipt(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
        
        receipt_number = self.payment_tree.item(selected[0])['values'][3]
        receipt = self.app.db.get_receipt_by_number(receipt_number)
        
        if receipt and os.path.exists(receipt['filepath']):
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', receipt['filepath']])
            elif platform.system() == 'Windows':
                os.startfile(receipt['filepath'])
            else:  # Linux
                subprocess.run(['xdg-open', receipt['filepath']])
    
    def show_outstanding_payments(self):
        """Show outstanding payments dialog"""
        from pages.outstanding_payments import OutstandingPaymentsDialog
        OutstandingPaymentsDialog(self, self.app)