import tkinter as tk
from tkinter import ttk, StringVar
from tkinter import messagebox
from pages.registration import RegistrationDialog
from datetime import datetime
import sqlite3

class HomePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main layout with sections
        self.create_header()
        self.create_quick_stats()
        self.create_search_section()
        self.create_navigation_buttons()
        self.create_recent_activities()
        
        # Auto refresh timer
        self.after(300000, self.refresh_stats)  # Refresh every 5 minutes
    
    def create_header(self):
        # Header frame with gradient effect
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Date and time
        date_frame = ttk.Frame(header_frame)
        date_frame.pack(side=tk.RIGHT, padx=20)
        
        current_time = datetime.now().strftime("%d %B, %Y")
        ttk.Label(date_frame,
                 text=current_time,
                 font=("Helvetica", 10)).pack()
        
        # Title with modern styling
        title = ttk.Label(header_frame, 
                         text="IMPACTTECH CODING ACADEMY", 
                         style="Title.TLabel")
        title.pack(pady=10)
        
        subtitle = ttk.Label(header_frame, 
                           text="Student Management System", 
                           style="Subtitle.TLabel")
        subtitle.pack()
    
    def create_quick_stats(self):
        # Quick statistics panel
        stats_frame = ttk.LabelFrame(self, text="Quick Statistics", padding=15)
        stats_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # Create grid for stats
        stats_frame.columnconfigure((0,1,2,3), weight=1)
        
        # Get statistics
        stats = self.app.db.get_student_statistics()
        
        # Statistics with icons and colors
        stats_data = [
            ("👥 Total Students", stats['total_students'], "#1976D2"),
            ("✅ Active", stats['active_students'], "#2E7D32"),
            ("🎓 Graduated", stats['graduated_students'], "#1565C0"),
            ("❌ Dropped Out", stats['dropouts'], "#C62828")
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            stat_container = ttk.Frame(stats_frame)
            stat_container.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            ttk.Label(stat_container,
                     text=label,
                     font=("Helvetica", 10)).pack()
            
            tk.Label(stat_container,
                    text=str(value),
                    font=("Helvetica", 16, "bold"),
                    fg=color).pack()
    
    def create_search_section(self):
        # Modern search frame
        search_frame = ttk.LabelFrame(self, text="Quick Search", padding=15)
        search_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # Search entry with placeholder
        self.search_var = StringVar()
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var,
                               width=40,
                               font=("Helvetica", 12))
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add placeholder behavior
        self.add_placeholder(search_entry, "Enter student name or registration number")
        
        # Search button with icon
        search_button = ttk.Button(search_frame,
                                 text="🔍 Search",
                                 style="Accent.TButton",
                                 command=self.search_student)
        search_button.pack(side=tk.LEFT)
    
    def create_navigation_buttons(self):
        # Navigation frame with modern grid layout
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Configure grid
        for i in range(3):
            nav_frame.columnconfigure(i, weight=1)
        
        # Navigation buttons with icons and descriptions
        nav_buttons = [
            ("📝 New Registration", "Register new student", "register_student", 0, 0),
            ("👥 Student Records", "View all students", "view_students", 0, 1),
            ("📚 Programmes", "Manage programmes", "show_programmes", 0, 2),
            ("💰 Payment History", "View payments", "show_payment_history", 1, 0),
            ("📊 Reports", "Generate reports", "show_reports", 1, 1),
            ("⚙️ Settings", "System settings", "show_settings", 1, 2)
        ]
        
        for text, desc, command, row, col in nav_buttons:
            self.create_nav_button(nav_frame, text, desc, command, row, col)
    
    def create_nav_button(self, parent, text, desc, command, row, col):
        # Button container frame
        container = ttk.Frame(parent)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Main button
        btn = ttk.Button(container,
                        text=text,
                        style="Nav.TButton",
                        command=lambda: self.navigate(command))
        btn.pack(fill=tk.X, ipady=15)
        
        # Description label
        ttk.Label(container,
                 text=desc,
                 font=("Helvetica", 9),
                 foreground="gray").pack(pady=(5, 0))
    
    def create_recent_activities(self):
        # Recent activities section
        activities_frame = ttk.LabelFrame(self, text="Recent Activities", padding=15)
        activities_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # Get recent activities (last 5)
        activities = self.get_recent_activities()
        
        for activity in activities:
            activity_label = ttk.Label(activities_frame,
                                     text=activity,
                                     font=("Helvetica", 9))
            activity_label.pack(anchor="w", pady=2)
    
    def add_placeholder(self, entry, placeholder):
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(foreground="black")
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground="gray")
        
        entry.insert(0, placeholder)
        entry.configure(foreground="gray")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    
    def navigate(self, command):
        if command == "register_student":
            RegistrationDialog(self, self.app)
        elif command == "view_students":
            self.app.show_student_list_page()
        elif command == "show_payment_history":
            self.app.show_payment_history()
        elif command == "show_programmes":
            self.app.show_programmes_page()
        elif command == "show_settings":
            self.app.show_settings_page()
        elif command == "show_reports":
            self.app.show_reports_page()
    
    def search_student(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Search Error", 
                                 "Please enter a name or registration number")
            return
        
        # Connect to database
        conn = sqlite3.connect(self.app.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Search by registration number or name (case-insensitive)
            cursor.execute('''
                SELECT reg_number 
                FROM students 
                WHERE LOWER(reg_number) = LOWER(?) OR 
                      LOWER(name) LIKE LOWER(?)
            ''', (search_term, f'%{search_term}%'))
            
            result = cursor.fetchone()
            
            if result:
                # Open student profile
                reg_number = result[0]
                self.app.show_student_profile(reg_number)
            else:
                # No student found
                messagebox.showinfo("Search Result", 
                                  f"No student found matching '{search_term}'")
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", 
                                f"An error occurred while searching: {str(e)}")
        
        finally:
            conn.close()
    
    def export_records(self):
        # TODO: Implement export functionality
        messagebox.showinfo("Export", 
                          "Export functionality will be implemented here")
    
    def show_reports(self):
        # TODO: Implement reports functionality
        messagebox.showinfo("Reports", 
                          "Reports functionality will be implemented here")
    
    def get_recent_activities(self):
        """Get list of recent activities from database"""
        conn = sqlite3.connect(self.app.db.db_path)
        cursor = conn.cursor()
        
        activities = []
        try:
            # Get recent payments
            cursor.execute('''
                SELECT 
                    s.name,
                    p.amount,
                    p.payment_date,
                    'payment' as type
                FROM payments p
                JOIN students s ON p.reg_number = s.reg_number
                ORDER BY p.payment_date DESC
                LIMIT 3
            ''')
            
            for row in cursor.fetchall():
                name, amount, date, _ = row
                formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                activities.append(f"💰 Payment of ₦{amount:,.2f} by {name} on {formatted_date}")
            
            # Get recent registrations
            cursor.execute('''
                SELECT 
                    name,
                    programme,
                    registration_date
                FROM students
                ORDER BY registration_date DESC
                LIMIT 3
            ''')
            
            for row in cursor.fetchall():
                name, programme, date = row
                formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                activities.append(f"📝 {name} registered for {programme} on {formatted_date}")
            
            # Sort all activities by date (most recent first)
            return sorted(activities, reverse=True)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return ["No recent activities to display"]
            
        finally:
            conn.close()
    
    def refresh_stats(self):
        """Refresh statistics periodically"""
        try:
            # Update statistics
            stats = self.app.db.get_student_statistics()
            
            # Update date/time
            current_time = datetime.now().strftime("%d %B, %Y")
            
            # Optional: Update UI elements if needed
            # For example, update labels or counters
            
            # Schedule next refresh
            self.after(300000, self.refresh_stats)  # Every 5 minutes
            
        except Exception as e:
            print(f"Error refreshing stats: {e}")
            # Optionally, add a fallback or error handling
            # Schedule next attempt even if this one fails
            self.after(300000, self.refresh_stats)
    