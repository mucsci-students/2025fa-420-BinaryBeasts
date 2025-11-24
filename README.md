# College Course Scheduler

**Team BinaryBeasts** - CMSC 420 Fall 2025
- Andrew Delich
- Collin Donnan
- Kenner Jimenez
- Naomi Ermold
- Patrick Kreibick
- Sophia Koziar
- Tyler Brown

## Overview

A comprehensive course scheduling system with both **Command-Line Interface (CLI)** and **Graphical User Interface (GUI)**. The application allows you to manage courses, rooms, labs, faculty, and generate optimized class schedules using constraint-based optimization.

## Features

### Core Management System
- **Course Management**: Add, modify, and delete courses with credits, room assignments, lab requirements, faculty assignments, and conflict resolution
- **Room Management**: Manage classroom inventory with automatic reference updates and impact analysis
- **Lab Management**: Manage lab types (Mac, Linux, Windows) as global resources with automatic reference updates
- **Faculty Management**: Comprehensive faculty profiles with availability, preferences (courses, rooms, labs), and credit limits
- **Schedule Generation**: Generate optimized schedules using constraint-based solver
- **Configuration Management**: Import/export configurations in JSON format with validation

### Schedule Viewing & Navigation
- **Multiple View Modes**:
  - **Basic View**: Tabular schedule with all courses
  - **Room View**: Navigate room-by-room with weekly grid layout
  - **Faculty View**: Navigate faculty-by-faculty with course assignments
- **Schedule Navigation**: Browse through multiple generated schedules
- **Export Options**: Save schedules in PDF, JSON or CSV format

### User Interfaces
- **CLI**: Full-featured command-line interface with menu-driven navigation
- **GUI**: Modern PyQt5-based graphical interface with modal dialogs

## Prerequisites

