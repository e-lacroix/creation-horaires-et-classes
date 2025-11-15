# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop application for generating optimized schedules for Quebec secondary schools (Secondaire 4). Le projet est en français et pour le Québec. The system uses constraint satisfaction algorithms to create schedules that minimize teacher and classroom usage while respecting Quebec educational requirements.

**Project Name:** creation-horaires-et-classes
**Purpose:** Create optimized schedules for 56 secondary students (Grade 4) with Quebec-specific course requirements
**License:** GNU General Public License v3.0
**Language:** Python 3.8+

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

### Test Data Generation
```bash
python data_generator.py
```

## Architecture

### Core Components

1. **models.py** - Data models for the domain:
   - `Student`, `Teacher`, `Classroom` entities
   - `CourseType` enum with Quebec secondary course types
   - `TimeSlot` for time representation
   - `CourseSession` for grouping students in the same course at the same time
   - `StudentScheduleEntry` for individual student schedule entries
   - `Course` (legacy) and `ScheduleAssignment` (for backward compatibility)

2. **scheduler.py** - Constraint satisfaction optimizer with individual schedules:
   - Uses Google OR-Tools CP-SAT solver
   - Creates personalized schedules for each student
   - Dynamically creates sessions by grouping students with matching timeslots
   - Decision variables: student-course-timeslot, session-active, session-teacher, session-room
   - Optimizes for minimal number of active sessions (primary objective)
   - Returns: (success, sessions, student_schedules)

3. **data_generator.py** - Generates sample data:
   - Loads data from CSV files if available (via data_manager.py)
   - Falls back to generating default data in memory
   - Configurable number of students (default 56), all in Grade 4 (Secondaire 4)
   - Course requirements loaded from program JSON files
   - Function signature: `generate_sample_data(num_students: int = 56, use_csv_data: bool = True) -> (course_requirements, teachers, classrooms, students)`

4. **data_manager.py** - CSV and JSON data management system:
   - `Programme`: Data model for academic programs with course requirements
   - `EleveData`: Student data (name, ID, program, restrictions, talents)
   - `EnseignantData`: Teacher data (name, ID, subjects, restrictions, preferred classroom)
   - `ClasseData`: Classroom data (ID, name, capacity, allowed subjects)
   - `DataManager`: Load/save operations for all data types
   - Data stored in `data/` directory with subdirectories for each type
   - See `GUIDE_GESTION_DONNEES.md` for detailed usage

5. **creer_donnees_exemple.py** - Sample data generator script:
   - Creates CSV files with 56 students, 13 teachers, 8 classrooms
   - Creates 2 default programs (Secondaire 4 Régulier, Secondaire 4 Sciences)
   - Generates realistic random data (talents, restrictions, specializations)
   - Can be run standalone: `python creer_donnees_exemple.py`

6. **gui.py** - Material Design desktop interface with ttkbootstrap:
   - Configuration panel with student count spinbox (1-200 students)
   - Course requirements info with emojis
   - **Sessions tab**: Displays all course sessions with teacher, room, and student count
   - **Individual Schedules tab**: View personalized schedule for each student with dropdown selector
   - **Teacher Schedules tab**: View personalized schedule for each teacher
   - **Statistics tab**: Detailed session analysis, teacher load, room usage, and optimization efficiency
   - **Data Management tab**: Manage CSV/JSON files, open files/folders, regenerate sample data
   - Excel export with 3 sheets: Sessions, Individual Schedules, and Teacher Assignments
   - Modern UI with primary/success/info color schemes
   - Status bar with real-time feedback

### Constraints Implemented

**Individual Schedule Constraints:**
- Each student must have exactly one timeslot for each required course type
- A student cannot attend multiple courses simultaneously
- A student cannot have more than one course of the same subject type per day

**Session Constraints:**
- Each active session must have exactly one teacher (qualified for that course type)
- Each active session must have exactly one classroom
- Maximum 28 students per session
- A teacher cannot teach multiple sessions simultaneously
- A classroom cannot host multiple sessions simultaneously

**Optimization Objective:**
- Minimize the total number of active sessions (primary goal)
- This automatically minimizes resource usage (teachers and classrooms)

### Quebec Course Requirements

The system generates schedules for these course types (with class counts):
- Science (4), STE (2), ASC (2)
- Français (6), Math SN (6)
- Anglais (4), Histoire (4)
- CCQ (2), Espagnol (2)
- Éducation physique (2), Option (2)

## Key Design Decisions

- **OR-Tools CP-SAT**: Chosen for efficient constraint satisfaction solving with optimization objectives
- **ttkbootstrap**: Modern Material Design-inspired GUI library built on Tkinter for better aesthetics
- **Individual Schedules with Session Optimization**: Each student has a personalized schedule with the same 36 courses, but timeslots can differ. Students are grouped into sessions to minimize resources.
- **Dynamic Session Creation**: Sessions are created dynamically based on which students take courses at the same timeslots, optimizing for minimal classrooms and teachers
- **Minimal Resource Optimization**: Primary objective is to minimize the number of active sessions (fewer sessions = fewer classrooms and teachers used)
- **Teacher Specialization**: Teachers can teach multiple related subjects (e.g., Science teachers can teach Science, STE, ASC)
- **Mandatory Course Participation**: All students must attend all 36 courses (each student gets exactly one timeslot per course type)
- **Daily Subject Limit**: Students can only have one course per subject type per day to reduce cognitive load

## Data Management System

### Overview
The system now uses CSV and JSON files to manage all data, allowing customization without code changes:

- **data/eleves/eleves.csv**: Student data (name, ID, program, restrictions, talents per subject)
- **data/enseignants/enseignants.csv**: Teacher data (name, ID, subjects, restrictions, preferred classroom)
- **data/classes/classes.csv**: Classroom data (ID, name, capacity, allowed subjects)
- **data/programmes/*.json**: Program definitions with course requirements

### Creating/Modifying Data

**Using the GUI** (recommended):
1. Open the application (`python main.py`)
2. Navigate to the "🗂️ Gestion des Données" tab
3. Click "Ouvrir le fichier CSV" to edit files with Excel/LibreOffice
4. Or use "Regénérer les données d'exemple" to reset to defaults

**Manual editing**:
- Edit CSV files directly in `data/` subdirectories
- Use UTF-8 encoding
- Follow the format specified in `data/README.md` and `GUIDE_GESTION_DONNEES.md`

### Available Programs
Programs define course requirements for different student tracks. Each program is a JSON file in `data/programmes/` with:
- Program name
- Course requirements (CourseType → count)
- Description

Students reference programs by name in their CSV entry. The system loads course requirements from the program file.

### Data Loading Flow
1. `generate_sample_data()` in data_generator.py attempts to load from CSV
2. If CSV files exist, `load_data_from_csv()` converts them to internal models
3. Program requirements are loaded from JSON based on student programs
4. If CSV loading fails, falls back to `generate_default_data()` (in-memory generation)

## Development Notes

- The project uses French terminology to match Quebec educational context
- Timeslots are 1-indexed (Day 1-9, Period 1-4)
- Solver timeout set to 600 seconds (10 minutes); configured for 176 students
- Excel export creates 3-sheet workbook: Sessions, Individual Schedules, Teacher Assignments
- Each student receives a personalized schedule with the same course requirements
- Sessions are dynamically created to group students efficiently
- The optimizer achieves high grouping efficiency (typically >80% reduction in potential sessions)
