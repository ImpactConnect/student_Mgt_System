import os
from pathlib import Path

def create_app_folders():
    # Get documents folder path
    documents_path = os.path.expanduser("~/Documents")
    impactech_path = os.path.join(documents_path, "Impactech")
    
    # Create main folder
    if not os.path.exists(impactech_path):
        os.makedirs(impactech_path)
        
    # Create subfolders for receipts and exports
    receipts_path = os.path.join(impactech_path, "receipts")
    exports_path = os.path.join(impactech_path, "exports")
    
    # Create directories if they don't exist
    os.makedirs(receipts_path, exist_ok=True)
    os.makedirs(exports_path, exist_ok=True)
    
    print(f"Created/verified directories:")
    print(f"Main path: {impactech_path}")
    print(f"Receipts path: {receipts_path}")
    print(f"Exports path: {exports_path}")
        
    return impactech_path

def reset_database():
    documents_path = os.path.expanduser("~/Documents")
    impactech_path = os.path.join(documents_path, "Impactech")
    db_path = os.path.join(impactech_path, "impactech.db")
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Database reset successfully")
        except Exception as e:
            print(f"Error resetting database: {e}") 