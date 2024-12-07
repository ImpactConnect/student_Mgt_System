import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta

class NotificationSystem:
    def __init__(self, app):
        """
        Initialize Notification System
        
        Args:
            app: Main application instance
        """
        self.app = app
        self.db_path = app.db.db_path
        
        # Create notifications table if not exists
        self._create_notifications_table()
    
    def _create_notifications_table(self):
        """Create notifications table in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_number TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY (reg_number) REFERENCES students(reg_number)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def send_payment_reminder(self, reg_number):
        """
        Send payment reminder notification
        
        Args:
            reg_number (str): Student registration number
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get student details and payment info
            cursor.execute('''
                SELECT 
                    s.name, 
                    s.programme, 
                    s.programme_fee,
                    COALESCE(SUM(p.amount), 0) as total_paid
                FROM students s
                LEFT JOIN payments p ON s.reg_number = p.reg_number
                WHERE s.reg_number = ?
                GROUP BY s.reg_number
            ''', (reg_number,))
            
            student = cursor.fetchone()
            
            if student:
                name, programme, total_fee, paid_amount = student
                balance = total_fee - paid_amount
                
                # Create notification message
                message = (f"Payment Reminder for {name}\n"
                          f"Programme: {programme}\n"
                          f"Total Fee: ₦{total_fee:,.2f}\n"
                          f"Paid Amount: ₦{paid_amount:,.2f}\n"
                          f"Remaining Balance: ₦{balance:,.2f}")
                
                # Insert notification
                cursor.execute('''
                    INSERT INTO notifications 
                    (reg_number, message, type) 
                    VALUES (?, ?, ?)
                ''', (reg_number, message, 'payment_reminder'))
                
                conn.commit()
                return True
            
            return False
        
        except sqlite3.Error as e:
            print(f"Error sending payment reminder: {e}")
            return False
        
        finally:
            conn.close()
    
    def send_course_progress_notification(self, reg_number):
        """
        Send course progress notification
        
        Args:
            reg_number (str): Student registration number
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get student details and course progress
            cursor.execute('''
                SELECT 
                    name, 
                    programme, 
                    start_date,
                    duration
                FROM students
                WHERE reg_number = ?
            ''', (reg_number,))
            
            student = cursor.fetchone()
            
            if student:
                name, programme, start_date, duration = student
                
                # Calculate progress
                start = datetime.strptime(start_date, '%Y-%m-%d')
                months = int(duration.split()[0])
                end_date = start + timedelta(days=months*30)
                total_days = (end_date - start).days
                current_days = (datetime.now() - start).days
                progress_percentage = min(max(0, current_days / total_days * 100), 100)
                
                # Create progress message
                message = (f"Course Progress Update for {name}\n"
                          f"Programme: {programme}\n"
                          f"Duration: {duration}\n"
                          f"Progress: {progress_percentage:.1f}%")
                
                # Insert notification
                cursor.execute('''
                    INSERT INTO notifications 
                    (reg_number, message, type) 
                    VALUES (?, ?, ?)
                ''', (reg_number, message, 'course_progress'))
                
                conn.commit()
                return True
            
            return False
        
        except sqlite3.Error as e:
            print(f"Error sending course progress notification: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_student_notifications(self, reg_number):
        """
        Retrieve notifications for a specific student
        
        Args:
            reg_number (str): Student registration number
        
        Returns:
            list: List of notification dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    id, 
                    message, 
                    type, 
                    created_at, 
                    is_read
                FROM notifications
                WHERE reg_number = ?
                ORDER BY created_at DESC
            ''', (reg_number,))
            
            notifications = [
                {
                    'id': row[0],
                    'message': row[1],
                    'type': row[2],
                    'created_at': row[3],
                    'is_read': bool(row[4])
                } for row in cursor.fetchall()
            ]
            
            return notifications
        
        except sqlite3.Error as e:
            print(f"Error retrieving notifications: {e}")
            return []
        
        finally:
            conn.close()
    
    def mark_notification_as_read(self, notification_id):
        """
        Mark a specific notification as read
        
        Args:
            notification_id (int): ID of the notification
        
        Returns:
            bool: True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE id = ?
            ''', (notification_id,))
            
            conn.commit()
            return True
        
        except sqlite3.Error as e:
            print(f"Error marking notification as read: {e}")
            return False
        
        finally:
            conn.close()
    
    def send_bulk_notification(self, programme=None, message=None):
        """
        Send bulk notifications to students
        
        Args:
            programme (str, optional): Target programme
            message (str, optional): Notification message
        
        Returns:
            int: Number of notifications sent
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Base query to select students
            query = "SELECT reg_number FROM students"
            params = []
            
            # Add programme filter if specified
            if programme:
                query += " WHERE programme = ?"
                params.append(programme)
            
            cursor.execute(query, params)
            students = cursor.fetchall()
            
            # Send notifications
            notifications_sent = 0
            for (reg_number,) in students:
                cursor.execute('''
                    INSERT INTO notifications 
                    (reg_number, message, type) 
                    VALUES (?, ?, ?)
                ''', (reg_number, message, 'bulk_announcement'))
                notifications_sent += 1
            
            conn.commit()
            return notifications_sent
        
        except sqlite3.Error as e:
            print(f"Error sending bulk notifications: {e}")
            return 0
        
        finally:
            conn.close() 