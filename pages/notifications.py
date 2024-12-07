import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class NotificationsPage(ttk.Frame):
    def __init__(self, parent, app):
        """
        Initialize Notifications Page
        
        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main layout
        self.create_header()
        self.create_notifications_view()
    
    def create_header(self):
        """Create page header with title and actions"""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button
        back_btn = ttk.Button(header_frame,
                            text="← Back",
                            command=self.app.show_home_page)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # Title
        title = ttk.Label(header_frame,
                         text="Notifications",
                         style="Title.TLabel")
        title.pack(pady=10)
        
        # Actions frame
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT, padx=20)
        
        # Bulk Notification Button
        bulk_btn = ttk.Button(actions_frame,
                             text="Send Bulk Notification",
                             command=self.show_bulk_notification_dialog)
        bulk_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh Button
        refresh_btn = ttk.Button(actions_frame,
                               text="↻ Refresh",
                               command=self.refresh_notifications)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_notifications_view(self):
        """Create the main notifications view with treeview"""
        # Outer frame for padding
        outer_frame = ttk.Frame(self)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Create Treeview
        columns = ("id", "type", "message", "created_at", "status")
        self.notifications_tree = ttk.Treeview(outer_frame, 
                                              columns=columns, 
                                              show="headings")
        
        # Configure columns
        self.notifications_tree.heading("id", text="ID")
        self.notifications_tree.heading("type", text="Type")
        self.notifications_tree.heading("message", text="Message")
        self.notifications_tree.heading("created_at", text="Date")
        self.notifications_tree.heading("status", text="Status")
        
        # Column widths
        self.notifications_tree.column("id", width=50, anchor="center")
        self.notifications_tree.column("type", width=100, anchor="center")
        self.notifications_tree.column("message", width=400)
        self.notifications_tree.column("created_at", width=150, anchor="center")
        self.notifications_tree.column("status", width=80, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(outer_frame, 
                                 orient=tk.VERTICAL, 
                                 command=self.notifications_tree.yview)
        self.notifications_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.notifications_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view details
        self.notifications_tree.bind('<Double-1>', self.view_notification_details)
        
        # Load initial notifications
        self.load_notifications()
    
    def load_notifications(self):
        """Load all notifications from the database"""
        # Clear existing items
        for item in self.notifications_tree.get_children():
            self.notifications_tree.delete(item)
        
        # Fetch all notifications
        conn = self.app.db.db_path
        notifications = self.app.notification_system.get_student_notifications(
            self.app.current_student['reg_number']
        )
        
        # Populate treeview
        for notification in notifications:
            status = "Read" if notification['is_read'] else "Unread"
            self.notifications_tree.insert("", "end", values=(
                notification['id'],
                notification['type'].replace('_', ' ').title(),
                notification['message'],
                notification['created_at'],
                status
            ))
    
    def view_notification_details(self, event):
        """Show detailed view of a selected notification"""
        # Get selected item
        selected_item = self.notifications_tree.selection()
        if not selected_item:
            return
        
        # Get notification details
        values = self.notifications_tree.item(selected_item[0])['values']
        notification_id, type_, message, created_at, status = values
        
        # Create details dialog
        details_dialog = tk.Toplevel(self)
        details_dialog.title("Notification Details")
        details_dialog.geometry("500x400")
        
        # Details frame
        details_frame = ttk.Frame(details_dialog, padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notification details
        ttk.Label(details_frame, text=f"Type: {type_}", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)
        ttk.Label(details_frame, text=f"Date: {created_at}", font=("Helvetica", 10)).pack(anchor="w", pady=5)
        
        # Message text widget
        message_text = tk.Text(details_frame, wrap=tk.WORD, height=10)
        message_text.insert(tk.END, message)
        message_text.config(state=tk.DISABLED)  # Make read-only
        message_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Mark as read button
        if status == "Unread":
            def mark_as_read():
                self.app.notification_system.mark_notification_as_read(notification_id)
                self.load_notifications()
                details_dialog.destroy()
            
            ttk.Button(details_frame, 
                      text="Mark as Read", 
                      command=mark_as_read).pack(pady=10)
        
        # Close button
        ttk.Button(details_frame, 
                  text="Close", 
                  command=details_dialog.destroy).pack(pady=10)
    
    def show_bulk_notification_dialog(self):
        """Show dialog to send bulk notifications"""
        dialog = tk.Toplevel(self)
        dialog.title("Send Bulk Notification")
        dialog.geometry("500x400")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Programme selection
        ttk.Label(main_frame, text="Select Programme (Optional):").pack(anchor="w")
        programme_var = tk.StringVar()
        from utils.constants import PROGRAMMES
        programme_combo = ttk.Combobox(main_frame, 
                                      textvariable=programme_var,
                                      values=["All"] + PROGRAMMES,
                                      state="readonly")
        programme_combo.set("All")
        programme_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Message input
        ttk.Label(main_frame, text="Notification Message:").pack(anchor="w")
        message_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        def send_notification():
            # Get message and programme
            message = message_text.get("1.0", tk.END).strip()
            programme = programme_var.get() if programme_var.get() != "All" else None
            
            # Validate message
            if not message:
                messagebox.showerror("Error", "Message cannot be empty")
                return
            
            # Send notification
            notifications_sent = self.app.notification_system.send_bulk_notification(
                programme=programme, 
                message=message
            )
            
            messagebox.showinfo("Notification Sent", 
                               f"Sent {notifications_sent} notifications")
            dialog.destroy()
        
        # Send button
        ttk.Button(main_frame, text="Send Notification", command=send_notification).pack(pady=10)
    
    def refresh_notifications(self):
        """Refresh the notifications view"""
        self.load_notifications()
        messagebox.showinfo("Refreshed", "Notifications updated successfully!") 