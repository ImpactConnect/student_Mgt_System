# IMPACTTECH CODING ACADEMY - Student Management System

## Prerequisites
- Windows 10 or later
- Python 3.8+ installed
- pip package manager

## Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/studentsmgt.git
cd studentsmgt
```

2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Run Directly
```bash
python main.py
```

### Option 2: Build Standalone Executable
```bash
pyinstaller --onefile --windowed --add-data "database;database" --add-data "pages;pages" main.py
```

The executable will be located in the `dist` folder.

## Troubleshooting
- Ensure all dependencies are installed
- Check Python version compatibility
- Verify SQLite database path

## License
[Your License Here] 