- Python 3.13.1 (or Python 3.7+)
- PyQt5 (for GUI)
- Git (for cloning the repository)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/mucsci-students/2025fa-420-BinaryBeasts.git
cd 2025fa-420-BinaryBeasts
```

### Step 2: Set Up Python Environment (Recommended)

Create a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- PyQt5 (for GUI)
- scheduler library (included in project)

## Usage

### GUI Application (Recommended)

1. **Start the GUI:**
   ```bash
   python app.py
   ```

2. **Upload Configuration:**
   - Click "Upload Configuration File"
   - Select a JSON configuration file 

3. **Manage Resources:**
   - **Edit Courses**: Add, modify, or delete course sections
   - **Edit Faculty**: Manage faculty profiles and preferences
   - **Edit Labs**: Manage lab types 
   - **Edit Rooms**: Manage classroom inventory

4. **Generate Schedules:**
   - Click "Generate Schedule"
   - Enter number of schedules to generate
   - View schedules with navigation and multiple view modes
   - Export to JSON or CSV

5. **Load Saved Schedules:**
   - Click "Upload Schedule"
   - Select previously saved schedule file 
   - Navigate and view schedules

### CLI Application

1. **Start the CLI:**
   ```bash
   python main.py
   ```

2. **Provide Configuration:**

3. **Main Menu Navigation:**
## Detailed Feature Guide

### 1. Course Management

**CLI Features:**
- View all courses with details (credits, rooms, labs, faculty, conflicts)
- Add new course sections interactively
- Modify existing course sections
- Delete course sections (with option to delete all instances)
- Automatic validation of course data

**GUI Features:**
- Course list showing all course IDs
- Section list for each course ID
- Add/Edit/Delete buttons with validation
- Modal dialogs for course entry
- Save changes to configuration

**Course Fields:**
- Course ID (e.g., "CMSC 140.01")
- Credits (1-6)
- Rooms (multiple allowed)
- Labs (multiple allowed)
- Faculty (multiple allowed)
- Conflicts (other courses)

### 2. Room Management

**Features:**
- View all available rooms
- Add new rooms
- Rename rooms (automatically updates all course and faculty references)
- Delete rooms with impact analysis showing:
  - Affected courses
  - Faculty with room preferences
  - Confirmation before deletion

**Reference Updates:**
- Course room assignments automatically updated
- Faculty room preferences automatically updated

### 3. Lab Management

**Features:**
- View all lab types
- Add new lab types (e.g., Mac, Linux, Windows, Android)
- Rename labs (automatically updates all references)
- Delete labs with impact analysis showing:
  - Affected courses
  - Faculty with lab preferences
  - Confirmation before deletion

**Lab Types as Global Resources:**
- Labs are managed as a global list
- Courses reference labs from this list
- Faculty can set preferences for each lab type

### 4. Faculty Management

**Features:**
- View all faculty with comprehensive details
- Add new faculty with full profile
- Modify faculty information and preferences
- Delete faculty with impact analysis

**Faculty Profile Includes:**
- Name
- Credit limits (minimum and maximum)
- Unique course limit
- Weekly availability (MON-FRI with time ranges)
- Course preferences (0-10 rating scale)
- Room preferences (0-10 rating scale)
- Lab preferences (0-10 rating scale)

### 5. Schedule Generation & Navigation

**Generation:**
- Specify number of schedules to generate
- Uses constraint-based optimization
- Respects faculty availability, preferences, and credit limits
- Avoids course conflicts

**Navigation (GUI):**
- Next/Previous schedule buttons
- Go to specific schedule number
- View by room (room-by-room with weekly grid)
- View by faculty (faculty-by-faculty with assignments)
- Export to JSON or CSV

**Schedule Views:**
- **Basic View**: Tabular format with columns:
  - Course ID
  - Faculty
  - Room
  - Lab
  - Time Slots (MON-FRI)

- **Room View**: For each room, shows weekly grid:
  - Course assignments by day
  - Faculty teaching each course
  - Time slots

- **Faculty View**: For each faculty, shows:
  - Courses assigned
  - Rooms for each course
  - Time slots by day

### 6. Import/Export

**Configuration Files:**
- Save configuration changes to JSON
- Load configuration from JSON
- Preserves all data including preferences

**Schedule Files:**
- Export schedules to JSON (with schedule IDs)
- Export schedules to CSV (spreadsheet format)
- Export schedules by faculty to PDF
- Import previously saved schedules for viewing


## Architecture

The application follows the **Model-View-Controller (MVC)** pattern:

- **Models**: Manage data and business logic (Course Model, Faculty Model, Room Model, Lab Model, Main Model)
- **Views**: Handle user interface (CLI Views for command-line interface, GUI Views for graphical interface)
- **Controllers**: Bridge between models and views (Course Controller, Faculty Controller, Room Controller, Lab Controller, etc.)

### Design Patterns Implementation

**Observer Pattern**: Automatic cross-manager dependency resolution
- **Core Files**: Observer Pattern module (Observable base class, EventType enum, EventData container)
- **Implementation**: Conflict Resolution module (ConflictResolutionObserver)
- **Integration**: All model managers inherit from Observable and emit events when data changes

**Factory Pattern**: Centralized dialog creation with consistent initialization
- **Core Files**: Dialog Factory module (DialogFactory class, DialogType constants)
- **Integration**: Main GUI uses factory to create all management dialogs
- **Products**: Course, Faculty, Lab, and Room management dialogs with their controllers and managers

**Singleton Pattern**: Centralized state management for application-wide data
- **Core Files**: Main Model module (main_model class with singleton implementation)
- **Usage**: Main Controller uses singleton for schedule and configuration management
- **Benefits**: Ensures consistent state across the application lifecycle

**Key Design Principles:**
- Separation of concerns
- Consistent patterns across all resource types
- Automatic reference updates (renaming rooms/labs updates all references)
- Impact analysis before deletions
- Validation at all input points

## Troubleshooting

### Common Issues

1. **PyQt5 Import Error**
   ```
   Solution: Install PyQt5 using: pip install PyQt5
   ```

2. **File Not Found Error**
   ```
   Solution: Ensure the configuration file path is correct and the file exists
   ```

3. **Permission Denied**
   ```
   Solution: Check file permissions and ensure write access for output directory
   ```

4. **Invalid JSON Format**
   ```
   Solution: Validate JSON syntax using a JSON validator (e.g., jsonlint.com)
   ```

5. **No Schedules Generated**
   ```
   Solution: Check that:
   - Courses have assigned faculty
   - Faculty have availability in their time slots
   - There are sufficient rooms for courses
   - Time slot configuration is valid
   ```

### Getting Help

For questions or issues:
- Check the configuration file format
- Verify all required fields are present
- Ensure faculty availability matches time slot configuration
- Contact Team BinaryBeasts

## Contributing

This project is part of CMSC 420 Fall 2025. For questions, contact Team BinaryBeasts.

## License

This project is developed for education