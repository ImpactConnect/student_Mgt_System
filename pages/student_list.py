import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import PROGRAMMES, SCHEDULES
from datetime import datetime

class StudentListPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main layout
        self.create_header()
        self.create_stats_section()
        self.create_filters()
        self.create_student_table()
        self.load_students()
        
    def create_header(self):
        # Header with back button and title
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create top section with back button and export
        top_section = ttk.Frame(header_frame)
        top_section.pack(fill=tk.X)
        
        back_btn = ttk.Button(top_section,
                            text="← Back",
                            command=self.app.show_home_page)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # Export and Reports buttons
        export_btn = ttk.Button(top_section,
                              text="Export to Excel",
                              style="Modern.TButton",
                              command=self.export_to_excel)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        reports_btn = ttk.Button(top_section,
                               text="Schedule Reports",
                               style="Modern.TButton",
                               command=self.show_schedule_reports)
        reports_btn.pack(side=tk.RIGHT, padx=5)
        
        # Title
        title = ttk.Label(header_frame,
                         text="Student Records",
                         style="Title.TLabel")
        title.pack(pady=10)
    
    def create_stats_section(self):
        # Stats frame
        stats_frame = ttk.LabelFrame(self, text="Student Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Get system background color
        system_bg = self.winfo_toplevel().cget('bg')
        
        # Get statistics from database
        stats = self.app.db.get_student_statistics()
        
        # Create grid of stats with styling
        stats_data = [
            {
                "title": "Total Students",
                "value": str(stats['total_students']),
                "title_color": "#1976D2",  # Blue
                "value_color": "#1565C0"   # Darker blue
            },
            {
                "title": "Active Students",
                "value": str(stats['active_students']),
                "title_color": "#2E7D32",  # Green
                "value_color": "#1B5E20"   # Darker green
            },
            {
                "title": "Graduated Students",
                "value": str(stats['graduated_students']),
                "title_color": "#7B1FA2",  # Purple
                "value_color": "#6A1B9A"   # Darker purple
            },
            {
                "title": "Drop Outs",
                "value": str(stats['dropouts']),
                "title_color": "#C62828",  # Red
                "value_color": "#B71C1C"   # Darker red
            },
            {
                "title": "Scholarships",
                "value": str(stats['scholarships']),
                "title_color": "#F57C00",  # Orange
                "value_color": "#EF6C00"   # Darker orange
            }
        ]
        
        # Create stats in a single row
        for col_idx, stat in enumerate(stats_data):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=0, column=col_idx, padx=10, pady=5, sticky="nsew")
            
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
        
        # Configure grid columns for equal spacing
        for i in range(len(stats_data)):
            stats_frame.columnconfigure(i, weight=1)
    
    def create_filters(self):
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Left side - Filter controls
        controls_frame = ttk.Frame(filter_frame)
        controls_frame.pack(side=tk.LEFT)
        
        # Programme filter
        ttk.Label(controls_frame, text="Programme:").pack(side=tk.LEFT, padx=(0, 5))
        self.programme_var = tk.StringVar()
        programme_combo = ttk.Combobox(controls_frame,
                                     textvariable=self.programme_var,
                                     values=["All"] + PROGRAMMES,
                                     state="readonly",
                                     width=30)
        programme_combo.set("All")
        programme_combo.pack(side=tk.LEFT, padx=5)
        
        # Schedule filter
        ttk.Label(controls_frame, text="Schedule:").pack(side=tk.LEFT, padx=(20, 5))
        self.schedule_var = tk.StringVar()
        schedule_combo = ttk.Combobox(controls_frame,
                                    textvariable=self.schedule_var,
                                    values=["All"] + SCHEDULES,
                                    state="readonly",
                                    width=20)
        schedule_combo.set("All")
        schedule_combo.pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(controls_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame,
                               textvariable=self.search_var,
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Right side - Action buttons
        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Apply Filter button
        ttk.Button(button_frame,
                   text="Apply Filter",
                   command=self.filter_students).pack(side=tk.LEFT, padx=5)
        
        # Clear Filter button
        ttk.Button(button_frame,
                   text="Clear Filter",
                   command=self.clear_filters).pack(side=tk.LEFT, padx=5)
    
    def clear_filters(self):
        """Clear all filters and show all records"""
        # Reset filter variables
        self.programme_var.set("All")
        self.schedule_var.set("All")
        self.search_var.set("")
        
        # Clear the table
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Reload all students
        students = self.app.db.get_all_students()
        
        # Add all students back to treeview with alternating colors
        for i, student in enumerate(students):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values with proper spacing
            values = (
                student['reg_number'].center(15),
                student['name'].ljust(40),
                student['programme'].center(30),
                student['schedule'].center(15),
                datetime.strptime(student['start_date'], 
                                '%Y-%m-%d').strftime('%d/%m/%Y').center(15)
            )
            
            self.student_tree.insert("", "end", values=values, tags=tags)
    
    def create_student_table(self):
        # Table frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("StudentTable.Treeview.Heading",
                       background='gray85',
                       font=("Helvetica", 10, "bold"),
                       padding=5)
        style.configure("StudentTable.Treeview",
                       font=("Helvetica", 10),
                       rowheight=30)
        
        # Create Treeview
        columns = ("reg_number", "name", "programme", "schedule", "start_date")
        self.student_tree = ttk.Treeview(table_frame,
                                       columns=columns,
                                       show="headings",
                                       style="StudentTable.Treeview")
        
        # Configure columns with exact widths and centered alignment
        column_configs = {
            "reg_number": {
                "width": 150, "minwidth": 150, "stretch": False,
                "anchor": "center", "text": "Registration Number"
            },
            "name": {
                "width": 250, "minwidth": 200, "stretch": True,
                "anchor": "center", "text": "Student Name"
            },
            "programme": {
                "width": 200, "minwidth": 150, "stretch": False,
                "anchor": "center", "text": "Programme"
            },
            "schedule": {
                "width": 150, "minwidth": 100, "stretch": False,
                "anchor": "center", "text": "Schedule"
            },
            "start_date": {
                "width": 150, "minwidth": 100, "stretch": False,
                "anchor": "center", "text": "Start Date"
            }
        }
        
        # Apply configurations and set up sorting
        for col, config in column_configs.items():
            self.student_tree.heading(
                col,
                text=config["text"],
                anchor="center"
            )
            self.student_tree.column(
                col,
                width=config["width"],
                minwidth=config["minwidth"],
                stretch=config["stretch"],
                anchor=config["anchor"]
            )
        
        # Add alternating row colors
        self.student_tree.tag_configure('oddrow', background='#F5F5F5')
        
        # Add vertical scrollbar only
        y_scrollbar = ttk.Scrollbar(table_frame,
                                   orient=tk.VERTICAL,
                                   command=self.student_tree.yview)
        
        self.student_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # Pack widgets
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view student profile
        self.student_tree.bind("<Double-1>", self.view_student_profile)
    
    def load_students(self):
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Get all students
        students = self.app.db.get_all_students()
        
        # Add to treeview with alternating colors
        for i, student in enumerate(students):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values with center alignment
            values = (
                student['reg_number'].center(15),
                student['name'].center(40),
                student['programme'].center(30),
                student['schedule'].center(15),
                datetime.strptime(student['start_date'], 
                                '%Y-%m-%d').strftime('%d/%m/%Y').center(15)
            )
            
            self.student_tree.insert("", "end", values=values, tags=tags)
    
    def filter_students(self):
        """Filter students based on selected criteria"""
        # Clear the current table
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Get filter values
        selected_programme = self.programme_var.get()
        selected_schedule = self.schedule_var.get()
        search_term = self.search_var.get().lower()
        
        # Fetch all students
        students = self.app.db.get_all_students()
        
        # Apply filters
        filtered_students = []
        for student in students:
            # Programme filter
            if selected_programme != "All" and student['programme'] != selected_programme:
                continue
            
            # Schedule filter
            if selected_schedule != "All" and student['schedule'] != selected_schedule:
                continue
            
            # Search filter (check if search term is in name or reg number)
            if search_term and (search_term not in student['name'].lower() and 
                                search_term not in student['reg_number'].lower()):
                continue
            
            filtered_students.append(student)
        
        # Add filtered students to treeview with alternating colors
        for i, student in enumerate(filtered_students):
            tags = ('oddrow',) if i % 2 else ()
            
            # Format values with proper spacing
            values = (
                student['reg_number'].center(15),
                student['name'].ljust(40),
                student['programme'].center(30),
                student['schedule'].center(15),
                datetime.strptime(student['start_date'], 
                                '%Y-%m-%d').strftime('%d/%m/%Y').center(15)
            )
            
            self.student_tree.insert("", "end", values=values, tags=tags)
        
        # Show number of filtered results
        messagebox.showinfo("Filter Results", 
                           f"Found {len(filtered_students)} students matching the filter criteria.")
    
    def get_payment_status(self, total_paid, total_fee):
        """Calculate payment status based on payments"""
        if total_paid >= total_fee:
            return "Fully Paid"
        elif total_paid > 0:
            percentage = (total_paid / total_fee) * 100
            return f"Partial ({percentage:.1f}%)"
        return "Not Paid"
    
    def view_student_profile(self, event):
        """Open student profile when double-clicked"""
        selection = self.student_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        reg_number = self.student_tree.item(item)['values'][0]
        
        # Import here to avoid circular imports
        from pages.student_profile import StudentProfileDialog
        StudentProfileDialog(self, self.app, reg_number)
    
    def export_to_excel(self):
        """Export student list to Excel"""
        try:
            filepath = self.app.db.export_students_to_excel()
            messagebox.showinfo("Success", 
                              f"Student records exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Failed to export student records: {str(e)}") 
    
    def sort_treeview(self, col):
        """Sort treeview when column header is clicked"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        items = [(self.student_tree.set(item, col), item) 
                 for item in self.student_tree.get_children('')]
        
        # Custom sorting for date column
        if col == "start_date":
            items.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'), 
                      reverse=self.sort_reverse)
        else:
            items.sort(reverse=self.sort_reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.student_tree.move(item, '', index)
            # Reapply alternating row colors
            tags = ('oddrow',) if index % 2 else ()
            self.student_tree.item(item, tags=tags)
    
    def show_schedule_reports(self):
        """Show detailed schedule reports"""
        report_window = tk.Toplevel(self)
        report_window.title("Schedule Reports")
        report_window.geometry("800x600")
        
        # Create notebook for different reports
        notebook = ttk.Notebook(report_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Distribution Report
        self.create_distribution_report(notebook)
        
        # Payment Analysis by Schedule
        self.create_payment_analysis(notebook)
        
        # Schedule Trends
        self.create_schedule_trends(notebook)
    
    def create_distribution_report(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Schedule Distribution")
        
        # Create Treeview for detailed statistics
        columns = ("schedule", "total", "paid", "partial", "unpaid", "revenue")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        tree.heading("schedule", text="Schedule")
        tree.heading("total", text="Total Students")
        tree.heading("paid", text="Fully Paid")
        tree.heading("partial", text="Partial Payment")
        tree.heading("unpaid", text="Unpaid")
        tree.heading("revenue", text="Total Revenue")
        
        # Get statistics from database
        stats = self.app.db.get_schedule_statistics()
        
        # Add data to treeview
        for stat in stats:
            tree.insert("", "end", values=(
                stat['schedule'],
                stat['total_students'],
                stat['fully_paid'],
                stat['partial_paid'],
                stat['unpaid'],
                f"₦{stat['total_revenue']:,.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def create_payment_analysis(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Payment Analysis")
        
        # Create Treeview for payment analysis
        columns = ("schedule", "expected", "received", "outstanding", "collection_rate")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        tree.heading("schedule", text="Schedule")
        tree.heading("expected", text="Expected Revenue")
        tree.heading("received", text="Received Revenue")
        tree.heading("outstanding", text="Outstanding")
        tree.heading("collection_rate", text="Collection Rate")
        
        # Get payment analysis from database
        analysis = self.app.db.get_schedule_payment_analysis()
        
        # Add data to treeview
        for item in analysis:
            tree.insert("", "end", values=(
                item['schedule'],
                f"₦{item['expected_revenue']:,.2f}",
                f"₦{item['received_revenue']:,.2f}",
                f"₦{item['outstanding']:,.2f}",
                f"{item['collection_rate']:.1f}%"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def create_schedule_trends(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Schedule Trends")
        
        # Create Treeview for trends
        columns = ("schedule", "this_month", "last_month", "growth")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        tree.heading("schedule", text="Schedule")
        tree.heading("this_month", text="This Month")
        tree.heading("last_month", text="Last Month")
        tree.heading("growth", text="Growth")
        
        # Get trends from database
        trends = self.app.db.get_schedule_trends()
        
        # Add data to treeview
        for trend in trends:
            tree.insert("", "end", values=(
                trend['schedule'],
                trend['this_month'],
                trend['last_month'],
                f"{trend['growth']:+.1f}%"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True) 