import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import platform
import subprocess

class StudentProfileDialog(tk.Toplevel):
    def __init__(self, parent, app, reg_number):
        super().__init__(parent)
        self.app = app
        self.reg_number = reg_number
        self.title("Student Profile")
        
        # Set dialog size
        dialog_width = 1200
        dialog_height = 700
        
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
        
        # Get student data
        self.student_data = self.app.db.get_student(reg_number)
        
        # Store main frame reference
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_header(self.main_frame)
        self.create_content(self.main_frame)
        
    def create_header(self, parent):
        # Header frame
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configure grid columns
        header_frame.columnconfigure(0, weight=1)  # Title column will expand
        header_frame.columnconfigure(1, weight=0)  # Buttons column will not expand
        
        # Title with student name
        title = ttk.Label(header_frame,
                         text=f"Student Profile - {self.student_data['name']}",
                         style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", pady=10, padx=5)
        
        # Buttons frame
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=1, sticky="e", pady=10, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(button_frame,
                              text="↻ Refresh",
                              style="Modern.TButton",
                              command=self.refresh_profile)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Edit Details button
        edit_btn = ttk.Button(button_frame,
                             text="Edit Details",
                             style="Modern.TButton",
                             command=self.edit_profile)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Export PDF button
        export_btn = ttk.Button(button_frame,
                             text="Export PDF",
                             style="Modern.TButton",
                             command=self.export_pdf)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Payment Record button
        payment_btn = ttk.Button(button_frame,
                               text="Payment Record",
                               style="Modern.TButton",
                               command=self.show_payment_record)
        payment_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = ttk.Button(button_frame,
                              text="🗑️ Delete",
                              style="Danger.TButton",
                              command=self.delete_student)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button - smaller size
        close_btn = ttk.Button(button_frame,
                             text="×",  # Use × symbol
                             width=3,   # Make button smaller
                             style="Modern.TButton",
                             command=self.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def create_content(self, parent):
        # Create main content frame with scrolling
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrolling components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create content in scrollable frame
        content_frame = ttk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Configure grid
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # Left column: Student Info and Payment Info
        left_column = ttk.Frame(content_frame)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.create_student_info(left_column)
        self.create_payment_section(left_column)
        
        # Right column: Payment History
        right_column = ttk.Frame(content_frame)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.create_payment_history(right_column)
        
        # Configure canvas scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_student_info(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Student Information", padding=20)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Get system background color
        system_bg = self.winfo_toplevel().cget('bg')  # Get system background color
        
        # Student details with default values and formatting
        details = [
            {
                "label": "Registration Number:",
                "value": self.student_data.get('reg_number', ''),
                "style": "code"  # Special style for registration number
            },
            {
                "label": "Name:",
                "value": self.student_data.get('name', ''),
                "style": "name"  # Special style for name
            },
            {
                "label": "Age:",
                "value": str(self.student_data.get('age', '')),
                "style": "normal"
            },
            {
                "label": "Gender:",
                "value": self.student_data.get('gender', ''),
                "style": "normal"
            },
            {
                "label": "Programme:",
                "value": self.student_data.get('programme', ''),
                "style": "highlight"  # Special style for programme
            },
            {
                "label": "Programme Fee:",
                "value": f"₦{self.student_data.get('programme_fee', 0):,.2f}",
                "style": "money"  # Special style for money
            },
            {
                "label": "Duration:",
                "value": self.student_data.get('duration', ''),
                "style": "normal"
            },
            {
                "label": "Schedule:",
                "value": self.student_data.get('schedule', ''),
                "style": "highlight"  # Special style for schedule
            },
            {
                "label": "Start Date:",
                "value": self.format_date(self.student_data.get('start_date', '')),
                "style": "date"  # Special style for date
            },
            {
                "label": "Registration Date:",
                "value": self.format_datetime(self.student_data.get('registration_date', '')),
                "style": "date"
            },
            {
                "label": "Status:",
                "value": self.get_student_status(),
                "style": "status"  # Special style for status
            }
        ]
        
        # Style configurations
        styles = {
            "normal": {
                "font": ("Helvetica", 10),
                "foreground": "#212121",
                "background": system_bg
            },
            "code": {
                "font": ("Consolas", 10, "bold"),
                "foreground": "#1976D2",
                "background": system_bg
            },
            "name": {
                "font": ("Helvetica", 11, "bold"),
                "foreground": "#212121",
                "background": system_bg
            },
            "highlight": {
                "font": ("Helvetica", 10, "bold"),
                "foreground": "#0D47A1",
                "background": system_bg
            },
            "money": {
                "font": ("Helvetica", 10, "bold"),
                "foreground": "#2E7D32",
                "background": system_bg
            },
            "date": {
                "font": ("Helvetica", 10),
                "foreground": "#616161",
                "background": system_bg
            },
            "status": {
                "font": ("Helvetica", 10, "bold"),
                "foreground": self.get_status_color(),
                "background": system_bg
            }
        }
        
        # Create labels with enhanced styling and spacing
        for i, detail in enumerate(details):
            # Section separator
            if i > 0 and i % 5 == 0:
                ttk.Separator(info_frame, orient="horizontal").grid(
                    row=i+i//5-1, column=0, columnspan=2, sticky="ew", pady=10)
            
            # Label with bold style
            ttk.Label(info_frame, 
                     text=detail["label"],
                     style="Bold.TLabel").grid(
                         row=i+i//5, 
                         column=0, 
                         sticky="e", 
                         padx=(5, 10),
                         pady=5)
            
            # Value with custom style
            tk.Label(info_frame, 
                    text=detail["value"],
                    **styles[detail["style"]]).grid(
                        row=i+i//5,
                        column=1,
                        sticky="w",
                        padx=5,
                        pady=5)
        
        # Remove the action buttons frame and its contents
        # (Delete or comment out the action_frame creation and button code)

    def format_date(self, date_str):
        """Format date string to readable format"""
        if not date_str:
            return ""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B, %Y')
        except:
            return date_str

    def format_datetime(self, datetime_str):
        """Format datetime string to readable format"""
        if not datetime_str:
            return ""
        try:
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').strftime('%d %B, %Y %I:%M %p')
        except:
            return datetime_str

    def get_student_status(self):
        """Calculate student status based on payments and schedule"""
        total_paid = self.app.db.get_total_payments(self.student_data.get('reg_number', ''))
        programme_fee = self.student_data.get('programme_fee', 0)
        
        if total_paid >= programme_fee:
            return "Active (Fully Paid)"
        elif total_paid > 0:
            percentage = (total_paid / programme_fee) * 100
            return f"Active (Partial Payment - {percentage:.1f}%)"
        return "Pending Payment"

    def get_status_color(self):
        """Get color based on student status"""
        total_paid = self.app.db.get_total_payments(self.student_data.get('reg_number', ''))
        programme_fee = self.student_data.get('programme_fee', 0)
        
        if total_paid >= programme_fee:
            return "#2E7D32"  # Green
        elif total_paid > 0:
            return "#F57C00"  # Orange
        return "#C62828"  # Red

    def edit_profile(self):
        """Open edit profile dialog"""
        from pages.edit_student import EditStudentDialog
        EditStudentDialog(self, self.app, self.student_data)

    def refresh_profile(self):
        """Refresh all profile data"""
        # Get updated student data
        self.student_data = self.app.db.get_student(self.reg_number)
        
        # Update payment history
        if hasattr(self, 'payment_tree'):
            self.load_payment_history()
        
        # Update payment section if exists
        if hasattr(self, 'create_payment_section'):
            # Clear existing payment frame
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.LabelFrame) and widget.winfo_children()[0].cget('text').startswith('Payment'):
                    widget.destroy()
            # Recreate payment section
            self.create_payment_section(self.main_frame)
        
        # Show success message
        messagebox.showinfo("Success", "Profile data refreshed successfully!")

    def export_pdf(self):
        """Export student profile as PDF"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"student_profile_{self.reg_number}_{timestamp}.pdf"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            # Ensure exports directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Student Profile", title_style))
            story.append(Spacer(1, 20))
            
            # Student Details
            data = [
                ["Registration Number:", self.student_data.get('reg_number', '')],
                ["Name:", self.student_data.get('name', '')],
                ["Age:", str(self.student_data.get('age', ''))],
                ["Gender:", self.student_data.get('gender', '')],
                ["Programme:", self.student_data.get('programme', '')],
                ["Schedule:", self.student_data.get('schedule', '')],
                ["Duration:", self.student_data.get('duration', '')],
                ["Start Date:", self.format_date(self.student_data.get('start_date', ''))],
                ["Programme Fee:", f"₦{self.student_data.get('programme_fee', 0):,.2f}"],
                ["Status:", self.get_student_status()]
            ]
            
            # Create table
            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
                ('PADDING', (0, 0), (-1, -1), 12)
            ]))
            story.append(table)
            
            # Add payment history
            story.append(Spacer(1, 30))
            story.append(Paragraph("Payment History", title_style))
            story.append(Spacer(1, 20))
            
            payments = self.app.db.get_payment_history(self.reg_number)
            if payments:
                payment_data = [["Date", "Amount", "Receipt", "Balance"]]
                for payment in payments:
                    payment_data.append([
                        datetime.strptime(payment['payment_date'], 
                                        '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'),
                        f"₦{payment['amount']:,.2f}",
                        payment['receipt_number'],
                        f"₦{payment['balance']:,.2f}"
                    ])
                
                payment_table = Table(payment_data, colWidths=[100, 100, 150, 100])
                payment_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('PADDING', (0, 0), (-1, -1), 12)
                ]))
                story.append(payment_table)
            
            # Build PDF
            doc.build(story)
            
            # Open the generated PDF
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            
            messagebox.showinfo("Success", 
                              f"Profile exported successfully to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export profile: {str(e)}")

    def create_payment_section(self, parent):
        # Payment Section
        payment_frame = ttk.LabelFrame(parent, text="Payment Information", padding=20)
        payment_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))
        
        # Payment summary with default values
        total_paid = self.app.db.get_total_payments(self.student_data.get('reg_number', ''))
        programme_fee = self.student_data.get('programme_fee', 0)
        balance = programme_fee - total_paid
        
        details = [
            ("Programme Fee:", f"₦{programme_fee:,.2f}"),
            ("Total Paid:", f"₦{total_paid:,.2f}"),
            ("Balance:", f"₦{balance:,.2f}")
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(payment_frame, text=label, style="Bold.TLabel").grid(
                row=i, column=0, sticky="e", padx=5, pady=5)
            ttk.Label(payment_frame, text=value).grid(
                row=i, column=1, sticky="w", padx=5, pady=5)
        
        # Add Payment Record button
        ttk.Button(payment_frame,
                  text="Payment Record",
                  style="Modern.TButton",
                  command=self.show_payment_record).grid(
            row=len(details), column=0, columnspan=2, pady=20)

    def show_payment_record(self):
        from pages.payment_record import PaymentRecordDialog
        PaymentRecordDialog(self, self.app, self.student_data) 

    def create_payment_history(self, parent):
        # Payment History Section
        history_frame = ttk.LabelFrame(parent, text="Payment History", padding=20)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
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
        columns = ("date", "amount", "receipt", "balance")
        self.payment_tree = ttk.Treeview(history_frame,
                                       columns=columns,
                                       show="headings",
                                       style="PaymentHistory.Treeview")
        
        # Configure columns
        column_configs = {
            "date": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Payment Date"
            },
            "amount": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Amount"
            },
            "receipt": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Receipt Number"
            },
            "balance": {
                "width": 150, "minwidth": 150, "stretch": True,
                "anchor": "center", "text": "Balance"
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
        scrollbar = ttk.Scrollbar(history_frame,
                                orient=tk.VERTICAL,
                                command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view receipt
        self.payment_tree.bind("<Double-1>", self.view_receipt)
        
        # Load payment history
        self.load_payment_history()

    def load_payment_history(self):
        # Clear existing items
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        # Get payment history
        payments = self.app.db.get_payment_history(self.reg_number)
        
        # Add to treeview with alternating colors
        for i, payment in enumerate(payments):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values
            values = (
                datetime.strptime(payment['payment_date'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M'),
                f"₦{payment['amount']:,.2f}",
                payment['receipt_number'],
                f"₦{payment['balance']:,.2f}"
            )
            
            self.payment_tree.insert("", "end", values=values, tags=tags)

    def view_receipt(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
        
        try:
            receipt_number = self.payment_tree.item(selected[0])['values'][2]
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
    def export_profile(self):
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"student_profile_{self.reg_number}_{timestamp}.pdf"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            # Ensure exports directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # TODO: Implement PDF generation
            messagebox.showinfo("Info", 
                              "Profile export will be implemented\n"
                              f"File will be saved to: {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export profile: {str(e)}") 

    def delete_student(self):
        """
        Delete the current student record after confirmation
        """
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the student record for {self.student_data['name']}?\n\n"
            "This will permanently remove the student and all associated payment records.\n"
            "This action CANNOT be undone."
        )
        
        if confirm:
            # Attempt to delete student
            success = self.app.db.delete_student(self.reg_number)
            
            if success:
                messagebox.showinfo(
                    "Student Deleted", 
                    f"Student record for {self.student_data['name']} has been successfully deleted."
                )
                # Close the current dialog
                self.destroy()
                
                # Refresh parent window if possible
                try:
                    if hasattr(self.master, 'load_students'):
                        self.master.load_students()
                except Exception as e:
                    print(f"Could not refresh parent window: {e}")
            else:
                messagebox.showerror(
                    "Deletion Failed", 
                    f"Could not delete student record for {self.student_data['name']}. Please try again."
                )
