# lab_manager.py
# Author: Naomi E.
"""
Interfaces with main file to implement feature to add, modify, and delete
lab from a scheduler program

User Story: Adding, modifying, or deleting a lab from Scheduler CLI

“As a scheduler administrator, I want to add, modify, or delete a lab so 
that all labs available to schedule are up-to-date.”

"""

import json

class labManager:

    # Parses data from JSON file for Scheduler
    def load_data(self, config_file):
        self.config_file = config_file
        self.data = self.load_config(config_file)

    def load_config(self, filename):
        # Attempt to load JSON file and check for exceptions
        try:
            with open(filename, 'r') as file:
                return json.load(file)
            # Catch if file DNE 
        except FileNotFoundError:
            print("The file " + filename + " does not exist.")
            return None
        # Catch if the file is not JSON extension type
        except json.JSONDecodeError:
            print("The file" + filename + " is not a valid JSON file.")
            return None

    # Saves data into JSON file for Scheduler   
    # Open JSON data file and write information from Scheduler to JSON file
    def save_data(self):
        # if file DNE or no data in file, print error msg
        if self.config_file is None:
            print("Error: File does not exist.")
            return
        # if file exists but has no data, print error msg
        if self.data is None:
            print("Error: File has no data to be written.")
            return
        
        # Write data to file handling exceptions
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.data, file, indent=4)
                print ("Data successfully written to " + self.config_file)
        # Catch any generic exception as failed save,
        except Exception as e:
            # Print error to user console with exception thrown 
            print("Error: Failed to save data. Exception thrown: " + str(e))


    # Locate respective course in JSON data list to add/del/mod lab from in
    # the Scheduler from user CLI input course ID
    def get_course_by_id(self, course_id):
        # Find and return course ID or nothing if none
        if self.data is None:
            print("No data loaded.")
            return None
    
        if 'courses' not in self.data:
            print("Data does not contain 'courses' list.")
            return None
    
        for course in self.data['courses']:
            # Check for course ID in parsed data, if ID matches, return course
            if 'course_id' in course and course['course_id'] == course_id:
                return course
        # Otherwise return nothing
        return None
    

    # Adds lab ['Mac' or 'Linux'] to a course in a scheduler CLI
    def add_lab(self, course_id, lab_type):

    # [Scenario: Add a lab to a course in a schedule]

    # Given I am in the CLI for the Scheduler program
    # When I type in “Add lab”
    # Then I should be prompted to add the course I want to attach the lab to
    # When I type in the course number of the course I want to add a lab to
    # Then I should be prompted to input either ‘Mac’ or ‘Linux'
    # When I type in the lab and press enter
    # Then the lab should be saved to the database with the course entered

        # Add lab_type to course with course_id
        # Look through JSON file data for course data by ID input by user
        course = self.get_course_by_id(course_id)
        if course is None:
            # If course DNE by given ID input by user, print error msg
            print("Course with ID " + course_id + " was not found.")
            return
    
        # If the course doesn't have a lab or labs DNE in list altogether,
        if 'labs' not in course or course['labs'] is None:
            # Create new empty list of labs for the courses to be stored in
            course['labs'] = []

        # If lab type being added to course already exists as a lab in the course,
        if lab_type in course['labs']:
            # Print error msg 
            print("Lab " + lab_type + " already exists in course " + course_id)
            return

        # Once passed all test cases, can add lab to course
        course['labs'].append(lab_type)
        print("Lab " + lab_type + " has been added to course " + course_id)

    # Modifies lab ['Mac' or 'Linux'] attached to a course in a scheduler CLI
    def modify_lab(self, course_id, old_type, new_type):

    # [Scenario: Modifying a pre-existing lab on a course in a schedule]

    # Given I am in the CLI for the Scheduler program
    # When I type "Modify Lab"
    # Then I should be prompted to enter the course whose lab I want to edit
    # When I type in course and press enter
    # Then the course I entered should be saved with the opposite
    # lab type option it previously was in the database ('Mac' <-> 'Linux')

        # Look through JSON file data for course data by ID input by user
        course = self.get_course_by_id(course_id)
        # If input course DNE throw user console an error msg
        if course is None:
            print("Course with ID " + course_id + " does not exist.")
            return
        # If the course doesn't have a lab or labs DNE in list altogether,
        if 'labs' not in course or course['labs'] is None:
            # Throw error message to user console
            print("The course ID " + course_id + " has no labs to modify.")
            return
        # If old type specified by user DNE in given course ID specified,
        if old_type not in course['labs']:
            # Throw error message to user console
            print("Lab " + old_type + " does not exist in " + course_id)
            return
    
        # Otherwise after passing all test cases, modify old lab type 
        # Create empty list to store new lab type in
        labs = []
        # Check list of courses for lab
        for lab in course['labs']:
            if lab == old_type:
                labs.append(new_type)

            else: 
                labs.append(lab)

            course['labs'] = labs
            # Print log msg to user console stating lab type has been changed
            print("Lab " + old_type + " has been changed to " + new_type + " for course " + course_id)


    def delete_lab(self, course_id, lab_type):

    # Given I am in the CLI for the Scheduler program
    # When I type "Delete Lab"
    # Then I should be prompted to enter the course whose lab I want to delete
    # When I type in course and press enter
    # Then the course I entered should be saved with no lab in the database

        # Look through JSON file data for course data by ID input by user
        course = self.get_course_by_id(course_id)

        if course is None:
            print("Course with ID " + course_id + " does not exist.")
            return
        # If the course doesn't have a lab or labs DNE in list altogether,
        if 'labs' not in course or course['labs'] is None:
            # Throw error message to user console
            print("The course ID " + course_id + " has no labs to modify.")
            return
        # If the course ID specified by user does not have a lab type,
        if lab_type not in course['labs']:
            # Throw error message to user console
            print("Lab " + lab_type + " does not exist in " + course_id)
            return
    
        # Creates new list to store labs in excluding one that is deleted
        new_labs = []
        for lab in course['labs']:
            if lab != lab_type:
                new_labs.append(lab)

        # Assign Updated list of labs for courses excluding deleted lab
        course['labs'] = new_labs

        print("Lab " + lab_type + " has been deleted from course" + course_id)