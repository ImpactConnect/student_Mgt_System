import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import PROGRAMMES, SCHEDULES, STUDENT_STATUSES
from datetime import datetime
import os

class EditStudentDialog(tk.Toplevel):
    def __init__(self, parent, app, student_data):
        super().__init__(parent)
        self.app = app
        self.student_data = student_data
        self.title("Edit Student Details")
        
        # Set dialog size and make it modal
        dialog_width = 500
        dialog_height = 700  # Increased height to accommodate new fields
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.transient(parent)
        self.grab_set()
        
        # Create main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form
        self.create_form(main_frame)
        
    def create_form(self, parent):
        # Create form fields
        fields = [
            ("Name:", "name", "entry"),
            ("Age:", "age", "entry"),
            ("Gender:", "gender", "combobox", ["Male", "Female"]),
            ("Programme:", "programme", "combobox", PROGRAMMES),
            ("Duration:", "duration", "entry"),
            ("Schedule:", "schedule", "combobox", SCHEDULES),
            ("Start Date:", "start_date", "entry"),
            ("Programme Fee:", "programme_fee", "entry")
        ]
        
        # Create and populate fields
        self.field_vars = {}
        for i, (label, key, field_type, *options) in enumerate(fields):
            # Label
            ttk.Label(parent, text=label, style="Bold.TLabel").grid(
                row=i, column=0, sticky="e", padx=5, pady=5)
            
            # Field
            if field_type == "entry":
                var = tk.StringVar(value=str(self.student_data.get(key, "")))
                ttk.Entry(parent, textvariable=var, width=30).grid(
                    row=i, column=1, sticky="ew", padx=5)
                self.field_vars[key] = var
            elif field_type == "combobox":
                var = tk.StringVar(value=self.student_data.get(key, ""))
                combo = ttk.Combobox(parent, 
                                   textvariable=var,
                                   values=options[0],
                                   state="readonly",
                                   width=27)
                combo.grid(row=i, column=1, sticky="ew", padx=5)
                self.field_vars[key] = var
        
        # Configure grid column
        parent.columnconfigure(1, weight=1)
        
        # Add status dropdown
        status_label = ttk.Label(parent, text="Student Status:")
        status_label.grid(row=len(fields), column=0, sticky="e", padx=5, pady=5)
        
        self.status_var = tk.StringVar(
            value=self.student_data.get('status', 'Active')
        )
        status_dropdown = ttk.Combobox(
            parent, 
            textvariable=self.status_var, 
            values=STUDENT_STATUSES, 
            state="readonly",
            width=30
        )
        status_dropdown.grid(
            row=len(fields), column=1, sticky="ew", padx=5, pady=5
        )
        
        # Add scholarship checkbox
        self.scholarship_var = tk.BooleanVar(
            value=bool(self.student_data.get('scholarship', False))
        )
        scholarship_check = ttk.Checkbutton(
            parent, 
            text="Scholarship Student", 
            variable=self.scholarship_var
        )
        scholarship_check.grid(
            row=len(fields)+1, column=1, sticky="w", padx=5, pady=5
        )
        
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        # Save button
        save_btn = ttk.Button(button_frame,
                            text="Save Changes",
                            style="Modern.TButton",
                            command=self.save_changes)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame,
                              text="Cancel",
                              style="Modern.TButton",
                              command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save_changes(self):
        try:
            # Validate fields
            updates = {}
            for key, var in self.field_vars.items():
                value = var.get().strip()
                if key == "age":
                    if value:  # Allow empty age
                        try:
                            value = int(value)
                        except ValueError:
                            messagebox.showerror("Error", "Age must be a number")
                            return
                elif key == "programme_fee":
                    if value:  # Allow empty fee
                        try:
                            value = float(value)
                        except ValueError:
                            messagebox.showerror("Error", "Programme fee must be a number")
                            return
                updates[key] = value
            
            # Add status and scholarship to updates
            updates['status'] = self.status_var.get()
            updates['scholarship'] = 1 if self.scholarship_var.get() else 0
            
            # Update database
            success = self.app.db.update_student(self.student_data['reg_number'], updates)
            
            if success:
                messagebox.showinfo("Success", "Student details updated successfully")
                self.destroy()
                # Refresh parent window if possible
                try:
                    if hasattr(self.master, 'refresh_profile'):
                        self.master.refresh_profile()
                    elif hasattr(self.master, 'load_students'):
                        self.master.load_students()
                except Exception as e:
                    print(f"Could not refresh parent window: {e}")
            else:
                messagebox.showerror("Error", "Failed to update student details")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}") 