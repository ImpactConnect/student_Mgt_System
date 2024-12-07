PROGRAMMES = [
    "Web Development",
    "Robotics",
    "Data Analytics",
    "Graphics Design",
    "Mobile App Development",
    "Basic Computer Training",
    "UI/UX Design",
    "Advanced Excel",
    "Blogging",
    "Content Creation"
]

DURATIONS = [
    "1 month",
    "3 months",
    "6 months",
    "9 months"
]

SCHEDULES = [
    "Weekdays (Morning)",
    "Weekdays (Afternoon)",
    "Weekend (Saturday)",
    "Weekend (Sunday)",
    "Online (Flexible)"
]

GENDERS = ["Male", "Female", "Other"]

STUDENT_STATUSES = [
    'Active',
    'Graduated',
    'Dropped Out'
]

def add_programme(new_programme):
    """
    Add a new programme to the PROGRAMMES list
    
    Args:
        new_programme (str): Name of the new programme to add
    
    Returns:
        bool: True if programme was added successfully, False if it already exists
    """
    # Convert to title case and strip whitespace
    new_programme = new_programme.strip().title()
    
    # Check if programme already exists (case-insensitive)
    if new_programme.lower() in [p.lower() for p in PROGRAMMES]:
        return False
    
    # Add the new programme
    PROGRAMMES.append(new_programme)
    
    # Optional: Sort the list alphabetically
    PROGRAMMES.sort()
    
    return True 