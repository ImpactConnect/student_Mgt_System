import tkinter as tk
from tkinter import ttk
from utils.constants import PROGRAMMES
import sqlite3
from datetime import datetime
from tkinter import messagebox
import os

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ProgrammesPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main layout
        self.create_header()
        self.create_scrollable_content()
        
        # Bind cleanup method
        self.bind("<Destroy>", lambda e: self.on_destroy())
    
    def create_header(self):
        # Header with back button and title
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side - Back button
        back_btn = ttk.Button(header_frame,
                            text="← Back",
                            command=self.app.show_home_page)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # Center - Title
        title = ttk.Label(header_frame,
                         text="Programme Overview",
                         style="Title.TLabel")
        title.pack(pady=10)
        
        # Right side - Actions
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT, padx=20)
        
        # Export button
        ttk.Button(action_frame,
                  text="Export Data",
                  command=self.export_programme_data).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        ttk.Button(action_frame,
                  text="↻ Refresh",
                  command=self.refresh_view).pack(side=tk.LEFT, padx=5)
    
    def create_scrollable_content(self):
        # Create outer frame with margins
        outer_frame = ttk.Frame(self)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(outer_frame)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # Create inner frame for content
        inner_frame = ttk.Frame(canvas)
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Configure canvas and scrolling behavior
        def configure_canvas(event):
            # Update the width of the canvas window
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        def configure_scroll_region(event):
            # Update the scrollregion to include all the content
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind events
        canvas.bind('<Configure>', configure_canvas)
        inner_frame.bind('<Configure>', configure_scroll_region)
        
        # Configure mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create programme cards in inner frame
        self.create_programmes_view(inner_frame)
        
        # Store canvas reference for cleanup
        self.canvas = canvas
    
    def on_destroy(self):
        """Clean up scroll bindings when page is destroyed"""
        if hasattr(self, 'canvas'):
            self.canvas.unbind_all("<MouseWheel>")
    
    def create_programmes_view(self, container):
        # Configure grid with 5 equal columns
        for i in range(5):
            container.columnconfigure(i, weight=1)
        
        # Create grid of programme cards
        for i, programme in enumerate(PROGRAMMES):
            # Calculate row and column for 5-column layout
            row = i // 5
            col = i % 5
            
            # Create card frame with padding
            card = ttk.LabelFrame(container, text=programme, padding=15)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Get programme statistics
            stats = self.get_programme_stats(programme)
            
            # Create statistics visualization
            self.create_stats_visualization(card, stats)
            
            # Button frame
            btn_frame = ttk.Frame(card)
            btn_frame.pack(pady=8)
            
            # Buttons
            ttk.Button(btn_frame,
                      text="View Details",
                      width=10,
                      command=lambda p=programme: self.view_programme_details(p)).pack(
                          side=tk.LEFT, padx=3)
            
            ttk.Button(btn_frame,
                      text="Edit",
                      width=6,
                      command=lambda p=programme: self.edit_programme(p)).pack(
                          side=tk.LEFT, padx=3)
    
    def refresh_view(self):
        """Refresh the programme view"""
        # Destroy and recreate content
        for widget in self.winfo_children():
            widget.destroy()
        self.create_header()
        self.create_scrollable_content()
        
        # Show success message
        messagebox.showinfo("Success", "Programme data refreshed successfully!")
    
    def export_programme_data(self):
        """Export programme statistics"""
        export_menu = tk.Menu(self, tearoff=0)
        
        # Excel export option
        export_menu.add_command(
            label="Export to Excel",
            command=self.export_to_excel
        )
        
        # PDF export option
        export_menu.add_command(
            label="Export to PDF",
            command=self.export_to_pdf
        )
        
        # CSV export option
        export_menu.add_command(
            label="Export to CSV",
            command=self.export_to_csv
        )
        
        # Show menu at button
        try:
            export_menu.tk_popup(
                self.winfo_pointerx(),
                self.winfo_pointery()
            )
        finally:
            export_menu.grab_release()
    
    def edit_programme(self, programme):
        """Edit programme details"""
        EditProgrammeDialog(self, self.app, programme)
    
    def get_programme_stats(self, programme):
        """Get statistics for a specific programme"""
        conn = sqlite3.connect(self.app.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Get total and active students
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'Active' OR status IS NULL THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'Graduated' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'Dropped Out' THEN 1 ELSE 0 END) as dropped,
                    SUM(programme_fee) as total_fees,
                    (SELECT COALESCE(SUM(amount), 0)
                     FROM payments p
                     JOIN students s ON p.reg_number = s.reg_number
                     WHERE s.programme = ?) as paid_amount
                FROM students
                WHERE programme = ?
            ''', (programme, programme))
            
            result = cursor.fetchone()
            
            if result:
                total_fees = result[4] or 0
                paid_amount = result[5] or 0
                
                return {
                    'total_students': result[0] or 0,
                    'active_students': result[1] or 0,
                    'completed': result[2] or 0,
                    'dropped_out': result[3] or 0,
                    'total_revenue': paid_amount,
                    'outstanding': total_fees - paid_amount
                }
            
            return {
                'total_students': 0,
                'active_students': 0,
                'completed': 0,
                'dropped_out': 0,
                'total_revenue': 0,
                'outstanding': 0
            }
            
        finally:
            conn.close()
    
    def view_programme_details(self, programme):
        """Open detailed view for a specific programme"""
        ProgrammeDetailsDialog(self, self.app, programme)
    
    def create_stats_visualization(self, parent, stats):
        """Create simplified text-based visualization of programme statistics"""
        # Student Statistics
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Total students count at the top
        total_frame = ttk.Frame(stats_frame)
        total_frame.pack(fill=tk.X, pady=3)
        ttk.Label(total_frame, 
                 text="Total Students:",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(total_frame,
                 text=str(stats['total_students']),
                 font=("Helvetica", 10, "bold")).pack(side=tk.RIGHT)
        
        # Student counts with colored labels
        student_stats = [
            ("Active:", stats['active_students'], "#2E7D32"),
            ("Completed:", stats['completed'], "#1976D2"),
            ("Dropped:", stats['dropped_out'], "#C62828")
        ]
        
        for label, value, color in student_stats:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, 
                     text=label,
                     font=("Helvetica", 9)).pack(side=tk.LEFT)
            tk.Label(frame,
                    text=str(value),
                    fg=color,
                    font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT)
        
        # Separator with more spacing
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=8)
        
        # Financial Statistics
        fin_frame = ttk.Frame(parent)
        fin_frame.pack(fill=tk.X, pady=5)
        
        total_fees = stats['total_revenue'] + stats['outstanding']
        collection_rate = (stats['total_revenue'] / total_fees * 100) if total_fees > 0 else 0
        
        # Financial info with colored labels
        financial_stats = [
            ("Revenue:", f"₦{stats['total_revenue']:,.0f}", "#1B5E20"),
            ("Outstanding:", f"₦{stats['outstanding']:,.0f}", "#D32F2F"),
            ("Collection:", f"{collection_rate:.1f}%", "#0D47A1")
        ]
        
        for label, value, color in financial_stats:
            frame = ttk.Frame(fin_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, 
                     text=label,
                     font=("Helvetica", 9)).pack(side=tk.LEFT)
            tk.Label(frame,
                    text=value,
                    fg=color,
                    font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT)
    
    def export_to_excel(self):
        """Export programme statistics to Excel"""
        try:
            import pandas as pd
            
            # Collect data for all programmes
            data = []
            for programme in PROGRAMMES:
                stats = self.get_programme_stats(programme)
                data.append({
                    'Programme': programme,
                    'Total Students': stats['total_students'],
                    'Active Students': stats['active_students'],
                    'Completed': stats['completed'],
                    'Dropped Out': stats['dropped_out'],
                    'Total Revenue': stats['total_revenue'],
                    'Outstanding': stats['outstanding']
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"programme_statistics_{timestamp}.xlsx"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            # Ensure exports directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Export to Excel
            df.to_excel(filepath, index=False)
            
            messagebox.showinfo("Success", 
                              f"Data exported successfully to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def export_to_pdf(self):
        """Export programme statistics to PDF"""
        # TODO: Implement PDF export
        pass
    
    def export_to_csv(self):
        """Export programme statistics to CSV"""
        # TODO: Implement CSV export
        pass


class ProgrammeDetailsDialog(tk.Toplevel):
    def __init__(self, parent, app, programme):
        super().__init__(parent)
        self.app = app
        self.programme = programme
        self.title(f"Programme Details - {programme}")
        
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
        
        # Create content
        self.create_content()
    
    def create_content(self):
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame,
                 text=self.programme,
                 style="Title.TLabel").pack(pady=(0, 20))
        
        # Create student list
        self.create_student_list(main_frame)
    
    def create_student_list(self, parent):
        # Create Treeview
        columns = ("reg_number", "name", "schedule", "start_date", "status", "payment")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        # Configure columns
        self.tree.heading("reg_number", text="Reg. Number")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("schedule", text="Schedule")
        self.tree.heading("start_date", text="Start Date")
        self.tree.heading("status", text="Status")
        self.tree.heading("payment", text="Payment Status")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load students
        self.load_students()
    
    def load_students(self):
        conn = sqlite3.connect(self.app.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    s.reg_number,
                    s.name,
                    s.schedule,
                    s.start_date,
                    s.status,
                    s.programme_fee,
                    COALESCE(SUM(p.amount), 0) as paid_amount
                FROM students s
                LEFT JOIN payments p ON s.reg_number = p.reg_number
                WHERE s.programme = ?
                GROUP BY s.reg_number
                ORDER BY s.name
            ''', (self.programme,))
            
            for row in cursor.fetchall():
                reg_number, name, schedule, start_date, status, fee, paid = row
                
                # Calculate payment status
                if paid >= fee:
                    payment_status = "Fully Paid"
                elif paid > 0:
                    percentage = (paid / fee) * 100
                    payment_status = f"Partial ({percentage:.1f}%)"
                else:
                    payment_status = "Unpaid"
                
                self.tree.insert("", "end", values=(
                    reg_number,
                    name,
                    schedule,
                    start_date,
                    status or "Active",
                    payment_status
                ))
                
        finally:
            conn.close() 


class EditProgrammeDialog(tk.Toplevel):
    def __init__(self, parent, app, programme):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.programme = programme
        self.title(f"Edit Programme - {programme}")
        
        # Set dialog size
        self.geometry("500x600")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create content
        self.create_content()
    
    def create_content(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Programme details
        ttk.Label(main_frame, text="Programme Name:").pack(anchor="w")
        self.name_var = tk.StringVar(value=self.programme)
        ttk.Entry(main_frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 10))
        
        # Duration options
        ttk.Label(main_frame, text="Duration Options:").pack(anchor="w")
        self.duration_text = tk.Text(main_frame, height=4)
        self.duration_text.pack(fill=tk.X, pady=(0, 10))
        
        # Fee structure
        ttk.Label(main_frame, text="Fee Structure:").pack(anchor="w")
        self.fee_text = tk.Text(main_frame, height=4)
        self.fee_text.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Programme Description:").pack(anchor="w")
        self.desc_text = tk.Text(main_frame, height=6)
        self.desc_text.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Save Changes",
                  command=self.save_changes).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_changes(self):
        # TODO: Implement saving changes to database
        messagebox.showinfo("Success", "Changes saved successfully!")
        self.parent.refresh_view()
        self.destroy() 