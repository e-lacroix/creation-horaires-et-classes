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
   - `Student`, `Teacher`, `Classroom`, `Course` entities
   - `CourseType` enum with Quebec secondary course types
   - `TimeSlot` and `ScheduleAssignment` for scheduling

2. **scheduler.py** - Constraint satisfaction optimizer:
   - Uses Google OR-Tools CP-SAT solver
   - Implements scheduling constraints (teacher conflicts, room conflicts, student conflicts)
   - Optimizes for minimal resource usage
   - Decision variables: course-to-timeslot, course-to-teacher, course-to-room, student-to-course

3. **data_generator.py** - Generates sample data:
   - 56 students all in Grade 4 (Secondaire 4)
   - 36 total courses with Quebec-specific distribution
   - Minimal teacher set (13 teachers with overlapping competencies)
   - 8 classrooms

4. **gui.py** - Tkinter desktop interface:
   - Configuration tab showing course requirements
   - Results tab displaying optimized schedule in TreeView
   - Statistics tab with teacher load, room usage, student distribution
   - Excel export functionality

### Constraints Implemented

- Each course assigned to exactly one timeslot (9 days × 4 periods = 36 slots)
- Each course has one teacher (only teachers qualified for that course type)
- Each course has one room
- Teachers cannot teach multiple courses simultaneously
- Rooms cannot host multiple courses simultaneously
- Students cannot attend multiple courses simultaneously
- Maximum 28 students per course
- Each student must take at least one course of each required type

### Quebec Course Requirements

The system generates schedules for these course types (with class counts):
- Science (4), STE (2), ASC (2)
- Français (6), Math SN (6)
- Anglais (4), Histoire (4)
- CCQ (2), Espagnol (2)
- Éducation physique (2), Option (2)

## Key Design Decisions

- **OR-Tools CP-SAT**: Chosen for efficient constraint satisfaction solving with optimization objectives
- **Tkinter**: Standard Python GUI library for cross-platform desktop app
- **Minimal Resource Optimization**: Primary objective is to minimize classrooms used (secondary: balance teacher load)
- **Teacher Specialization**: Teachers can teach multiple related subjects (e.g., Science teachers can teach Science, STE, ASC)

## Development Notes

- The project uses French terminology to match Quebec educational context
- Timeslots are 1-indexed (Day 1-9, Period 1-4)
- Solver timeout set to 60 seconds; may need adjustment for larger instances
- Excel export creates multi-sheet workbook (schedule, teacher assignments)
