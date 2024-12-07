import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os
from datetime import datetime, timedelta
import platform
import subprocess

# Modern color palette
MODERN_COLORS = {
    'primary': '#1976D2',    # Blue
    'secondary': '#2E7D32',  # Green
    'accent': '#FF9800',     # Orange
    'background': '#F5F5F5', # Light Grey
    'text': '#333333'        # Dark Grey
}

class ModernButton(ttk.Button):
    def __init__(self, parent, **kwargs):
        kwargs['style'] = 'Modern.TButton'
        super().__init__(parent, **kwargs)

class ReportsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style='Reports.TFrame')
        self.pack(fill=tk.BOTH, expand=True)
        
        # Configure modern styles
        self.configure_styles()
        
        # Create main layout
        self.create_header()
        self.create_report_sections()
    
    def configure_styles(self):
        style = ttk.Style()
        
        # Modern frame style
        style.configure('Reports.TFrame', 
                        background=MODERN_COLORS['background'])
        
        # Modern button style
        style.configure('Modern.TButton', 
                        background=MODERN_COLORS['primary'], 
                        foreground='white', 
                        font=('Helvetica', 10, 'bold'),
                        padding=(10, 5))
        
        # Hover effect
        style.map('Modern.TButton', 
                  background=[('active', MODERN_COLORS['secondary'])])
        
        # Modern notebook style
        style.configure('Modern.TNotebook', 
                        background=MODERN_COLORS['background'])
        style.configure('Modern.TNotebook.Tab', 
                        background=MODERN_COLORS['primary'], 
                        foreground='white', 
                        padding=(15, 10))
        style.map('Modern.TNotebook.Tab', 
                  background=[('selected', MODERN_COLORS['secondary'])])
    
    def create_header(self):
        # Modern header with gradient-like effect
        header_frame = ttk.Frame(self, style='Reports.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button with icon-like styling
        back_btn = ModernButton(
            header_frame, 
            text="← Back", 
            command=self.app.show_home_page
        )
        back_btn.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Title with modern typography
        title = ttk.Label(
            header_frame, 
            text="Reports & Analytics", 
            font=('Helvetica', 24, 'bold'),
            foreground=MODERN_COLORS['text'],
            background=MODERN_COLORS['background']
        )
        title.pack(pady=10)
    
    def create_report_sections(self):
        # Create notebook with modern styling
        notebook = ttk.Notebook(self, style='Modern.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Report sections with modern design
        report_sections = [
            ("Student Reports", self.create_student_reports_section),
            ("Financial Reports", self.create_financial_reports_section),
            ("Programme Reports", self.create_programme_reports_section),
            ("Advanced Analytics", self.create_advanced_analytics_section)
        ]
        
        for title, section_method in report_sections:
            frame = ttk.Frame(notebook, style='Reports.TFrame')
            section_method(frame)
            notebook.add(frame, text=title)
    
    def create_report_section(self, parent, reports):
        """
        Create a modern, grid-based report section
        
        :param parent: Parent widget
        :param reports: List of (button_text, command) tuples
        """
        frame = ttk.Frame(parent, style='Reports.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # Create buttons in a grid layout
        for i, (text, command) in enumerate(reports):
            row = i // 2
            col = i % 2
            
            btn = ModernButton(
                frame, 
                text=text, 
                command=command
            )
            btn.grid(
                row=row, 
                column=col, 
                padx=10, 
                pady=10, 
                sticky='ew'
            )
        
        return frame
    
    def create_student_reports_section(self, parent):
        reports = [
            ("Student Status Distribution", self.generate_student_status_report),
            ("Student Age Distribution", self.generate_age_distribution_report),
            ("Gender Distribution", self.generate_gender_distribution_report),
            ("Export Student List", self.export_full_student_list)
        ]
        return self.create_report_section(parent, reports)
    
    def create_financial_reports_section(self, parent):
        reports = [
            ("Monthly Revenue Analysis", self.generate_monthly_revenue_report),
            ("Outstanding Payments", self.generate_outstanding_payments_report),
            ("Payment Trends", self.generate_payment_trends_report),
            ("Export Comprehensive Report", self.export_comprehensive_report)
        ]
        return self.create_report_section(parent, reports)
    
    def create_programme_reports_section(self, parent):
        reports = [
            ("Programme Enrollment", self.generate_programme_enrollment_report),
            ("Programme Revenue", self.generate_programme_revenue_report),
            ("Programme Completion Rates", self.generate_programme_completion_report)
        ]
        return self.create_report_section(parent, reports)
    
    def create_advanced_analytics_section(self, parent):
        reports = [
            ("Performance Correlation", self.generate_performance_correlation_report),
            ("Student Retention Prediction", self.generate_retention_prediction_report),
            ("Student Cohort Analysis", self.generate_cohort_analysis_report)
        ]
        return self.create_report_section(parent, reports)
    
    def generate_student_status_report(self):
        """Generate pie chart of student statuses"""
        try:
            # Get statistics from database
            stats = self.app.db.get_student_statistics()
            
            # Prepare data
            labels = ['Active', 'Graduated', 'Dropped Out']
            sizes = [
                stats['active_students'], 
                stats['graduated_students'], 
                stats['dropouts']
            ]
            
            # Create pie chart
            plt.figure(figsize=(10, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.title('Student Status Distribution')
            
            # Save and show report
            self.save_and_show_plot('student_status_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_age_distribution_report(self):
        """Generate histogram of student ages"""
        try:
            # Fetch student ages from database
            ages = self.app.db.get_student_ages()
            
            plt.figure(figsize=(10, 6))
            plt.hist(ages, bins=20, edgecolor='black')
            plt.title('Student Age Distribution')
            plt.xlabel('Age')
            plt.ylabel('Number of Students')
            
            # Save and show report
            self.save_and_show_plot('age_distribution_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_gender_distribution_report(self):
        """Generate bar chart of gender distribution"""
        try:
            # Get gender statistics
            gender_stats = self.app.db.get_gender_distribution()
            
            plt.figure(figsize=(10, 6))
            plt.bar(gender_stats.keys(), gender_stats.values())
            plt.title('Gender Distribution')
            plt.xlabel('Gender')
            plt.ylabel('Number of Students')
            
            # Save and show report
            self.save_and_show_plot('gender_distribution_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def export_full_student_list(self):
        """Export complete student list to Excel"""
        try:
            # Get full student list from database
            students = self.app.db.export_students_to_excel()
            
            messagebox.showinfo(
                "Export Successful", 
                f"Student list exported to: {students}"
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export student list: {str(e)}")
    
    def generate_monthly_revenue_report(self):
        """Generate line chart of monthly revenue"""
        try:
            # Get monthly revenue data
            revenue_data = self.app.db.get_monthly_revenue()
            
            plt.figure(figsize=(12, 6))
            plt.plot(revenue_data.keys(), revenue_data.values(), marker='o')
            plt.title('Monthly Revenue Analysis')
            plt.xlabel('Month')
            plt.ylabel('Revenue (₦)')
            plt.xticks(rotation=45)
            
            # Save and show report
            self.save_and_show_plot('monthly_revenue_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_outstanding_payments_report(self):
        """Generate report of outstanding payments"""
        try:
            # Get outstanding payments
            outstanding = self.app.db.get_outstanding_payments()
            
            # Export to Excel
            df = pd.DataFrame(outstanding)
            filename = f"outstanding_payments_{datetime.now().strftime('%Y%m%d')}.xlsx"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            df.to_excel(filepath, index=False)
            
            messagebox.showinfo(
                "Report Generated", 
                f"Outstanding payments report saved to: {filepath}"
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_performance_correlation_report(self):
        """Generate correlation analysis between different student metrics"""
        try:
            # Fetch comprehensive student data
            students_df = pd.DataFrame(self.app.db.get_student_performance_data())
            
            # Create correlation heatmap
            plt.figure(figsize=(12, 10))
            
            if SEABORN_AVAILABLE:
                # Use seaborn if available
                sns.heatmap(
                    students_df.corr(), 
                    annot=True, 
                    cmap='coolwarm', 
                    linewidths=0.5
                )
            else:
                # Fallback to matplotlib
                plt.imshow(
                    students_df.corr(), 
                    cmap='coolwarm', 
                    aspect='auto'
                )
                plt.colorbar()
                plt.xticks(range(len(students_df.columns)), students_df.columns, rotation=45)
                plt.yticks(range(len(students_df.columns)), students_df.columns)
            
            plt.title('Student Performance Correlation Analysis')
            
            # Save and show report
            self.save_and_show_plot('performance_correlation_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate correlation report: {str(e)}")
    
    def generate_retention_prediction_report(self):
        """Generate predictive insights for student retention"""
        try:
            # Fetch retention data
            retention_data = self.app.db.get_student_retention_data()
            
            # Create stacked bar chart
            plt.figure(figsize=(12, 6))
            retention_df = pd.DataFrame(retention_data)
            
            retention_df.plot(
                kind='bar', 
                stacked=True, 
                x='programme', 
                y=['retained', 'dropped']
            )
            plt.title('Student Retention Prediction by Programme')
            plt.xlabel('Programme')
            plt.ylabel('Number of Students')
            plt.legend(title='Retention Status')
            
            # Save and show report
            self.save_and_show_plot('retention_prediction_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate retention report: {str(e)}")
    
    def generate_cohort_analysis_report(self):
        """Generate cohort analysis report"""
        try:
            # Fetch cohort data
            cohort_data = self.app.db.get_student_cohort_data()
            
            # Create line plot for cohort progression
            plt.figure(figsize=(12, 6))
            cohort_df = pd.DataFrame(cohort_data)
            
            for cohort, data in cohort_df.groupby('cohort'):
                plt.plot(data['period'], data['students'], label=cohort)
            
            plt.title('Student Cohort Progression')
            plt.xlabel('Time Period')
            plt.ylabel('Number of Students')
            plt.legend(title='Cohort')
            
            # Save and show report
            self.save_and_show_plot('cohort_analysis_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate cohort report: {str(e)}")
    
    def export_comprehensive_report(self):
        """Export a comprehensive report with multiple sections"""
        try:
            # Create Excel writer
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"comprehensive_report_{timestamp}.xlsx"
            filepath = os.path.join(self.app.app_path, "exports", filename)
            
            with pd.ExcelWriter(filepath) as writer:
                # Student Statistics
                student_stats = pd.DataFrame(self.app.db.get_student_statistics())
                student_stats.to_excel(writer, sheet_name='Student Statistics', index=False)
                
                # Financial Summary
                financial_summary = pd.DataFrame(self.app.db.get_financial_summary())
                financial_summary.to_excel(writer, sheet_name='Financial Summary', index=False)
                
                # Programme Performance
                programme_performance = pd.DataFrame(
                    self.app.db.generate_programme_completion_report()
                )
                programme_performance.to_excel(
                    writer, 
                    sheet_name='Programme Performance', 
                    index=False
                )
            
            messagebox.showinfo(
                "Export Successful", 
                f"Comprehensive report exported to: {filepath}"
            )
            
            # Open the file
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export comprehensive report: {str(e)}")
    
    def save_and_show_plot(self, report_name):
        """Save and optionally show matplotlib plot"""
        # Ensure exports directory exists
        exports_dir = os.path.join(self.app.app_path, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_name}_{timestamp}.png"
        filepath = os.path.join(exports_dir, filename)
        
        # Save plot
        plt.tight_layout()
        plt.savefig(filepath)
        
        # Ask if user wants to view
        if messagebox.askyesno("Report Generated", 
                              f"Report saved to {filepath}.\n\nDo you want to view the report?"):
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', filepath])
                elif platform.system() == 'Windows':
                    os.startfile(filepath)
                else:  # Linux
                    subprocess.run(['xdg-open', filepath])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
        
        # Close the plot to free memory
        plt.close()
    
    def generate_payment_trends_report(self):
        """Generate payment trends report"""
        try:
            # Get payment trends data from database
            trends_data = self.app.db.generate_payment_trends_report()
            
            # Create line plot for payment trends
            plt.figure(figsize=(12, 6))
            
            # Convert trends data to DataFrame for easier plotting
            trends_df = pd.DataFrame(trends_data)
            
            # Plot payment count and total amount
            plt.subplot(2, 1, 1)
            plt.plot(trends_df['month'], trends_df['payment_count'], marker='o')
            plt.title('Number of Payments per Month')
            plt.xlabel('Month')
            plt.ylabel('Payment Count')
            plt.xticks(rotation=45)
            
            plt.subplot(2, 1, 2)
            plt.plot(trends_df['month'], trends_df['total_amount'], marker='o', color='green')
            plt.title('Total Payment Amount per Month')
            plt.xlabel('Month')
            plt.ylabel('Total Amount (₦)')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Save and show report
            self.save_and_show_plot('payment_trends_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate payment trends report: {str(e)}")
    
    def generate_programme_enrollment_report(self):
        """Generate programme enrollment analysis report"""
        try:
            # Get programme enrollment data from database
            enrollment_data = self.app.db.generate_programme_enrollment_report()
            
            # Create bar chart for programme enrollment
            plt.figure(figsize=(12, 6))
            
            # Convert enrollment data to DataFrame
            enrollment_df = pd.DataFrame(enrollment_data)
            
            # Plot total students and graduated students
            plt.bar(
                enrollment_df['programme'], 
                enrollment_df['total_students'], 
                label='Total Students'
            )
            plt.bar(
                enrollment_df['programme'], 
                enrollment_df['graduated_students'], 
                label='Graduated Students'
            )
            
            plt.title('Programme Enrollment and Graduation Analysis')
            plt.xlabel('Programme')
            plt.ylabel('Number of Students')
            plt.xticks(rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            # Save and show report
            self.save_and_show_plot('programme_enrollment_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate programme enrollment report: {str(e)}")
    
    def generate_programme_revenue_report(self):
        """Generate programme revenue breakdown report"""
        try:
            # Get programme revenue data from database
            revenue_data = self.app.db.generate_programme_revenue_report()
            
            # Create bar chart for programme revenue
            plt.figure(figsize=(12, 6))
            
            # Convert revenue data to DataFrame
            revenue_df = pd.DataFrame(revenue_data)
            
            # Plot total revenue and total students
            plt.subplot(1, 2, 1)
            plt.bar(revenue_df['programme'], revenue_df['total_revenue'])
            plt.title('Total Revenue by Programme')
            plt.xlabel('Programme')
            plt.ylabel('Total Revenue (₦)')
            plt.xticks(rotation=45, ha='right')
            
            plt.subplot(1, 2, 2)
            plt.bar(revenue_df['programme'], revenue_df['total_students'], color='green')
            plt.title('Total Students by Programme')
            plt.xlabel('Programme')
            plt.ylabel('Number of Students')
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Save and show report
            self.save_and_show_plot('programme_revenue_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate programme revenue report: {str(e)}")
    
    def generate_programme_completion_report(self):
        """Generate programme completion rates report"""
        try:
            # Get programme completion data from database
            completion_data = self.app.db.generate_programme_completion_report()
            
            # Create bar chart for programme completion rates
            plt.figure(figsize=(12, 6))
            
            # Convert completion data to DataFrame
            completion_df = pd.DataFrame(completion_data)
            
            # Plot completion rates
            plt.bar(
                completion_df['programme'], 
                completion_df['completion_rate']
            )
            
            plt.title('Programme Completion Rates')
            plt.xlabel('Programme')
            plt.ylabel('Completion Rate (%)')
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on top of each bar
            for i, v in enumerate(completion_df['completion_rate']):
                plt.text(
                    i, v + 1, 
                    f'{v:.1f}%', 
                    ha='center', 
                    va='bottom'
                )
            
            plt.tight_layout()
            
            # Save and show report
            self.save_and_show_plot('programme_completion_report')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate programme completion report: {str(e)}")