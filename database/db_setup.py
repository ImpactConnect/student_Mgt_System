from datetime import datetime, timedelta
import sqlite3
import os
from utils.constants import SCHEDULES
from utils.receipt_generator import ReceiptGenerator

class Database:
    def __init__(self, db_path):
        # Store base path and ensure it's the parent directory
        self.base_path = os.path.dirname(db_path) if os.path.isfile(db_path) else db_path
        self.db_path = os.path.join(self.base_path, "impactech.db")
        self.receipts_path = os.path.join(self.base_path, "receipts")
        self.receipt_generator = ReceiptGenerator(self.base_path)
        
        # Create tables if they don't exist
        self.create_tables()
        
        # Check if migration is needed
        if not self.check_status_column():
            from database.migrations import migrate_database
            migrate_database(self.db_path)
    
    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create Students table with additional fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    reg_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    programme TEXT,
                    start_date DATE,
                    duration TEXT,
                    schedule TEXT,
                    programme_fee REAL,
                    registration_date TIMESTAMP,
                    status TEXT DEFAULT 'Active',
                    scholarship INTEGER DEFAULT 0
                )
            ''')
            
            # Create Payments table with payment_note column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reg_number TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    receipt_number TEXT UNIQUE,
                    payment_note TEXT,
                    FOREIGN KEY (reg_number) REFERENCES students(reg_number)
                )
            ''')
            
            # Enable foreign key support
            cursor.execute('PRAGMA foreign_keys = ON')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def generate_serial_number(self, programme, year):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prepare the programme code
        prog_code = ''.join(word[0] for word in programme.split()[:3]).upper()
        
        # Get the last registration number for this programme and year
        cursor.execute('''
            SELECT reg_number FROM students 
            WHERE reg_number LIKE ? 
            ORDER BY reg_number DESC LIMIT 1
        ''', [f'IMPTECH-{prog_code}-{year}%'])
        
        result = cursor.fetchone()
        
        if result:
            # Extract the serial number from the last registration number
            last_serial = int(result[0].split('-')[-1])
            new_serial = str(last_serial + 1).zfill(3)
        else:
            new_serial = '001'
        
        conn.close()
        return new_serial
    
    def save_student(self, student_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        receipt_path = None
        
        try:
            # Check if registration number already exists
            cursor.execute('SELECT COUNT(*) FROM students WHERE reg_number = ?', (student_data['reg_number'],))
            if cursor.fetchone()[0] > 0:
                return False, None, "Registration number already exists. Please regenerate."
            
            # Insert student record with current timestamp and Active status
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO students (
                    reg_number, name, age, gender, programme, 
                    start_date, duration, schedule, programme_fee,
                    registration_date, status, scholarship
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', 0)
            ''', (
                student_data['reg_number'],
                student_data['name'],
                student_data['age'],
                student_data['gender'],
                student_data['programme'],
                student_data['start_date'],
                student_data['duration'],
                student_data['schedule'],
                student_data['programme_fee'],
                current_time
            ))
            
            # Insert initial payment record and generate receipt
            if student_data['initial_payment'] > 0:
                receipt_number = self.generate_receipt_number()
                cursor.execute('''
                    INSERT INTO payments (
                        reg_number, amount, receipt_number
                    ) VALUES (?, ?, ?)
                ''', (
                    student_data['reg_number'],
                    student_data['initial_payment'],
                    receipt_number
                ))
                
                # Generate receipt PDF
                payment_data = {
                    'receipt_number': receipt_number,
                    'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': student_data['initial_payment']
                }
                
                receipt_path = self.receipt_generator.generate_receipt(payment_data, student_data)
            
            conn.commit()
            return True, receipt_path, None
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return False, None, "Duplicate registration number or database constraint violation"
        except sqlite3.Error as e:
            conn.rollback()
            return False, None, str(e)
            
        finally:
            conn.close()
    
    def generate_receipt_number(self):
        # Generate receipt number format: RCP-YYYYMMDD-XXXX
        now = datetime.now()
        date_part = now.strftime('%Y%m%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the last receipt number for today
        cursor.execute('''
            SELECT receipt_number FROM payments 
            WHERE receipt_number LIKE ? 
            ORDER BY receipt_number DESC LIMIT 1
        ''', [f'RCP-{date_part}%'])
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            last_number = int(result[0].split('-')[-1])
            serial = str(last_number + 1).zfill(4)
        else:
            serial = '0001'
            
        return f'RCP-{date_part}-{serial}'
    
    def get_student(self, reg_number):
        """Get student details by registration number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT reg_number, name, age, gender, programme, 
                   start_date, duration, schedule, programme_fee,
                   registration_date
            FROM students 
            WHERE reg_number = ?
        ''', [reg_number])
        
        student = cursor.fetchone()
        conn.close()
        
        if student:
            return {
                'reg_number': student[0],
                'name': student[1],
                'age': student[2] or '',
                'gender': student[3] or '',
                'programme': student[4] or '',
                'start_date': student[5] or '',
                'duration': student[6] or '',
                'schedule': student[7] or '',
                'programme_fee': student[8] or 0,
                'registration_date': student[9] or ''
            }
        return None
    
    def get_student_payments(self, reg_number):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT amount, payment_date, receipt_number 
            FROM payments 
            WHERE reg_number = ?
            ORDER BY payment_date DESC
        ''', [reg_number])
        
        payments = cursor.fetchall()
        conn.close()
        
        return [{
            'amount': payment[0],
            'payment_date': payment[1],
            'receipt_number': payment[2]
        } for payment in payments]
    
    def get_student_receipts(self, reg_number):
        """Get all receipt paths for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT receipt_number, payment_date, amount 
            FROM payments 
            WHERE reg_number = ?
            ORDER BY payment_date DESC
        ''', [reg_number])
        
        receipts = cursor.fetchall()
        conn.close()
        
        receipt_list = []
        for receipt in receipts:
            receipt_number = receipt[0]
            filename = f"receipt_{receipt_number}.pdf"
            filepath = os.path.join(self.receipts_path, filename)
            
            if os.path.exists(filepath):
                receipt_list.append({
                    'receipt_number': receipt_number,
                    'payment_date': receipt[1],
                    'amount': receipt[2],
                    'filepath': filepath
                })
        
        return receipt_list
    
    def save_payment(self, reg_number, amount, payment_note=''):
        """Save a new payment with comment and generate receipt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        receipt_path = None
        
        try:
            # Get student data first
            cursor.execute('''
                SELECT name, programme, reg_number, programme_fee,
                       (SELECT COALESCE(SUM(amount), 0) 
                        FROM payments 
                        WHERE reg_number = s.reg_number) as total_paid
                FROM students s
                WHERE reg_number = ?
            ''', [reg_number])
            
            student = cursor.fetchone()
            if not student:
                raise ValueError("Student not found")
            
            # Extract student info and current total paid
            name, programme, reg_num, programme_fee, previous_payments = student
            
            # Calculate new total and balance
            new_total_paid = previous_payments + amount
            balance = programme_fee - new_total_paid
            
            # Generate receipt number and save payment with note
            receipt_number = self.generate_receipt_number()
            payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO payments (
                    reg_number, amount, receipt_number, 
                    payment_date, payment_note
                ) VALUES (?, ?, ?, ?, ?)
            ''', (reg_number, amount, receipt_number, payment_date, payment_note))
            
            # Prepare data for receipt generation
            student_data = {
                'reg_number': str(reg_num),
                'name': str(name),
                'programme': str(programme),
                'programme_fee': float(programme_fee)
            }
            
            payment_data = {
                'receipt_number': str(receipt_number),
                'payment_date': str(payment_date),
                'amount': float(amount),
                'total_paid': float(new_total_paid),
                'balance': float(balance),
                'payment_note': payment_note
            }
            
            # Generate receipt
            receipt_path = self.receipt_generator.generate_receipt(payment_data, student_data)
            
            conn.commit()
            return True, receipt_path, None
            
        except (sqlite3.Error, ValueError) as e:
            conn.rollback()
            return False, None, str(e)
            
        finally:
            conn.close()
    
    def get_total_payments(self, reg_number):
        """Get total amount paid by a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM payments 
            WHERE reg_number = ?
        ''', [reg_number])
        
        total = cursor.fetchone()[0]
        conn.close()
        
        return total
    
    def get_payment_history(self, reg_number):
        """Get detailed payment history for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT amount, payment_date, receipt_number,
                   (SELECT programme_fee FROM students WHERE reg_number = p.reg_number) as total_fee,
                   (SELECT SUM(amount) FROM payments WHERE reg_number = p.reg_number AND payment_date <= p.payment_date) as running_total
            FROM payments p
            WHERE reg_number = ?
            ORDER BY payment_date DESC
        ''', [reg_number])
        
        payments = cursor.fetchall()
        conn.close()
        
        return [{
            'amount': payment[0],
            'payment_date': payment[1],
            'receipt_number': payment[2],
            'total_fee': payment[3],
            'balance': payment[3] - payment[4]  # total_fee - running_total
        } for payment in payments]
    
    def get_all_students(self):
        """Get all students from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT reg_number, name, programme, start_date, 
                   programme_fee, duration, schedule
            FROM students
            ORDER BY registration_date DESC
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        return [{
            'reg_number': student[0],
            'name': student[1],
            'programme': student[2],
            'start_date': student[3],
            'programme_fee': student[4],
            'duration': student[5],
            'schedule': student[6]
        } for student in students]
    
    def export_students_to_excel(self):
        """Export student records to Excel"""
        try:
            import pandas as pd
            
            # Get all students with payment info
            students = []
            for student in self.get_all_students():
                total_paid = self.get_total_payments(student['reg_number'])
                students.append({
                    'Registration Number': student['reg_number'],
                    'Name': student['name'],
                    'Programme': student['programme'],
                    'Schedule': student['schedule'],
                    'Duration': student['duration'],
                    'Start Date': student['start_date'],
                    'Programme Fee': student['programme_fee'],
                    'Total Paid': total_paid,
                    'Balance': student['programme_fee'] - total_paid
                })
            
            # Create DataFrame
            df = pd.DataFrame(students)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"student_records_{timestamp}.xlsx"
            filepath = os.path.join(os.path.dirname(self.db_path), 
                                  "exports", filename)
            
            # Export to Excel
            df.to_excel(filepath, index=False, sheet_name='Students')
            
            return filepath
            
        except ImportError:
            raise Exception("Please install pandas: pip install pandas")
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def get_schedule_statistics(self):
        """Get detailed statistics for each schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = []
        for schedule in SCHEDULES:
            cursor.execute('''
                WITH StudentPayments AS (
                    SELECT s.reg_number,
                           s.programme_fee,
                           COALESCE(SUM(p.amount), 0) as paid_amount
                    FROM students s
                    LEFT JOIN payments p ON s.reg_number = p.reg_number
                    WHERE s.schedule = ?
                    GROUP BY s.reg_number
                )
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN paid_amount >= programme_fee THEN 1 ELSE 0 END) as fully_paid,
                    SUM(CASE WHEN paid_amount > 0 AND paid_amount < programme_fee THEN 1 ELSE 0 END) as partial,
                    SUM(CASE WHEN paid_amount = 0 THEN 1 ELSE 0 END) as unpaid,
                    COALESCE(SUM(paid_amount), 0) as revenue
                FROM StudentPayments
            ''', [schedule])
            
            result = cursor.fetchone()
            stats.append({
                'schedule': schedule,
                'total_students': result[0],
                'fully_paid': result[1],
                'partial_paid': result[2],
                'unpaid': result[3],
                'total_revenue': result[4]
            })
        
        conn.close()
        return stats
    
    def get_schedule_payment_analysis(self):
        """Get payment analysis for each schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        analysis = []
        for schedule in SCHEDULES:
            cursor.execute('''
                SELECT 
                    SUM(s.programme_fee) as expected,
                    COALESCE(SUM(p.amount), 0) as received
                FROM students s
                LEFT JOIN payments p ON s.reg_number = p.reg_number
                WHERE s.schedule = ?
            ''', [schedule])
            
            result = cursor.fetchone()
            expected = result[0] or 0
            received = result[1] or 0
            
            analysis.append({
                'schedule': schedule,
                'expected_revenue': expected,
                'received_revenue': received,
                'outstanding': expected - received,
                'collection_rate': (received / expected * 100) if expected > 0 else 0
            })
        
        conn.close()
        return analysis
    
    def get_schedule_trends(self):
        """Get month-over-month trends for each schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_month = datetime.now().strftime('%Y-%m')
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        trends = []
        for schedule in SCHEDULES:
            cursor.execute('''
                SELECT 
                    COUNT(CASE WHEN strftime('%Y-%m', registration_date) = ? THEN 1 END) as this_month,
                    COUNT(CASE WHEN strftime('%Y-%m', registration_date) = ? THEN 1 END) as last_month
                FROM students
                WHERE schedule = ?
            ''', [current_month, last_month, schedule])
            
            result = cursor.fetchone()
            this_month = result[0]
            last_month = result[1]
            
            growth = ((this_month - last_month) / last_month * 100 
                     if last_month > 0 else 0)
            
            trends.append({
                'schedule': schedule,
                'this_month': this_month,
                'last_month': last_month,
                'growth': growth
            })
        
        conn.close()
        return trends
    
    def check_and_fix_database(self):
        """Check database structure and fix if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update schema if needed
            cursor.execute('''
                UPDATE students 
                SET status = 'Active' 
                WHERE status IS NULL
            ''')
            
            cursor.execute('''
                UPDATE students 
                SET scholarship = 0 
                WHERE scholarship IS NULL
            ''')
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error fixing database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def verify_database_structure(self):
        """Verify that the database has the correct structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check students table structure
            cursor.execute("PRAGMA table_info(students)")
            students_columns = {column[1] for column in cursor.fetchall()}
            
            # Check payments table structure
            cursor.execute("PRAGMA table_info(payments)")
            payments_columns = {column[1] for column in cursor.fetchall()}
            
            # Verify required columns exist
            required_students_columns = {
                'reg_number', 'name', 'age', 'gender', 'programme',
                'start_date', 'duration', 'schedule', 'programme_fee',
                'registration_date'
            }
            
            required_payments_columns = {
                'payment_id', 'reg_number', 'amount', 'payment_date',
                'receipt_number'
            }
            
            if not required_students_columns.issubset(students_columns):
                print("Students table missing columns")
                return False
            
            if not required_payments_columns.issubset(payments_columns):
                print("Payments table missing columns")
                return False
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error verifying database structure: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_payments(self):
        """Get all payments with student names and programmes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.payment_date, s.name, p.amount, p.receipt_number, s.programme
            FROM payments p
            JOIN students s ON p.reg_number = s.reg_number
            ORDER BY p.payment_date DESC
        ''')
        
        payments = cursor.fetchall()
        conn.close()
        
        return [{
            'payment_date': payment[0],
            'student_name': payment[1],
            'amount': payment[2],
            'receipt_number': payment[3],
            'programme': payment[4]
        } for payment in payments]
    
    def get_receipt_by_number(self, receipt_number):
        """Get receipt details by receipt number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT p.payment_date, p.amount, s.reg_number, s.name
                FROM payments p
                JOIN students s ON p.reg_number = s.reg_number
                WHERE p.receipt_number = ?
            ''', [receipt_number])
            
            result = cursor.fetchone()
            
            if result:
                # Build the full filepath
                filename = f"receipt_{receipt_number}.pdf"
                filepath = os.path.join(self.receipts_path, filename)
                
                print(f"Looking for receipt at: {filepath}")  # Debug print
                
                return {
                    'payment_date': result[0],
                    'amount': result[1],
                    'reg_number': result[2],
                    'student_name': result[3],
                    'receipt_number': receipt_number,
                    'filepath': filepath
                }
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
        
        return None
    
    def update_student(self, reg_number, updates):
        """Update student details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            update_fields = []
            values = []
            for key, value in updates.items():
                update_fields.append(f"{key} = ?")
                values.append(value)
            
            # Add reg_number to values
            values.append(reg_number)
            
            # Execute update
            cursor.execute(f'''
                UPDATE students 
                SET {", ".join(update_fields)}
                WHERE reg_number = ?
            ''', values)
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            conn.close()
    
    def get_payment_statistics(self):
        """Get overall payment statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get total programme fees and student count
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_students,
                    SUM(programme_fee) as total_fees
                FROM students
            ''')
            result = cursor.fetchone()
            total_students = result[0] or 0
            total_fees = result[1] or 0
            
            # Get total revenue and payment stats
            cursor.execute('''
                WITH StudentPayments AS (
                    SELECT 
                        s.reg_number,
                        s.programme_fee,
                        COALESCE(SUM(p.amount), 0) as paid_amount
                    FROM students s
                    LEFT JOIN payments p ON s.reg_number = p.reg_number
                    GROUP BY s.reg_number, s.programme_fee
                )
                SELECT 
                    COUNT(*) as total_students,
                    SUM(CASE WHEN paid_amount >= programme_fee THEN 1 ELSE 0 END) as fully_paid,
                    SUM(paid_amount) as total_revenue
                FROM StudentPayments
            ''')
            
            result = cursor.fetchone()
            fully_paid_students = result[1] or 0
            total_revenue = result[2] or 0
            
            # Calculate derived statistics
            total_outstanding = total_fees - total_revenue
            collection_rate = (total_revenue / total_fees * 100) if total_fees > 0 else 0
            
            return {
                'total_fees': total_fees,
                'total_revenue': total_revenue,
                'total_outstanding': total_outstanding,
                'total_students': total_students,
                'fully_paid_students': fully_paid_students,
                'collection_rate': collection_rate
            }
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {
                'total_fees': 0,
                'total_revenue': 0,
                'total_outstanding': 0,
                'total_students': 0,
                'fully_paid_students': 0,
                'collection_rate': 0
            }
        finally:
            conn.close()
    
    def export_payments_to_excel(self, programme=None, search_term=None, from_date=None, to_date=None):
        """Export filtered payments to Excel"""
        try:
            import pandas as pd
            
            # Get all payments with additional info
            payments = []
            for payment in self.get_all_payments():
                # Apply filters
                if programme and payment['programme'] != programme:
                    continue
                    
                if search_term and search_term.lower() not in payment['student_name'].lower() and \
                   search_term.lower() not in payment['programme'].lower():
                    continue
                    
                payment_date = datetime.strptime(payment['payment_date'], '%Y-%m-%d %H:%M:%S')
                if from_date and payment_date.date() < datetime.strptime(from_date, '%Y-%m-%d').date():
                    continue
                if to_date and payment_date.date() > datetime.strptime(to_date, '%Y-%m-%d').date():
                    continue
                
                payments.append({
                    'Payment Date': payment_date.strftime('%Y-%m-%d %H:%M'),
                    'Student Name': payment['student_name'],
                    'Programme': payment['programme'],
                    'Amount': payment['amount'],
                    'Receipt Number': payment['receipt_number']
                })
            
            # Create DataFrame
            df = pd.DataFrame(payments)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"payment_history_{timestamp}.xlsx"
            filepath = os.path.join(self.base_path, "exports", filename)
            
            # Ensure exports directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Export to Excel
            df.to_excel(filepath, index=False, sheet_name='Payments')
            
            return filepath
            
        except ImportError:
            raise Exception("Please install pandas: pip install pandas")
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def get_outstanding_payments(self):
        """Get list of students with outstanding payments"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                WITH StudentPayments AS (
                    SELECT 
                        s.reg_number,
                        s.name,
                        s.programme,
                        s.programme_fee,
                        COALESCE(SUM(p.amount), 0) as amount_paid
                    FROM students s
                    LEFT JOIN payments p ON s.reg_number = p.reg_number
                    GROUP BY s.reg_number, s.name, s.programme, s.programme_fee
                    HAVING amount_paid < programme_fee
                )
                SELECT 
                    name,
                    programme,
                    programme_fee,
                    amount_paid,
                    (programme_fee - amount_paid) as balance
                FROM StudentPayments
                ORDER BY balance DESC
            ''')
            
            results = cursor.fetchall()
            return [{
                'name': result[0],
                'programme': result[1],
                'programme_fee': result[2],
                'amount_paid': result[3],
                'balance': result[4]
            } for result in results]
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def get_student_statistics(self):
        """Get student statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all statistics in a single query
            cursor.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM students) as total_students,
                    (SELECT COUNT(*) FROM students WHERE status = 'Active' OR status IS NULL) as active_students,
                    (SELECT COUNT(*) FROM students WHERE status = 'Graduated') as graduated_students,
                    (SELECT COUNT(*) FROM students WHERE status = 'Dropped Out') as dropouts,
                    (SELECT COUNT(*) FROM students WHERE scholarship = 1) as scholarships
                FROM students LIMIT 1
            ''')
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_students': result[0],
                    'active_students': result[1],
                    'graduated_students': result[2],
                    'dropouts': result[3],
                    'scholarships': result[4]
                }
            else:
                return {
                    'total_students': 0,
                    'active_students': 0,
                    'graduated_students': 0,
                    'dropouts': 0,
                    'scholarships': 0
                }
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {
                'total_students': 0,
                'active_students': 0,
                'graduated_students': 0,
                'dropouts': 0,
                'scholarships': 0
            }
        finally:
            conn.close()
    
    def check_status_column(self):
        """Check if status column exists in students table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(students)")
            columns = {column[1] for column in cursor.fetchall()}
            return 'status' in columns
            
        except sqlite3.Error as e:
            print(f"Error checking status column: {e}")
            return False
            
        finally:
            conn.close()
    
    def update_student_status(self, reg_number, status):
        """Update student status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE students 
                SET status = ? 
                WHERE reg_number = ?
            ''', (status, reg_number))
            
            conn.commit()
            return True
        
        except sqlite3.Error as e:
            print(f"Error updating student status: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_student_ages(self):
        """Fetch all student ages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT age FROM students WHERE age IS NOT NULL')
            ages = [row[0] for row in cursor.fetchall()]
            return ages
        except sqlite3.Error as e:
            print(f"Error fetching student ages: {e}")
            return []
        finally:
            conn.close()
    
    def get_gender_distribution(self):
        """Get count of students by gender"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT gender, COUNT(*) FROM students GROUP BY gender')
            return dict(cursor.fetchall())
        except sqlite3.Error as e:
            print(f"Error fetching gender distribution: {e}")
            return {}
        finally:
            conn.close()
    
    def get_monthly_revenue(self):
        """Calculate monthly revenue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', payment_date) as month, 
                    SUM(amount) as total_revenue
                FROM payments
                GROUP BY month
                ORDER BY month
            ''')
            return dict(cursor.fetchall())
        except sqlite3.Error as e:
            print(f"Error fetching monthly revenue: {e}")
            return {}
        finally:
            conn.close()
    
    def generate_payment_trends_report(self):
        """Generate payment trends report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', payment_date) as month, 
                    COUNT(*) as payment_count,
                    SUM(amount) as total_amount
                FROM payments
                GROUP BY month
                ORDER BY month
            ''')
            return [
                {
                    'month': row[0],
                    'payment_count': row[1],
                    'total_amount': row[2]
                } for row in cursor.fetchall()
            ]
        except sqlite3.Error as e:
            print(f"Error generating payment trends: {e}")
            return []
        finally:
            conn.close()
    
    def generate_programme_enrollment_report(self):
        """Generate programme enrollment report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    programme, 
                    COUNT(*) as total_students,
                    COUNT(CASE WHEN status = 'Graduated' THEN 1 END) as graduated_students
                FROM students
                GROUP BY programme
            ''')
            return [
                {
                    'programme': row[0],
                    'total_students': row[1],
                    'graduated_students': row[2]
                } for row in cursor.fetchall()
            ]
        except sqlite3.Error as e:
            print(f"Error generating programme enrollment report: {e}")
            return []
        finally:
            conn.close()
    
    def generate_programme_revenue_report(self):
        """Generate programme revenue breakdown"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    s.programme, 
                    SUM(p.amount) as total_revenue,
                    COUNT(DISTINCT s.reg_number) as total_students
                FROM students s
                LEFT JOIN payments p ON s.reg_number = p.reg_number
                GROUP BY s.programme
            ''')
            return [
                {
                    'programme': row[0],
                    'total_revenue': row[1],
                    'total_students': row[2]
                } for row in cursor.fetchall()
            ]
        except sqlite3.Error as e:
            print(f"Error generating programme revenue report: {e}")
            return []
        finally:
            conn.close()
    
    def generate_programme_completion_report(self):
        """Generate programme completion rates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    programme, 
                    COUNT(*) as total_students,
                    COUNT(CASE WHEN status = 'Graduated' THEN 1 END) as graduated_students,
                    ROUND(COUNT(CASE WHEN status = 'Graduated' THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate
                FROM students
                GROUP BY programme
            ''')
            return [
                {
                    'programme': row[0],
                    'total_students': row[1],
                    'graduated_students': row[2],
                    'completion_rate': row[3]
                } for row in cursor.fetchall()
            ]
        except sqlite3.Error as e:
            print(f"Error generating programme completion report: {e}")
            return []
        finally:
            conn.close()
    
    def get_student_performance_data(self):
        """Fetch comprehensive student performance data for correlation analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    age,
                    programme_fee,
                    (SELECT SUM(amount) FROM payments p WHERE p.reg_number = s.reg_number) as total_paid,
                    CASE WHEN status = 'Graduated' THEN 1 ELSE 0 END as graduated
                FROM students s
            ''')
            columns = ['age', 'programme_fee', 'total_paid', 'graduated']
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except sqlite3.Error as e:
            print(f"Error fetching performance data: {e}")
            return []
        finally:
            conn.close()
    
    def get_student_retention_data(self):
        """Fetch student retention data by programme"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    programme,
                    COUNT(CASE WHEN status != 'Dropped Out' THEN 1 END) as retained,
                    COUNT(CASE WHEN status = 'Dropped Out' THEN 1 END) as dropped
                FROM students
                GROUP BY programme
            ''')
            return [
                {
                    'programme': row[0],
                    'retained': row[1],
                    'dropped': row[2]
                } for row in cursor.fetchall()
            ]
        
        except sqlite3.Error as e:
            print(f"Error fetching retention data: {e}")
            return []
        finally:
            conn.close()
    
    def get_student_cohort_data(self):
        """Fetch student cohort progression data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    strftime('%Y', registration_date) as cohort,
                    strftime('%Y-%m', registration_date) as period,
                    COUNT(*) as students
                FROM students
                GROUP BY cohort, period
                ORDER BY period
            ''')
            return [
                {
                    'cohort': row[0],
                    'period': row[1],
                    'students': row[2]
                } for row in cursor.fetchall()
            ]
        
        except sqlite3.Error as e:
            print(f"Error fetching cohort data: {e}")
            return []
        finally:
            conn.close()
    
    def get_financial_summary(self):
        """Generate comprehensive financial summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    'Total Revenue' as metric,
                    SUM(amount) as value
                FROM payments
                UNION ALL
                SELECT 
                    'Total Programme Fees',
                    SUM(programme_fee)
                FROM students
                UNION ALL
                SELECT 
                    'Total Outstanding',
                    SUM(programme_fee) - (SELECT SUM(amount) FROM payments p WHERE p.reg_number = s.reg_number)
                FROM students s
            ''')
            return [
                {
                    'metric': row[0],
                    'value': row[1]
                } for row in cursor.fetchall()
            ]
        
        except sqlite3.Error as e:
            print(f"Error fetching financial summary: {e}")
            return []
        finally:
            conn.close()
    
    def delete_student(self, reg_number):
        """
        Delete a student record and all associated payment records
        
        Args:
            reg_number (str): Registration number of the student to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Enable foreign key support
            cursor.execute('PRAGMA foreign_keys = ON')
            
            # Start a transaction
            conn.execute('BEGIN TRANSACTION')
            
            # First, delete all payment records for this student
            cursor.execute('DELETE FROM payments WHERE reg_number = ?', (reg_number,))
            
            # Then delete the student record
            cursor.execute('DELETE FROM students WHERE reg_number = ?', (reg_number,))
            
            # Commit the transaction
            conn.commit()
            
            return True
        
        except sqlite3.Error as e:
            # Rollback in case of error
            conn.rollback()
            print(f"Error deleting student: {e}")
            return False
        
        finally:
            conn.close()
    
    def delete_payment_record(self, payment_id):
        """
        Delete a specific payment record
        
        Args:
            payment_id (int): ID of the payment record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete the specific payment record
            cursor.execute('DELETE FROM payments WHERE payment_id = ?', (payment_id,))
            
            conn.commit()
            return True
        
        except sqlite3.Error as e:
            # Rollback in case of error
            conn.rollback()
            print(f"Error deleting payment record: {e}")
            return False
        
        finally:
            conn.close()