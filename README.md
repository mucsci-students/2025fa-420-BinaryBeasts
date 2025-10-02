# Scheduler CLI Application

**Team BinaryBeasts** - CMSC 420 Fall 2025
- Kenner Jimenez
- Sophia Koziar
- Andrew Delich
- Naomi Ermold
- Collin Donnan
- Patrick Kreibick
- Tyler Brown

## Overview

This is a course scheduling system with an command-line interface. The application allows you to manage courses, rooms, labs, faculty, and generate optimized class schedules.

## Features

- **Course Management**: Add, modify, and delete courses with credits, room assignments, lab requirements, faculty assignments, and conflict resolution
- **Room Management**: Manage classroom inventory with impact analysis for deletions
- **Lab Management**: Assign and manage lab requirements for courses (Linux/Mac labs)
- **Faculty Management**: Manage faculty with availability, preferences, and credit limits
- **Schedule Generation**: Generate optimized schedules in CSV or JSON format
- **Configuration Management**: Import/export configurations with validation

## Prerequisites

- Python 3.12 or higher
- Git (for cloning the repository)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/mucsci-students/2025fa-420-BinaryBeasts.git
cd 2025fa-420-BinaryBeasts
```

### Step 2: Set Up Python Environment (Optional but Recommended)

Create a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv scheduler_env

# Activate virtual environment
# On Windows:
scheduler_env\Scripts\activate
# On macOS/Linux:
source scheduler_env/bin/activate
```

### Step 3: Install Dependencies

Install the required course constraint scheduler library:

```bash
# Install the course constraint scheduler library
pip install course-constraint-scheduler
```
**Note:** This library provides the core scheduling algorithms and constraint satisfaction functionality required for generating optimized class schedules.

## Usage

### Quick Start

1. **Navigate to the project directory:**
   ```bash
   cd 2025fa-420-BinaryBeasts
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

### Step-by-Step Usage Guide

#### Initial Setup

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Provide a configuration file:**
   - Use the included `example.json` for testing
   - Or create your own JSON configuration file
   - The application will load both configuration and time slot data from this file

#### Main Menu Navigation

The application presents a main menu with 6 options:

```
SCHEDULER CLI - MAIN MENU
==================================================
1. 🗂️  Course Management
2. 🏢 Room Management  
3. 🔬 Lab Management
4. 👥 Faculty Management
5. 📅 Generate Schedules
6. 🚪 Exit
==================================================
```

#### 1. Course Management

Manage all course-related data:

- **View Courses**: Display all courses with details (credits, rooms, labs, faculty, conflicts)
- **Add Course**: Create new courses with interactive prompts
- **Modify Course**: Edit existing course details and assignments
- **Delete Course**: Remove courses (supports multiple instances)

**Example workflow:**
1. Select option `1` from main menu
2. Choose `2` to add a new course
3. Enter course details when prompted:
   - Course ID (e.g., "CMSC 140")
   - Credits (1-6)
   - Available rooms
   - Required labs
   - Assigned faculty
   - Conflicting courses

#### 2. Room Management

Manage classroom inventory:

- **View Rooms**: List all available rooms
- **Add Room**: Add new classroom spaces
- **Edit Room**: Rename rooms (automatically updates all references)
- **Delete Room**: Remove rooms with impact analysis

**Example workflow:**
1. Select option `2` from main menu
2. Choose `2` to add a new room
3. Enter room name (e.g., "Roddy 101")
4. System automatically updates course and faculty preferences

#### 3. Lab Management

Manage lab assignments to courses:

- **View Labs**: Show lab usage across all courses
- **Add Lab**: Assign labs to specific courses
- **Modify Lab**: Change lab assignments for courses
- **Remove Lab**: Remove lab requirements from courses

**Example workflow:**
1. Select option `3` from main menu
2. Choose `2` to add lab to course
3. Select course from the list
4. Choose lab type (Linux/Mac)

#### 4. Faculty Management

Manage faculty information and preferences:

- **View Faculty**: Display all faculty with availability, preferences, and credit limits
- **Add Faculty**: Create new faculty profiles with comprehensive details
- **Edit Faculty**: Modify faculty information and preferences
- **Delete Faculty**: Remove faculty with course impact analysis

**Faculty details include:**
- Name and contact information
- Credit range (minimum/maximum)
- Unique course limits
- Weekly availability schedule
- Course preferences (1-5 rating scale)
- Room preferences (1-5 rating scale)
- Lab preferences (1-5 rating scale)

#### 5. Generate Schedules

Create optimized class schedules:

1. **Configure generation parameters:**
   - Output file location
   - Number of schedules to generate (1-1000)
   - Output format (JSON/CSV)
   - Enable optimization
   - Show configuration preview

2. **Review configuration** (if enabled):
   - Courses summary
   - Room availability
   - Faculty assignments
   - Time slot patterns

3. **Generate and save** schedules to specified output file

## Configuration File Format

The application uses JSON configuration files with the following structure:

```json
{
  "config": {
    "rooms": ["Roddy 136", "Roddy 140", "Roddy 147"],
    "labs": ["Linux", "Mac"],
    "courses": [
      {
        "course_id": "CMSC 140",
        "credits": 4,
        "room": ["Roddy 136", "Roddy 140"],
        "lab": ["Linux"],
        "conflicts": ["CMSC 161"],
        "faculty": ["Dr. Smith"]
      }
    ],
    "faculty": [
      {
        "name": "Dr. Smith",
        "minimum_credits": 8,
        "maximum_credits": 12,
        "unique_course_limit": 3,
        "times": {
          "MON": ["09:00-17:00"],
          "TUE": [],
          "WED": ["09:00-17:00"],
          "THU": [],
          "FRI": ["09:00-15:00"]
        },
        "course_preferences": {
          "CMSC 140": 5,
          "CMSC 161": 4
        },
        "room_preferences": {
          "Roddy 136": 5,
          "Roddy 140": 3
        },
        "lab_preferences": {
          "Linux": 5,
          "Mac": 2
        }
      }
    ]
  },
  "time_slot_config": {
    "times": {
      "MON": [{"start": "08:00", "spacing": 60, "end": "19:00"}]
    },
    "classes": [
      {
        "credits": 4,
        "meetings": [
          {"day": "MON", "duration": 110, "lab": true},
          {"day": "WED", "duration": 110}
        ]
      }
    ]
  }
}
```

## File Management

### Input Files
- **Configuration File**: Contains course, room, lab, and faculty data
- **Time Slot File**: Defines available time slots and class patterns (can be same file)

### Output Files
- **JSON Format**: Structured schedule data for programmatic use
- **CSV Format**: Spreadsheet-compatible schedule data

### Backup and Recovery
- All management operations include save/cancel options
- Changes are only persisted when explicitly saved
- Original configuration files are preserved until save operation

## Troubleshooting

### Common Issues

1. **File Not Found Error**
   ```
   Solution: Ensure the configuration file path is correct and the file exists
   ```

2. **Permission Denied**
   ```
   Solution: Check file permissions and ensure write access for output directory
   ```

3. **Invalid JSON Format**
   ```
   Solution: Validate JSON syntax using a JSON validator
   ```

4. **Faculty Management Errors**
   ```
   Solution: Ensure faculty names are unique and preference values are 1-5
   ```
## Contributing

This project is part of CMSC 420. For questions, contact the BinaryBeasts

.


