import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import PROGRAMMES
import platform
import os
import subprocess
from datetime import datetime

class OutstandingPaymentsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Outstanding Payments")
        
        # Set dialog size
        dialog_width = 800
        dialog_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_content(main_frame)
        
    def create_content(self, parent):
        # Header frame with title
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        ttk.Label(header_frame,
                 text="Students with Outstanding Payments",
                 style="Title.TLabel").pack(pady=10)
        
        # Controls frame (row 2)
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side - Filter controls
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.pack(side=tk.LEFT)
        
        ttk.Label(filter_frame, text="Filter by Programme:").pack(side=tk.LEFT, padx=(0, 5))
        self.programme_var = tk.StringVar(value="All")
        programme_combo = ttk.Combobox(filter_frame,
                                     textvariable=self.programme_var,
                                     values=["All"] + PROGRAMMES,
                                     state="readonly",
                                     width=30)
        programme_combo.pack(side=tk.LEFT, padx=(0, 10))
        programme_combo.bind("<<ComboboxSelected>>", self.apply_filter)
        
        # Right side - Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Clear filter button
        ttk.Button(button_frame,
                  text="Clear Filter",
                  command=self.clear_filter).pack(side=tk.LEFT, padx=5)
        
        # Export button
        ttk.Button(button_frame,
                  text="Export to Excel",
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Create Treeview
        columns = ("name", "programme", "total_fee", "paid", "balance")
        self.tree = ttk.Treeview(parent,
                                columns=columns,
                                show="headings",
                                style="PaymentHistory.Treeview")
        
        # Configure columns
        column_configs = {
            "name": {
                "width": 200, "minwidth": 200, "stretch": True,
                "anchor": "w", "text": "Student Name"
            },
            "programme": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "w", "text": "Programme"
            },
            "total_fee": {
                "width": 120, "minwidth": 120, "stretch": True,
                "anchor": "e", "text": "Programme Fee"
            },
            "paid": {
                "width": 120, "minwidth": 120, "stretch": True,
                "anchor": "e", "text": "Amount Paid"
            },
            "balance": {
                "width": 120, "minwidth": 120, "stretch": True,
                "anchor": "e", "text": "Balance"
            }
        }
        
        # Apply configurations
        for col, config in column_configs.items():
            self.tree.heading(
                col,
                text=config["text"],
                anchor=config["anchor"]
            )
            self.tree.column(
                col,
                width=config["width"],
                minwidth=config["minwidth"],
                stretch=config["stretch"],
                anchor=config["anchor"]
            )
        
        # Add alternating row colors
        self.tree.tag_configure('oddrow', background='#F5F5F5')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent,
                                orient=tk.VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load data
        self.load_outstanding_payments()
        
    def apply_filter(self, event=None):
        self.load_outstanding_payments()
        
    def load_outstanding_payments(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get outstanding payments from database
        students = self.app.db.get_outstanding_payments()
        
        # Apply programme filter
        programme_filter = self.programme_var.get()
        if programme_filter != "All":
            students = [s for s in students if s['programme'] == programme_filter]
        
        # Add to treeview with alternating colors
        for i, student in enumerate(students):
            tags = ('oddrow',) if i % 2 else ()
            
            values = (
                student['name'],
                student['programme'],
                f"₦{student['programme_fee']:,.2f}",
                f"₦{student['amount_paid']:,.2f}",
                f"₦{student['balance']:,.2f}"
            )
            
            self.tree.insert("", "end", values=values, tags=tags)
    
    def export_data(self):
        """Export outstanding payments to Excel"""
        try:
            # Get filtered data
            data = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                data.append({
                    'Student Name': values[0],
                    'Programme': values[1],
                    'Programme Fee': values[2],
                    'Amount Paid': values[3],
                    'Balance': values[4]
                })
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            programme = self.programme_var.get()
            filename = f"outstanding_payments_{programme}_{timestamp}.xlsx"
            
            # Export to Excel using pandas
            import pandas as pd
            df = pd.DataFrame(data)
            
            # Create exports directory if it doesn't exist
            export_dir = os.path.join(self.app.app_path, "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(export_dir, filename)
            df.to_excel(filepath, index=False)
            
            messagebox.showinfo("Success", 
                              f"Outstanding payments exported successfully to:\n{filepath}")
            
            # Open the exported file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
                
        except ImportError:
            messagebox.showerror("Error", "Please install pandas: pip install pandas")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def clear_filter(self):
        """Clear the programme filter"""
        self.programme_var.set("All")
        self.load_outstanding_payments()