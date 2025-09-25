#!/usr/bin/env python3
"""
CSV Schedule Generator
Generates and displays course schedules in CSV format.
Provides functionality to create, format, and export schedule data as CSV files.
"""

import csv
import json
from typing import Dict, List, Any, Optional, Tuple
from io import StringIO
from datetime import datetime, timedelta
import os


class ScheduleCSVGenerator:
    """
    Generates and manages course schedules in CSV format.
    Handles schedule creation, formatting, and export operations.
    """
    
    def __init__(self, config: Dict = None, time_slots: Dict = None):
        """
        Initialize the CSV generator with configuration data.
        
        Args:
            config: Configuration dictionary containing courses and faculty
            time_slots: Time slot configuration dictionary
        """
        self.config = config or {}
        self.time_slots = time_slots or {}
        self.schedules = []
        self.csv_headers = [
            'Course ID', 'Credits', 'Faculty', 'Room', 'Lab',
            'Day', 'Start Time', 'End Time', 'Duration', 'Instance', 'Conflicts'
        ]
    
    def generate_sample_schedules(self, count: int = 5) -> List[Dict]:
        """
        Generate sample schedules for demonstration purposes.
        
        Args:
            count: Number of schedules to generate
            
        Returns:
            List of generated schedule dictionaries
        """
        schedules = []
        
        if not self.config.get('courses'):
            # Generate sample data if no config provided
            sample_courses = [
                {'course_id': 'CMSC 140', 'credits': 4, 'room': ['Roddy 136'], 'lab': [], 'faculty': ['Hardy']},
                {'course_id': 'CMSC 161', 'credits': 4, 'room': ['Roddy 136'], 'lab': ['Linux'], 'faculty': ['Zoppetti']},
                {'course_id': 'CMSC 330', 'credits': 4, 'room': ['Roddy 147'], 'lab': ['Mac'], 'faculty': ['Xie']},
            ]
            courses = sample_courses
        else:
            courses = self.config['courses']
        
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        times = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00']
        
        for i in range(count):
            schedule = {
                'schedule_id': f'Schedule_{i+1}',
                'courses': [],
                'faculty_assignments': {},
                'room_assignments': {},
                'optimization_score': 85.5 + (i * 2.3)
            }
            
            # Assign courses to time slots
            for j, course in enumerate(courses[:4]):  # Limit to 4 courses per schedule
                course_assignment = {
                    'course_id': course['course_id'],
                    'credits': course['credits'],
                    'faculty': course.get('faculty', ['TBD'])[0] if course.get('faculty') else 'TBD',
                    'room': course.get('room', ['TBD'])[0] if course.get('room') else 'TBD',
                    'lab': ', '.join(course.get('lab', [])) or 'None',
                    'day': days[j % len(days)],
                    'start_time': times[j % len(times)],
                    'end_time': self._calculate_end_time(times[j % len(times)], course['credits']),
                    'duration': self._calculate_duration(course['credits']),
                    'instance': f'Instance {j+1}',
                    'conflicts': ', '.join(course.get('conflicts', [])) or 'None'
                }
                schedule['courses'].append(course_assignment)
            
            schedules.append(schedule)
        
        self.schedules = schedules
        return schedules
    
    def _calculate_end_time(self, start_time: str, credits: int) -> str:
        """Calculate end time based on start time and credits."""
        try:
            start = datetime.strptime(start_time, '%H:%M')
            duration_minutes = credits * 50  # 50 minutes per credit hour
            end = start + timedelta(minutes=duration_minutes)
            return end.strftime('%H:%M')
        except:
            return '12:00'  # Default fallback
    
    def _calculate_duration(self, credits: int) -> str:
        """Calculate duration string based on credits."""
        minutes = credits * 50
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{mins}m"
    
    def generate_schedules_from_config(self, limit: int = 10) -> List[Dict]:
        """
        Generate schedules from provided configuration data.
        
        Args:
            limit: Maximum number of schedules to generate
            
        Returns:
            List of generated schedules
        """
        if not self.config:
            print("No configuration provided, generating sample schedules...")
            return self.generate_sample_schedules(limit)
        
        schedules = []
        courses = self.config.get('courses', [])
        faculty_data = self.config.get('faculty', [])
        
        # Create faculty lookup
        faculty_lookup = {f['name']: f for f in faculty_data}
        
        for i in range(limit):
            schedule = {
                'schedule_id': f'Config_Schedule_{i+1}',
                'courses': [],
                'total_credits': 0,
                'faculty_workload': {},
                'room_utilization': {},
                'optimization_score': 75.0 + (i * 1.5)
            }
            
            # Select subset of courses for this schedule
            selected_courses = courses[:min(6, len(courses))]  # Limit courses per schedule
            
            for j, course in enumerate(selected_courses):
                # Get faculty assignment
                faculty_name = 'Unassigned'
                if course.get('faculty'):
                    faculty_name = course['faculty'][0]
                
                # Generate time assignment
                days = ['MON', 'WED', 'FRI'] if course.get('credits', 3) == 3 else ['TUE', 'THU']
                base_time = f"{8 + (j % 8):02d}:00"
                
                course_entry = {
                    'course_id': course['course_id'],
                    'credits': course.get('credits', 3),
                    'faculty': faculty_name,
                    'room': course.get('room', ['TBD'])[0] if course.get('room') else 'TBD',
                    'lab': ', '.join(course.get('lab', [])) or 'None',
                    'day': days[0],  # Primary day
                    'start_time': base_time,
                    'end_time': self._calculate_end_time(base_time, course.get('credits', 3)),
                    'duration': self._calculate_duration(course.get('credits', 3)),
                    'instance': f'Inst{j+1:02d}',
                    'conflicts': ', '.join(course.get('conflicts', [])) or 'None'
                }
                
                schedule['courses'].append(course_entry)
                schedule['total_credits'] += course.get('credits', 3)
            
            schedules.append(schedule)
        
        self.schedules = schedules
        return schedules
    
    def schedules_to_csv_string(self, schedules: List[Dict] = None) -> str:
        """
        Convert schedules to CSV string format.
        
        Args:
            schedules: List of schedules to convert (uses self.schedules if None)
            
        Returns:
            CSV formatted string
        """
        if schedules is None:
            schedules = self.schedules
        
        if not schedules:
            return "No schedules available to convert."
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        extended_headers = ['Schedule ID'] + self.csv_headers + ['Optimization Score']
        writer.writerow(extended_headers)
        
        # Write data
        for schedule in schedules:
            schedule_id = schedule.get('schedule_id', 'Unknown')
            optimization_score = schedule.get('optimization_score', 0.0)
            
            for course in schedule.get('courses', []):
                row = [
                    schedule_id,
                    course.get('course_id', ''),
                    course.get('credits', ''),
                    course.get('faculty', ''),
                    course.get('room', ''),
                    course.get('lab', ''),
                    course.get('day', ''),
                    course.get('start_time', ''),
                    course.get('end_time', ''),
                    course.get('duration', ''),
                    course.get('instance', ''),
                    course.get('conflicts', ''),
                    optimization_score
                ]
                writer.writerow(row)
        
        return output.getvalue()
    
    def display_schedules_csv(self, schedules: List[Dict] = None) -> None:
        """
        Display schedules in CSV format to console.
        
        Args:
            schedules: List of schedules to display (uses self.schedules if None)
        """
        csv_content = self.schedules_to_csv_string(schedules)
        print("=" * 80)
        print("COURSE SCHEDULES - CSV FORMAT")
        print("=" * 80)
        print(csv_content)
        print("=" * 80)
    
    def save_schedules_csv(self, filename: str, schedules: List[Dict] = None) -> bool:
        """
        Save schedules to a CSV file.
        
        Args:
            filename: Output filename for the CSV file
            schedules: List of schedules to save (uses self.schedules if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            csv_content = self.schedules_to_csv_string(schedules)
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)
            
            print(f"✅ Schedules saved successfully to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving CSV file: {e}")
            return False
    
    def generate_summary_csv(self, schedules: List[Dict] = None) -> str:
        """
        Generate a summary CSV of schedule statistics.
        
        Args:
            schedules: List of schedules to summarize
            
        Returns:
            CSV formatted summary string
        """
        if schedules is None:
            schedules = self.schedules
        
        if not schedules:
            return "No schedules available for summary."
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write summary headers
        writer.writerow(['Metric', 'Value'])
        
        # Calculate statistics
        total_schedules = len(schedules)
        total_courses = sum(len(s.get('courses', [])) for s in schedules)
        avg_courses_per_schedule = total_courses / total_schedules if total_schedules > 0 else 0
        
        # Faculty utilization
        faculty_counts = {}
        room_counts = {}
        
        for schedule in schedules:
            for course in schedule.get('courses', []):
                faculty = course.get('faculty', 'Unassigned')
                room = course.get('room', 'Unassigned')
                
                faculty_counts[faculty] = faculty_counts.get(faculty, 0) + 1
                room_counts[room] = room_counts.get(room, 0) + 1
        
        # Write summary data
        writer.writerow(['Total Schedules', total_schedules])
        writer.writerow(['Total Course Assignments', total_courses])
        writer.writerow(['Average Courses per Schedule', f"{avg_courses_per_schedule:.2f}"])
        writer.writerow(['Unique Faculty Used', len(faculty_counts)])
        writer.writerow(['Unique Rooms Used', len(room_counts)])
        
        # Top faculty and rooms
        if faculty_counts:
            top_faculty = max(faculty_counts.items(), key=lambda x: x[1])
            writer.writerow(['Most Utilized Faculty', f"{top_faculty[0]} ({top_faculty[1]} assignments)"])
        
        if room_counts:
            top_room = max(room_counts.items(), key=lambda x: x[1])
            writer.writerow(['Most Utilized Room', f"{top_room[0]} ({top_room[1]} assignments)"])
        
        return output.getvalue()
    
    def display_summary(self, schedules: List[Dict] = None) -> None:
        """
        Display schedule summary statistics.
        
        Args:
            schedules: List of schedules to summarize
        """
        summary_csv = self.generate_summary_csv(schedules)
        print("\n" + "=" * 50)
        print("SCHEDULE SUMMARY STATISTICS")
        print("=" * 50)
        print(summary_csv)
        print("=" * 50)


def load_config_and_generate_csv(config_file: str, time_slots_file: str = None, 
                                output_file: str = "schedules.csv", limit: int = 10) -> None:
    """
    Load configuration and generate CSV schedules.
    
    Args:
        config_file: Path to configuration JSON file
        time_slots_file: Path to time slots JSON file (optional)
        output_file: Output CSV filename
        limit: Number of schedules to generate
    """
    try:
        # Load configuration
        with open(config_file, 'r') as f:
            data = json.load(f)
            config = data.get('config', data)
        
        # Load time slots if separate file
        time_slots = None
        if time_slots_file and time_slots_file != config_file:
            with open(time_slots_file, 'r') as f:
                time_data = json.load(f)
                time_slots = time_data.get('time_slot_config', time_data)
        elif 'time_slot_config' in data:
            time_slots = data['time_slot_config']
        
        # Generate CSV schedules
        generator = ScheduleCSVGenerator(config, time_slots)
        schedules = generator.generate_schedules_from_config(limit)
        
        # Display and save
        generator.display_schedules_csv(schedules)
        generator.display_summary(schedules)
        generator.save_schedules_csv(output_file, schedules)
        
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
    except Exception as e:
        print(f"❌ Error generating CSV schedules: {e}")


def main():
    """
    Main function for command-line usage of the CSV generator.
    """

    print("📊 Course Schedule CSV Generator")
    print("=" * 40)
    
    # Get user input
    config_file = input("Enter path to configuration file (or just press Enter for an example): ").strip()
    
    if not config_file:
        # Demo mode with sample data
        print("\n🎯 Showing example...")
        generator = ScheduleCSVGenerator()
        schedules = generator.generate_sample_schedules(5)
        
        generator.display_schedules_csv(schedules)
        generator.display_summary(schedules)
        
        save_demo = input("\nSave demo schedules to CSV? (y/n): ").strip().lower()
        if save_demo in ['y', 'yes']:
            filename = input("Enter filename (default: demo_schedules.csv): ").strip() or "demo_schedules.csv"
            generator.save_schedules_csv(filename, schedules)
    
    else:
        # Use provided configuration
        try:
            limit = int(input("Number of schedules to generate (default: 10): ").strip() or "10")
            output_file = input("Output CSV filename (default: schedules.csv): ").strip() or "schedules.csv"
            
            load_config_and_generate_csv(config_file, output_file=output_file, limit=limit)
            
        except ValueError:
            print("❌ Invalid number entered, using default limit of 10")
            load_config_and_generate_csv(config_file, limit=10)
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()