import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SettingsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Load current settings
        self.settings = self.load_settings()
        
        # Create layout
        self.create_header()
        self.create_settings_content()
    
    def create_header(self):
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button
        back_btn = ttk.Button(header_frame,
                            text="← Back",
                            command=self.app.show_home_page)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # Title
        title = ttk.Label(header_frame,
                         text="System Settings",
                         style="Title.TLabel")
        title.pack(pady=10)
    
    def create_settings_content(self):
        # Create notebook for settings categories
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # General Settings
        general_frame = ttk.Frame(notebook, padding=20)
        notebook.add(general_frame, text="General")
        self.create_general_settings(general_frame)
        
        # Appearance Settings
        appearance_frame = ttk.Frame(notebook, padding=20)
        notebook.add(appearance_frame, text="Appearance")
        self.create_appearance_settings(appearance_frame)
        
        # Receipt Settings
        receipt_frame = ttk.Frame(notebook, padding=20)
        notebook.add(receipt_frame, text="Receipt")
        self.create_receipt_settings(receipt_frame)
        
        # Backup Settings
        backup_frame = ttk.Frame(notebook, padding=20)
        notebook.add(backup_frame, text="Backup")
        self.create_backup_settings(backup_frame)
        
        # Save button
        save_btn = ttk.Button(self,
                            text="Save Changes",
                            style="Accent.TButton",
                            command=self.save_settings)
        save_btn.pack(pady=20)
    
    def create_general_settings(self, parent):
        # School Information
        school_frame = ttk.LabelFrame(parent, text="School Information", padding=10)
        school_frame.pack(fill=tk.X, pady=(0, 20))
        
        # School Name
        ttk.Label(school_frame, text="School Name:").pack(anchor="w")
        self.school_name_var = tk.StringVar(value=self.settings.get('school_name', 'Impactech Academy'))
        ttk.Entry(school_frame, textvariable=self.school_name_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Address
        ttk.Label(school_frame, text="Address:").pack(anchor="w")
        self.address_var = tk.StringVar(value=self.settings.get('address', ''))
        ttk.Entry(school_frame, textvariable=self.address_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Contact Information
        ttk.Label(school_frame, text="Contact Email:").pack(anchor="w")
        self.email_var = tk.StringVar(value=self.settings.get('email', ''))
        ttk.Entry(school_frame, textvariable=self.email_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Currency Settings
        currency_frame = ttk.LabelFrame(parent, text="Currency Settings", padding=10)
        currency_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(currency_frame, text="Currency Symbol:").pack(side=tk.LEFT, padx=5)
        self.currency_var = tk.StringVar(value=self.settings.get('currency', '₦'))
        ttk.Entry(currency_frame, textvariable=self.currency_var, width=5).pack(side=tk.LEFT, padx=5)
    
    def create_appearance_settings(self, parent):
        # Theme Settings
        theme_frame = ttk.LabelFrame(parent, text="Theme Settings", padding=10)
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Color Theme
        ttk.Label(theme_frame, text="Color Theme:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'Light'))
        themes = ['Light', 'Dark', 'System']
        ttk.OptionMenu(theme_frame, self.theme_var, self.theme_var.get(), *themes).pack(anchor="w", pady=(0, 10))
        
        # Font Settings
        font_frame = ttk.LabelFrame(parent, text="Font Settings", padding=10)
        font_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(font_frame, text="Default Font Size:").pack(anchor="w")
        self.font_size_var = tk.StringVar(value=self.settings.get('font_size', '12'))
        ttk.Spinbox(font_frame, from_=8, to=16, textvariable=self.font_size_var, width=10).pack(anchor="w")
    
    def create_receipt_settings(self, parent):
        # Receipt Customization
        receipt_frame = ttk.LabelFrame(parent, text="Receipt Customization", padding=10)
        receipt_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo Settings
        ttk.Label(receipt_frame, text="School Logo:").pack(anchor="w")
        logo_frame = ttk.Frame(receipt_frame)
        logo_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.logo_path_var = tk.StringVar(value=self.settings.get('logo_path', ''))
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side=tk.LEFT)
        
        # Footer Text
        ttk.Label(receipt_frame, text="Receipt Footer Text:").pack(anchor="w")
        self.footer_var = tk.StringVar(value=self.settings.get('receipt_footer', 'Thank you for your payment!'))
        ttk.Entry(receipt_frame, textvariable=self.footer_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Auto-print Option
        self.autoprint_var = tk.BooleanVar(value=self.settings.get('auto_print', False))
        ttk.Checkbutton(receipt_frame, 
                       text="Automatically print receipts after payment",
                       variable=self.autoprint_var).pack(anchor="w")
    
    def create_backup_settings(self, parent):
        # Backup Configuration
        backup_frame = ttk.LabelFrame(parent, text="Backup Configuration", padding=10)
        backup_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Backup Location
        ttk.Label(backup_frame, text="Backup Location:").pack(anchor="w")
        location_frame = ttk.Frame(backup_frame)
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.backup_path_var = tk.StringVar(value=self.settings.get('backup_path', ''))
        ttk.Entry(location_frame, textvariable=self.backup_path_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(location_frame, text="Browse", command=self.browse_backup).pack(side=tk.LEFT)
        
        # Auto-backup Options
        self.autobackup_var = tk.BooleanVar(value=self.settings.get('auto_backup', True))
        ttk.Checkbutton(backup_frame,
                       text="Enable automatic backups",
                       variable=self.autobackup_var).pack(anchor="w")
        
        # Backup Frequency
        freq_frame = ttk.Frame(backup_frame)
        freq_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(freq_frame, text="Backup every:").pack(side=tk.LEFT)
        self.backup_freq_var = tk.StringVar(value=self.settings.get('backup_frequency', '7'))
        ttk.Spinbox(freq_frame, from_=1, to=30, width=5, textvariable=self.backup_freq_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(freq_frame, text="days").pack(side=tk.LEFT)
        
        # Manual Backup Button
        ttk.Button(backup_frame,
                  text="Backup Now",
                  command=self.manual_backup).pack(anchor="w", pady=10)
    
    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = os.path.join(self.app.app_path, "config", "settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {}
    
    def save_settings(self):
        """Save settings to JSON file"""
        settings = {
            'school_name': self.school_name_var.get(),
            'address': self.address_var.get(),
            'email': self.email_var.get(),
            'currency': self.currency_var.get(),
            'theme': self.theme_var.get(),
            'font_size': self.font_size_var.get(),
            'logo_path': self.logo_path_var.get(),
            'receipt_footer': self.footer_var.get(),
            'auto_print': self.autoprint_var.get(),
            'backup_path': self.backup_path_var.get(),
            'auto_backup': self.autobackup_var.get(),
            'backup_frequency': self.backup_freq_var.get()
        }
        
        try:
            config_dir = os.path.join(self.app.app_path, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            settings_path = os.path.join(config_dir, "settings.json")
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def browse_logo(self):
        """Browse for school logo"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if filename:
            self.logo_path_var.set(filename)
    
    def browse_backup(self):
        """Browse for backup location"""
        from tkinter import filedialog
        dirname = filedialog.askdirectory(title="Select Backup Location")
        if dirname:
            self.backup_path_var.set(dirname)
    
    def manual_backup(self):
        """Perform manual backup"""
        # TODO: Implement backup functionality
        messagebox.showinfo("Backup", "Backup functionality will be implemented soon!") 