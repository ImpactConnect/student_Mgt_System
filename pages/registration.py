import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import platform
import subprocess
from utils.constants import PROGRAMMES, DURATIONS, GENDERS, SCHEDULES

class AdmissionLetterGenerator:
    @staticmethod
    def generate_admission_letter(student_data):
        """Generate PDF admission letter for a newly registered student"""
        try:
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(
                os.path.expanduser("~/Documents"), 
                "Impactech", 
                "exports"
            )
            os.makedirs(exports_dir, exist_ok=True)
            
            # Generate filename
            filename = f"admission_letter_{student_data['reg_number']}.pdf"
            filepath = os.path.join(exports_dir, filename)
            
            # Create PDF with custom letterhead
            def add_page_number(canvas, doc):
                """Add page numbers and letterhead"""
                canvas.saveState()
                AdmissionLetterGenerator.create_letterhead(canvas, doc)
                
                # Page number
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(doc.width + doc.leftMargin, 0.75 * inch, text)
                
                canvas.restoreState()
            
            # Create PDF
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=letter, 
                rightMargin=72, 
                leftMargin=72, 
                topMargin=120,  # Increased for letterhead
                bottomMargin=18
            )
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'Title', 
                parent=styles['Heading1'], 
                alignment=TA_CENTER,
                fontSize=16,
                textColor=colors.HexColor('#1976D2'),  # Blue title
                spaceAfter=12
            )
            
            # PDF content
            story = []
            
            # Title
            story.append(Paragraph("Admission Offer Letter", title_style))
            story.append(Spacer(1, 12))
            
            # Calculate programme dates
            start_date = datetime.strptime(
                str(student_data['start_date']), 
                "%Y-%m-%d"
            )
            
            # Duration mapping
            duration_map = {
                '1 month': 30,
                '3 months': 90,
                '6 months': 180,
                '9 months': 270
            }
            
            # Calculate end date
            days = duration_map.get(student_data['duration'], 90)
            end_date = start_date + timedelta(days=days)
            
            # Calculate balance payment date (middle of programme)
            balance_payment_date = start_date + timedelta(days=days//2)
            
            # Calculate payment amounts
            total_fee = student_data['programme_fee']
            upfront_payment = total_fee * 0.5  # 50% upfront
            balance_payment = total_fee * 0.5  # 50% balance
            
            # Personalized welcome paragraph
            welcome_text = (
                f"Dear {student_data['name']},<br/><br/>"
                "We are pleased to inform you that you have been accepted into "
                f"the {student_data['programme']} programme at Impactech Academy. "
                "This is a significant milestone in your professional development, "
                "and we are excited to support your learning journey."
            )
            story.append(Paragraph(welcome_text, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Create a table for key details
            details_data = [
                ["Student Name:", student_data['name']],
                ["Registration Number:", student_data['reg_number']],
                ["Programme:", f"{student_data['programme']} ({student_data['duration']})"],
                ["Programme Start Date:", start_date.strftime('%d %B %Y')],
                ["Programme End Date:", end_date.strftime('%d %B %Y')],
                ["Total Programme Fee:", f"₦{total_fee:,.2f}"]
            ]
            
            details_table = Table(details_data, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#E0E0E0')),
                ('TEXTCOLOR', (0,0), (0,-1), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white)
            ]))
            story.append(details_table)
            story.append(Spacer(1, 12))
            
            # Payment Schedule
            story.append(Paragraph("Payment Schedule:", styles['Heading3']))
            payment_data = [
                ["Payment Stage", "Amount", "Due Date"],
                ["50% Upfront Payment", f"₦{upfront_payment:,.2f}", start_date.strftime('%d %B %Y')],
                ["50% Balance Payment", f"₦{balance_payment:,.2f}", balance_payment_date.strftime('%d %B %Y')]
            ]
            
            payment_table = Table(payment_data, colWidths=[2*inch, 2*inch, 2*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            story.append(payment_table)
            story.append(Spacer(1, 12))
            
            # Payment Terms Explanation
            payment_explanation = (
                "Payment Terms: The total programme fee is to be paid in two installments. "
                "The first 50% is due at the start of the programme, and the remaining 50% "
                f"must be paid on or before {balance_payment_date.strftime('%d %B %Y')}, "
                "which is the midpoint of the programme duration."
            )
            story.append(Paragraph(payment_explanation, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Closing paragraph
            closing_text = (
                "We look forward to welcoming you to Impactech Academy. "
                "This is the beginning of an exciting journey of learning and growth. "
                "If you have any questions, please do not hesitate to contact our admissions team."
            )
            story.append(Paragraph(closing_text, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Signature space
            story.append(Paragraph("Best Regards,", styles['Normal']))
            story.append(Paragraph("Impactech Academy Admissions Team", styles['Normal']))
            
            # Build PDF with page numbers and letterhead
            doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
            
            return filepath
        
        except Exception as e:
            print(f"Failed to generate admission letter: {str(e)}")
            return None

    @staticmethod
    def create_letterhead(canvas, doc):
        """Create a custom letterhead for the admission letter"""
        # Company details
        company_details = [
            "IMPACTTECH CODING ACADEMY",
            "Suite 4/5 De-West Plaza, Power Plant Road, Agwa Kaduna",
            "Phone: 07032196863, Email: info@impacttech-solutions.com"
        ]
        
        # Calculate the center of the page
        page_center = doc.width / 2 + doc.leftMargin
        
        # Draw company name
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColor(colors.HexColor('#1976D2'))  # Deep blue color
        text_width = canvas.stringWidth(company_details[0], "Helvetica-Bold", 14)
        canvas.drawString(page_center - text_width/2, doc.height + doc.topMargin - 1*inch, company_details[0])
        
        # Draw address and contact details
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.black)
        y_position = doc.height + doc.topMargin - 1.2*inch
        
        for detail in company_details[1:]:
            text_width = canvas.stringWidth(detail, "Helvetica", 10)
            canvas.drawString(page_center - text_width/2, y_position, detail)
            y_position -= 12
        
        # Draw line separator with more prominence
        canvas.setStrokeColor(colors.HexColor('#1976D2'))  # Blue line
        canvas.setLineWidth(1.5)
        line_y = doc.height + doc.topMargin - 1.5*inch
        canvas.line(
            doc.leftMargin, 
            line_y, 
            doc.width + doc.leftMargin, 
            line_y
        )

class RegistrationDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("New Student Registration")
        
        # Set dialog size
        dialog_width = 600  # Reduced width for single column
        dialog_height = 700  # Increased height for content
        
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
        
        # Store receipt path
        self.current_receipt_path = None
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Add scrollable frame to canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=dialog_width-50)
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create main container with padding
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form sections in single column
        self.create_personal_info(main_frame)
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.create_programme_info(main_frame)
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.create_payment_info(main_frame)
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.create_additional_info(main_frame)
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.create_buttons(main_frame)
        
        # Configure mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_personal_info(self, parent):
        # Personal Information Section
        info_frame = ttk.LabelFrame(parent, text="Personal Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Name
        ttk.Label(info_frame, text="Full Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var, width=50).pack(
            fill=tk.X, pady=(0, 10))
        
        # Age
        ttk.Label(info_frame, text="Age:").pack(anchor=tk.W)
        self.age_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.age_var, width=10).pack(
            anchor=tk.W, pady=(0, 10))
        
        # Gender
        ttk.Label(info_frame, text="Gender:").pack(anchor=tk.W)
        self.gender_var = tk.StringVar()
        gender_frame = ttk.Frame(info_frame)
        gender_frame.pack(fill=tk.X, pady=(0, 5))
        
        for gender in GENDERS:
            ttk.Radiobutton(gender_frame, text=gender, value=gender,
                          variable=self.gender_var).pack(side=tk.LEFT, padx=5)
    
    def create_programme_info(self, parent):
        # Programme Information Section
        prog_frame = ttk.LabelFrame(parent, text="Programme Information", padding=10)
        prog_frame.pack(fill=tk.X, pady=5)
        
        # Programme
        ttk.Label(prog_frame, text="Programme:").pack(anchor=tk.W)
        self.programme_var = tk.StringVar()
        ttk.Combobox(prog_frame, textvariable=self.programme_var,
                    values=PROGRAMMES, state="readonly", width=48).pack(
            fill=tk.X, pady=(0, 10))
        
        # Duration
        ttk.Label(prog_frame, text="Duration:").pack(anchor=tk.W)
        self.duration_var = tk.StringVar()
        ttk.Combobox(prog_frame, textvariable=self.duration_var,
                    values=DURATIONS, state="readonly", width=48).pack(
            fill=tk.X, pady=(0, 10))
        
        # Schedule
        ttk.Label(prog_frame, text="Schedule:").pack(anchor=tk.W)
        self.schedule_var = tk.StringVar()
        ttk.Combobox(prog_frame, textvariable=self.schedule_var,
                    values=SCHEDULES, state="readonly", width=48).pack(
            fill=tk.X, pady=(0, 10))
        
        # Start Date
        ttk.Label(prog_frame, text="Start Date:").pack(anchor=tk.W)
        self.start_date = DateEntry(prog_frame, width=48, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.pack(fill=tk.X, pady=(0, 5))
    
    def create_payment_info(self, parent):
        # Payment Information Section
        payment_frame = ttk.LabelFrame(parent, text="Payment Information", padding=10)
        payment_frame.pack(fill=tk.X, pady=5)
        
        # Programme Fee
        ttk.Label(payment_frame, text="Programme Fee:").pack(anchor=tk.W)
        self.fee_var = tk.StringVar()
        ttk.Entry(payment_frame, textvariable=self.fee_var, width=50).pack(
            fill=tk.X, pady=(0, 10))
        
        # Initial Payment
        ttk.Label(payment_frame, text="Initial Payment:").pack(anchor=tk.W)
        self.payment_var = tk.StringVar()
        ttk.Entry(payment_frame, textvariable=self.payment_var, width=50).pack(
            fill=tk.X, pady=(0, 5))
    
    def create_additional_info(self, parent):
        # Additional Information Section
        add_frame = ttk.LabelFrame(parent, text="Additional Information", padding=10)
        add_frame.pack(fill=tk.X, pady=5)
        
        # Keep this method empty or remove it entirely
        pass
    
    def create_buttons(self, parent):
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10)
        
        # Cancel button
        ttk.Button(button_frame, text="Cancel",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # Register button
        ttk.Button(button_frame, text="Register Student",
                  style="Modern.TButton",
                  command=self.submit_registration).pack(side=tk.LEFT, padx=5)
    
    def validate_form(self):
        # Basic validation
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Please enter student name")
            return False
        
        try:
            age = int(self.age_var.get())
            if age < 5 or age > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age")
            return False
        
        if not self.gender_var.get():
            messagebox.showerror("Error", "Please select gender")
            return False
        
        if not self.programme_var.get():
            messagebox.showerror("Error", "Please select a programme")
            return False
        
        if not self.duration_var.get():
            messagebox.showerror("Error", "Please select programme duration")
            return False
        
        if not self.schedule_var.get():
            messagebox.showerror("Error", "Please select class schedule")
            return False
        
        try:
            fee = float(self.fee_var.get())
            payment = float(self.payment_var.get())
            if fee < 0 or payment < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid payment amounts")
            return False
        
        return True

    def generate_reg_number(self, programme):
        year = datetime.now().year
        prog_code = ''.join(word[0] for word in programme.split()[:3]).upper()
        serial = self.app.db.generate_serial_number(programme, year)
        return f"IMPTECH-{prog_code}-{year}-{serial}"

    def submit_registration(self):
        if not self.validate_form():
            return
        
        # Generate registration number
        reg_number = self.generate_reg_number(self.programme_var.get())
        
        # Prepare student data
        student_data = {
            'reg_number': reg_number,
            'name': self.name_var.get().strip(),
            'age': int(self.age_var.get()),
            'gender': self.gender_var.get(),
            'programme': self.programme_var.get(),
            'start_date': self.start_date.get_date(),
            'duration': self.duration_var.get(),
            'schedule': self.schedule_var.get(),
            'programme_fee': float(self.fee_var.get()),
            'initial_payment': float(self.payment_var.get()),
            'status': 'Active',
            'scholarship': 0
        }
        
        # Save to database
        success, receipt_path, error = self.app.db.save_student(student_data)
        
        if success:
            # Generate admission letter
            admission_letter_path = AdmissionLetterGenerator.generate_admission_letter(student_data)
            
            # Show success message with admission letter option
            response = messagebox.askyesno(
                "Registration Successful", 
                f"Student registered successfully!\n"
                f"Registration Number: {reg_number}\n\n"
                "Would you like to view the admission letter?"
            )
            
            # Open admission letter if user chooses yes
            if response and admission_letter_path:
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', admission_letter_path])
                    elif platform.system() == 'Windows':
                        os.startfile(admission_letter_path)
                    else:  # Linux
                        subprocess.run(['xdg-open', admission_letter_path])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open admission letter: {str(e)}")
            
            # Store receipt path if payment was made
            self.current_receipt_path = receipt_path
            
            # If there was an initial payment, show the receipt buttons
            if student_data['initial_payment'] > 0 and receipt_path:
                self.show_receipt_buttons()
            
            # Close the registration dialog
            self.destroy()
        else:
            messagebox.showerror("Error", 
                               f"Failed to register student: {error}")

    def show_receipt_buttons(self):
        # Clear the buttons frame
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Create new buttons frame centered at the bottom
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Center the buttons
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor=tk.CENTER)
        
        # Preview Receipt button
        preview_btn = ttk.Button(button_container,
                               text="Preview Receipt",
                               style="Modern.TButton",
                               command=self.preview_receipt)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # Print Receipt button
        print_btn = ttk.Button(button_container,
                              text="Print Receipt",
                              style="Modern.TButton",
                              command=self.print_receipt)
        print_btn.pack(side=tk.LEFT, padx=5)
        
        # Done button
        done_btn = ttk.Button(button_container,
                             text="Done",
                             style="Modern.TButton",
                             command=self.destroy)
        done_btn.pack(side=tk.LEFT, padx=5)

    def preview_receipt(self):
        """Open the receipt PDF with the default PDF viewer"""
        if not self.current_receipt_path:
            messagebox.showerror("Error", "Receipt not found")
            return
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.current_receipt_path])
            elif platform.system() == 'Windows':
                os.startfile(self.current_receipt_path)
            else:  # Linux
                subprocess.run(['xdg-open', self.current_receipt_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open receipt: {str(e)}")

    def print_receipt(self):
        """Print the receipt using the default printer"""
        if not self.current_receipt_path:
            messagebox.showerror("Error", "Receipt not found")
            return
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['lpr', self.current_receipt_path])
            elif platform.system() == 'Windows':
                subprocess.run(['print', self.current_receipt_path], shell=True)
            else:  # Linux
                subprocess.run(['lpr', self.current_receipt_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {str(e)}")
    
    # Rest of the methods remain the same (validate_form, submit_registration, etc.)
    # Just update self.app.show_home_page() to self.destroy() where appropriate 