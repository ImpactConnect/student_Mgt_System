import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import subprocess
import platform

class PaymentRecordDialog(tk.Toplevel):
    def __init__(self, parent, app, student_data):
        super().__init__(parent)
        self.app = app
        self.student_data = student_data
        self.title("Payment Record")
        
        # Set dialog size
        dialog_width = 800
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
        self.create_student_info(main_frame)
        self.create_payment_form(main_frame)
        self.create_payment_history(main_frame)
        
    def create_student_info(self, parent):
        # Student Information Section
        info_frame = ttk.LabelFrame(parent, text="Student Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Student details grid
        details = [
            ("Registration Number:", self.student_data['reg_number']),
            ("Name:", self.student_data['name']),
            ("Programme:", self.student_data['programme']),
            ("Programme Fee:", f"₦{self.student_data['programme_fee']:,.2f}")
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, 
                                                 sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=value).grid(row=i, column=1, 
                                                 sticky="w", padx=5, pady=2)
        
        # Payment summary
        total_paid = self.app.db.get_total_payments(self.student_data['reg_number'])
        balance = self.student_data['programme_fee'] - total_paid
        
        ttk.Label(info_frame, text="Total Paid:").grid(row=len(details), column=0, 
                                                     sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=f"₦{total_paid:,.2f}").grid(row=len(details), 
                                                             column=1, sticky="w", 
                                                             padx=5, pady=2)
        
        ttk.Label(info_frame, text="Balance:").grid(row=len(details)+1, column=0, 
                                                  sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=f"₦{balance:,.2f}").grid(row=len(details)+1, 
                                                          column=1, sticky="w", 
                                                          padx=5, pady=2)
    
    def create_payment_form(self, parent):
        # Payment Form Section
        form_frame = ttk.LabelFrame(parent, text="New Payment", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configure grid layout - 3 equal columns
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)
        
        # Amount Entry - Column 1
        ttk.Label(form_frame, text="Amount:").grid(
            row=0, column=0, sticky="w", padx=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(form_frame, 
                               textvariable=self.amount_var, 
                               width=15)
        amount_entry.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 10))
        
        # Payment Note - Column 2
        ttk.Label(form_frame, text="Payment Note:").grid(
            row=0, column=1, sticky="w", padx=5)
        self.note_text = tk.Text(form_frame, 
                               height=3,  # Reduced height
                               width=20)  # Reduced width
        self.note_text.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 10))
        
        # Add Payment Button - Column 3
        ttk.Button(form_frame, 
                  text="Add Payment",
                  command=self.add_payment,
                  style="Modern.TButton").grid(
                      row=1, column=2, sticky="w", padx=5, pady=(0, 10))
    
    def create_payment_history(self, parent):
        # Payment History Section
        history_frame = ttk.LabelFrame(parent, text="Payment History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("date", "amount", "receipt", "balance")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                       show="headings")
        
        # Configure columns
        self.history_tree.heading("date", text="Payment Date")
        self.history_tree.heading("amount", text="Amount")
        self.history_tree.heading("receipt", text="Receipt Number")
        self.history_tree.heading("balance", text="Balance")
        
        self.history_tree.column("date", width=150)
        self.history_tree.column("amount", width=150)
        self.history_tree.column("receipt", width=150)
        self.history_tree.column("balance", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load payment history
        self.load_payment_history()
        
        # Add right-click menu for receipts
        self.create_context_menu()
    
    def load_payment_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get payment history
        payments = self.app.db.get_payment_history(self.student_data['reg_number'])
        
        # Add to treeview
        for payment in payments:
            self.history_tree.insert("", 0, values=(
                datetime.strptime(payment['payment_date'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M'),
                f"₦{payment['amount']:,.2f}",
                payment['receipt_number'],
                f"₦{payment['balance']:,.2f}"
            ))
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Preview Receipt", 
                                    command=self.preview_receipt)
        self.context_menu.add_command(label="Print Receipt", 
                                    command=self.print_receipt)
        
        self.history_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        try:
            item = self.history_tree.identify_row(event.y)
            if item:
                self.history_tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def add_payment(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
                
            # Get payment note
            payment_note = self.note_text.get('1.0', 'end-1c').strip()
            
            # Save payment
            success, receipt_path, error = self.app.db.save_payment(
                self.student_data['reg_number'], amount, payment_note)
            
            if success:
                messagebox.showinfo("Success", "Payment recorded successfully!")
                self.amount_var.set("")  # Clear amount entry
                self.load_payment_history()  # Refresh history
                
                # Show receipt options
                if receipt_path:
                    self.show_receipt_buttons(receipt_path)
            else:
                messagebox.showerror("Error", f"Failed to record payment: {error}")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid amount")
    
    def preview_receipt(self):
        selected = self.history_tree.selection()
        if not selected:
            return
            
        receipt_number = self.history_tree.item(selected[0])['values'][2]
        receipts = self.app.db.get_student_receipts(self.student_data['reg_number'])
        
        for receipt in receipts:
            if receipt['receipt_number'] == receipt_number:
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', receipt['filepath']])
                    elif platform.system() == 'Windows':
                        os.startfile(receipt['filepath'])
                    else:  # Linux
                        subprocess.run(['xdg-open', receipt['filepath']])
                except Exception as e:
                    messagebox.showerror("Error", 
                                       f"Failed to open receipt: {str(e)}")
                break
    
    def print_receipt(self):
        selected = self.history_tree.selection()
        if not selected:
            return
            
        receipt_number = self.history_tree.item(selected[0])['values'][2]
        receipts = self.app.db.get_student_receipts(self.student_data['reg_number'])
        
        for receipt in receipts:
            if receipt['receipt_number'] == receipt_number:
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['lpr', receipt['filepath']])
                    elif platform.system() == 'Windows':
                        subprocess.run(['print', receipt['filepath']], shell=True)
                    else:  # Linux
                        subprocess.run(['lpr', receipt['filepath']])
                except Exception as e:
                    messagebox.showerror("Error", 
                                       f"Failed to print receipt: {str(e)}")
                break 
    
    def show_receipt_buttons(self, receipt_path):
        """Show buttons to view or print receipt"""
        # Create a new dialog for receipt options
        receipt_dialog = tk.Toplevel(self)
        receipt_dialog.title("Receipt Options")
        
        # Set dialog size and position
        dialog_width = 300
        dialog_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        receipt_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        receipt_dialog.transient(self)
        receipt_dialog.grab_set()
        
        # Create content frame with padding
        content_frame = ttk.Frame(receipt_dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        ttk.Label(content_frame, 
                 text="Receipt has been generated successfully!",
                 wraplength=250).pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack()
        
        # View Receipt button
        ttk.Button(button_frame,
                  text="View Receipt",
                  command=lambda: self.view_receipt_file(receipt_path)).pack(
                      side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(button_frame,
                  text="Close",
                  command=receipt_dialog.destroy).pack(
                      side=tk.LEFT, padx=5)

    def view_receipt_file(self, receipt_path):
        """Open receipt file with default PDF viewer"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', receipt_path])
            elif platform.system() == 'Windows':
                os.startfile(receipt_path)
            else:  # Linux
                subprocess.run(['xdg-open', receipt_path])
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open receipt: {str(e)}"
            ) 