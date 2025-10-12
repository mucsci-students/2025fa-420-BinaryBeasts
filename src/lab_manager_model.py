# lab_manager(model).py
# Author: Naomi Ermold

"""
Interfaces with main file to implement a GUI for the add, modify, and delete lab 
feature functionality from the preexisting Scheduler CLI program in MVC format.

User Story: Adding, Modifying, and Deleting Labs from a Scheduler Program (GUI)

"As a scheduler administrator, I want to press buttons that allow me to add, modify,
or delete preexisting labs from a course schedule builder (Scheduler)"

"""

import json

class LabModel:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"config": {"courses": [], "labs": []}}

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=4)
                return True
        except Exception:
            return False

    def get_courses(self):
        return self.data.get("config", {}).get("courses", [])

    def get_labs(self):
        return self.data.get("config", {}).get("labs", [])

    def get_course_by_id(self, course_id):
        for course in self.get_courses():
            if course.get("course_id") == course_id:
                return course
        return None

    def add_lab_to_course(self, course_id, lab_type):
        course = self.get_course_by_id(course_id)
        if course is None:
            return False, "Course not found"

        if 'lab' not in course or course['lab'] is None:
            course['lab'] = []

        if lab_type in course['lab']:
            return False, "Lab already exists in this course"

        course['lab'].append(lab_type)
        return True, f"Added lab '{lab_type}' to course '{course_id}'"

    def modify_lab(self, course_id, old_lab, new_lab):
        course = self.get_course_by_id(course_id)
        if course is None or 'lab' not in course:
            return False, "Course or lab not found"

        if old_lab not in course['lab']:
            return False, f"{old_lab} not in course"

        course['lab'] = [new_lab if lab == old_lab else lab for lab in course['lab']]
        return True, f"Modified lab '{old_lab}' to '{new_lab}'"

    def delete_lab(self, course_id, lab_type):
        course = self.get_course_by_id(course_id)
        if not course or 'lab' not in course:
            return False, "Course or lab not found"

        if lab_type not in course['lab']:
            return False, "Lab not found in course"

        course['lab'].remove(lab_type)
        return True, f"Deleted lab '{lab_type}' from course '{course_id}'"
