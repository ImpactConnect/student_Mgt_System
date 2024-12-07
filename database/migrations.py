import sqlite3
from datetime import datetime

def migrate_database(db_path):
    """Safely migrate database to new schema while preserving data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Create temporary table with new schema
        cursor.execute('''
            CREATE TABLE students_new (
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
        
        # 2. Copy existing data to new table
        cursor.execute('''
            INSERT INTO students_new (
                reg_number, name, age, gender, programme,
                start_date, duration, schedule, programme_fee,
                registration_date
            )
            SELECT 
                reg_number, name, age, gender, programme,
                start_date, duration, schedule, programme_fee,
                registration_date
            FROM students
        ''')
        
        # 3. Drop old table
        cursor.execute('DROP TABLE students')
        
        # 4. Rename new table to original name
        cursor.execute('ALTER TABLE students_new RENAME TO students')
        
        # 5. Add indexes if needed
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_status ON students(status)')
        
        # Commit transaction
        conn.commit()
        print("Migration completed successfully")
        return True
        
    except sqlite3.Error as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Migration failed: {e}")
        return False
        
    finally:
        conn.close() 