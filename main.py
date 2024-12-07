import tkinter as tk
from tkinter import ttk
from utils.folder_setup import create_app_folders, reset_database
from database.db_setup import Database
from pages.home import HomePage
from pages.registration import RegistrationDialog
from pages.student_list import StudentListPage
from pages.student_profile import StudentProfileDialog
from pages.payment_history import PaymentHistoryPage
from pages.programmes import ProgrammesPage
import os
from tkinter import messagebox
from utils.notifications import NotificationSystem
import sqlite3

class ImpactechApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Impactech Academy")
        self.root.geometry("1200x800")
        
        # Check for matplotlib
        try:
            import matplotlib
        except ImportError:
            messagebox.showinfo(
                "Optional Dependency Missing",
                "For better visualizations, install matplotlib:\n"
                "pip install matplotlib"
            )
        
        # Setup folders and database
        self.app_path = create_app_folders()
        self.db = Database(self.app_path)
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize homepage
        self.current_page = None
        self.show_home_page()
        
        # Initialize Notification System
        self.notification_system = NotificationSystem(self)
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Modern button styles
        style.configure("Modern.TButton",
                       padding=10,
                       font=("Helvetica", 12))
        
        style.configure("Nav.TButton",
                       padding=15,
                       font=("Helvetica", 12, "bold"))
        
        style.configure("Accent.TButton",
                       padding=10,
                       font=("Helvetica", 12),
                       background="#1976D2")
        
        # Label styles
        style.configure("Title.TLabel",
                       font=("Helvetica", 24, "bold"))
        
        style.configure("Subtitle.TLabel",
                       font=("Helvetica", 16))
                       
    def show_home_page(self):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = HomePage(self.main_container, self)
        
    def show_registration_page(self):
        RegistrationDialog(self.root, self)
    
    def show_student_list_page(self):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = StudentListPage(self.main_container, self)
    
    def show_student_profile(self, reg_number):
        """Show student profile, creating a new dialog"""
        from pages.student_profile import StudentProfileDialog
        StudentProfileDialog(self.root, self, reg_number)
    
    def show_payment_history(self):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = PaymentHistoryPage(self.main_container, self)
    
    def show_programmes_page(self):
        """Show programmes page"""
        if self.current_page:
            self.current_page.destroy()
        self.current_page = ProgrammesPage(self.main_container, self)
    
    def show_settings_page(self):
        """Show settings page"""
        if self.current_page:
            self.current_page.destroy()
        from pages.settings import SettingsPage
        self.current_page = SettingsPage(self.main_container, self)
    
    def show_reports_page(self):
        """Show reports page"""
        if self.current_page:
            self.current_page.destroy()
        from pages.reports import ReportsPage
        self.current_page = ReportsPage(self.main_container, self)
    
    def show_notifications_page(self):
        """Show the notifications page"""
        # Clear existing content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Import and create notifications page
        from pages.notifications import NotificationsPage
        NotificationsPage(self.root, self)
    
    def send_payment_reminder_notifications(self):
        """
        Send payment reminder notifications to students with outstanding balances
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Find students with outstanding balances
            cursor.execute('''
                SELECT 
                    s.reg_number,
                    s.name,
                    s.programme_fee,
                    COALESCE(SUM(p.amount), 0) as total_paid
                FROM students s
                LEFT JOIN payments p ON s.reg_number = p.reg_number
                GROUP BY s.reg_number
                HAVING total_paid < s.programme_fee
            ''')
            
            students_with_balance = cursor.fetchall()
            
            # Send notifications
            for reg_number, name, total_fee, paid_amount in students_with_balance:
                self.notification_system.send_payment_reminder(reg_number)
            
            return len(students_with_balance)
        
        except sqlite3.Error as e:
            print(f"Error sending payment reminders: {e}")
            return 0
        
        finally:
            conn.close()
    
    def send_course_progress_notifications(self):
        """
        Send course progress notifications to all active students
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Find active students
            cursor.execute('''
                SELECT reg_number
                FROM students
                WHERE status = 'Active' OR status IS NULL
            ''')
            
            active_students = cursor.fetchall()
            
            # Send notifications
            for (reg_number,) in active_students:
                self.notification_system.send_course_progress_notification(reg_number)
            
            return len(active_students)
        
        except sqlite3.Error as e:
            print(f"Error sending course progress notifications: {e}")
            return 0
        
        finally:
            conn.close()
    
    def schedule_periodic_notifications(self):
        """
        Schedule periodic notifications
        """
        # Send payment reminders every 7 days
        payment_reminders = self.send_payment_reminder_notifications()
        print(f"Sent {payment_reminders} payment reminder notifications")
        
        # Send course progress notifications monthly
        progress_notifications = self.send_course_progress_notifications()
        print(f"Sent {progress_notifications} course progress notifications")
    
    def run(self):
        self.root.mainloop()
        
        # Schedule periodic notifications
        self.root.after(7 * 24 * 60 * 60 * 1000, self.schedule_periodic_notifications)  # 7 days

if __name__ == "__main__":
    # Uncomment the following line to reset the database
    # from utils.folder_setup import reset_database
    # reset_database()
    
    app = ImpactechApp()
    app.run() 