# Author: Naomi E.
"""
Interfaces with main file to implement feature to add, modify, and delete
lab from a scheduler program

User Story: Adding, modifying, or deleting a lab from Scheduler CLI

“As a scheduler administrator, I want to add, modify, or delete a lab so 
that all labs available to schedule are up-to-date.”
"""
import json

class LabManager:

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
            print("The file " + filename + " is not a valid JSON file.")
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
    
        # Handle both direct and nested structure
        courses = self.data.get('courses') or self.data.get('config', {}).get('courses', [])
        if not courses:
            print("Data does not contain 'courses' list.")
            return None
    
        for course in courses:
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
            return False
    
        # If the course doesn't have a lab or lab DNE in list altogether,
        if 'lab' not in course or course['lab'] is None:
            # Create new empty list of lab for the courses to be stored in
            course['lab'] = []

        # If lab type being added to course already exists as a lab in the course,
        if lab_type in course['lab']:
            # Print error msg 
            print("Lab " + lab_type + " already exists in course " + course_id)
            return False

        # Once passed all test cases, can add lab to course
        course['lab'].append(lab_type)
        print("Lab " + lab_type + " has been added to course " + course_id)
        return True

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
            return False
        # If the course doesn't have a lab or lab DNE in list altogether,
        if 'lab' not in course or course['lab'] is None:
            # Throw error message to user console
            print("The course ID " + course_id + " has no lab to modify.")
            return False
        # If old type specified by user DNE in given course ID specified,
        if old_type not in course['lab']:
            # Throw error message to user console
            print("Lab " + old_type + " does not exist in " + course_id)
            return False
    
        # Otherwise after passing all test cases, modify old lab type 
        # Create empty list to store new lab type in
        labs = []
        # Check list of courses for lab
        for lab in course['lab']:
            if lab == old_type:
                labs.append(new_type)
            else: 
                labs.append(lab)

        course['lab'] = labs
        # Print log msg to user console stating lab type has been changed
        print("Lab " + old_type + " has been changed to " + new_type + " for course " + course_id)
        return True


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
            return False
        # If the course doesn't have a lab or lab DNE in list altogether,
        if 'lab' not in course or course['lab'] is None:
            # Throw error message to user console
            print("The course ID " + course_id + " has no lab to delete.")
            return False
        # If the course ID specified by user does not have a lab type,
        if lab_type not in course['lab']:
            # Throw error message to user console
            # old print ("Lab " + lab_type + " does not exist in " + course_id)
            print("no lab to delete")
            return False
    
        # Creates new list to store lab in excluding one that is deleted
        new_labs = []
        for lab in course['lab']:
            if lab != lab_type:
                new_labs.append(lab)

        # Assign Updated list of lab for courses excluding deleted lab
        course['lab'] = new_labs

        print("Lab " + lab_type + " has been deleted from course " + course_id)
        return True

    def display_labs_and_courses(self) -> None:
        """Display all labs and which courses use them."""
        print("\n" + "="*60)
        print("LAB USAGE SUMMARY")
        print("="*60)
        
        # Get all labs from the global labs list
        all_labs = self.data.get('config', {}).get('labs', [])
        courses = self.data.get('config', {}).get('courses', [])
        
        if not all_labs:
            print("No labs found in configuration.")
            return
        
        print(f"📍 Total Labs Available: {len(all_labs)}")
        print("-" * 60)
        
        for lab in all_labs:
            print(f"\n🔬 {lab}")
            
            # Find courses that use this lab
            courses_using_lab = []
            for course in courses:
                if 'lab' in course and isinstance(course.get('lab'), list):
                    if lab in course['lab']:
                        courses_using_lab.append(course.get('course_id', 'Unknown'))
            
            if courses_using_lab:
                print(f"   📚 Used by {len(courses_using_lab)} course(s):")
                for course_id in courses_using_lab:
                    print(f"      • {course_id}")
            else:
                print("   📭 No courses currently use this lab")
        
        print("="*60)

    def add_lab_to_course_interactive(self) -> None:
        """Interactive lab assignment to course."""
        print("\n➕ ADD LAB TO COURSE")
        print("=" * 30)
        
        # Show available courses
        courses = self.data.get('config', {}).get('courses', [])
        if not courses:
            print("❌ No courses found.")
            return
        
        print("Available courses:")
        course_ids = set()
        for course in courses:
            course_id = course.get('course_id')
            if course_id:
                course_ids.add(course_id)
        
        for i, course_id in enumerate(sorted(course_ids), 1):
            print(f"  {i}. {course_id}")
        
        course_id = input("\nEnter Course ID to add lab to: ").strip()
        if not course_id:
            print("❌ Course ID cannot be empty.")
            return
        
        # Check if course exists
        if not self.get_course_by_id(course_id):
            print(f"❌ Course '{course_id}' not found.")
            return
        
        # Show available labs
        all_labs = self.data.get('config', {}).get('labs', [])
        if not all_labs:
            print("❌ No labs available in configuration.")
            return
        
        print(f"\nAvailable labs:")
        for i, lab in enumerate(all_labs, 1):
            print(f"  {i}. {lab}")
        
        lab_type = input("\nEnter lab name to add: ").strip()
        if not lab_type:
            print("❌ Lab name cannot be empty.")
            return
        
        if lab_type not in all_labs:
            print(f"❌ Lab '{lab_type}' not found in available labs.")
            return
        
        try:
            result = self.add_lab(course_id, lab_type)
            if result:
                print(f"✅ Successfully added lab '{lab_type}' to course '{course_id}'")
            else:
                print(f"❌ Failed to add lab. Lab may already be assigned to this course.")
        except Exception as e:
            print(f"❌ Error adding lab: {e}")

    def modify_lab_interactive(self) -> None:
        """Interactive lab modification for courses."""
        self.display_labs_and_courses()
        
        course_id = input("\nEnter Course ID to modify lab for: ").strip()
        if not course_id:
            print("❌ Course ID cannot be empty.")
            return
        
        # Check if course exists
        course = self.get_course_by_id(course_id)
        if not course:
            print(f"❌ Course '{course_id}' not found.")
            return
        
        # Show current labs for this course
        current_labs = course.get('lab', [])
        if not current_labs:
            print(f"❌ Course '{course_id}' has no labs assigned.")
            return
        
        print(f"\nCurrent labs for {course_id}:")
        for i, lab in enumerate(current_labs, 1):
            print(f"  {i}. {lab}")
        
        old_lab = input("\nEnter current lab name to modify: ").strip()
        if not old_lab:
            print("❌ Lab name cannot be empty.")
            return
        
        if old_lab not in current_labs:
            print(f"❌ Lab '{old_lab}' is not assigned to course '{course_id}'.")
            return
        
        # Show available labs
        all_labs = self.data.get('config', {}).get('labs', [])
        print(f"\nAvailable labs:")
        for i, lab in enumerate(all_labs, 1):
            print(f"  {i}. {lab}")
        
        new_lab = input("\nEnter new lab name: ").strip()
        if not new_lab:
            print("❌ New lab name cannot be empty.")
            return
        
        if new_lab not in all_labs:
            print(f"❌ Lab '{new_lab}' not found in available labs.")
            return
        
        try:
            result = self.modify_lab(course_id, old_lab, new_lab)
            if result:
                print(f"✅ Successfully modified lab '{old_lab}' to '{new_lab}' for course '{course_id}'")
            else:
                print(f"❌ Failed to modify lab.")
        except Exception as e:
            print(f"❌ Error modifying lab: {e}")

    def delete_lab_interactive(self) -> None:
        """Interactive lab deletion from course."""
        self.display_labs_and_courses()
        
        course_id = input("\nEnter Course ID to remove lab from: ").strip()
        if not course_id:
            print("❌ Course ID cannot be empty.")
            return
        
        # Check if course exists
        course = self.get_course_by_id(course_id)
        if not course:
            print(f"❌ Course '{course_id}' not found.")
            return
        
        # Show current labs for this course
        current_labs = course.get('lab', [])
        if not current_labs:
            print(f"❌ Course '{course_id}' has no labs assigned.")
            return
        
        print(f"\nCurrent labs for {course_id}:")
        for i, lab in enumerate(current_labs, 1):
            print(f"  {i}. {lab}")
        
        lab_type = input("\nEnter lab name to remove: ").strip()
        if not lab_type:
            print("❌ Lab name cannot be empty.")
            return
        
        if lab_type not in current_labs:
            print(f"❌ Lab '{lab_type}' is not assigned to course '{course_id}'.")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to remove lab '{lab_type}' from course '{course_id}'? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Deletion cancelled.")
            return
        
        try:
            result = self.delete_lab(course_id, lab_type)
            if result:
                print(f"✅ Successfully removed lab '{lab_type}' from course '{course_id}'")
            else:
                print(f"❌ Failed to remove lab.")
        except Exception as e:
            print(f"❌ Error removing lab: {e}")

    def lab_management_menu(self, config_file: str, config: dict, time_slots: dict) -> dict:
        """Lab management menu interface."""
        try:
            self.load_data(config_file)
            
            if not self.data:
                print("❌ Error loading lab data. Please check the configuration file.")
                return config
            
            while True:
                print("\n" + "="*50)
                print("LAB MANAGEMENT")
                print("="*50)
                print("1. 👀 View labs and course assignments")
                print("2. ➕ Add lab to course")
                print("3. ✏️ Modify course lab assignment")
                print("4. ❌ Remove lab from course")
                print("5. 💾 Save changes and exit")
                print("6. 🚪 Exit without saving")
                print("="*50)
                
                choice = input("Select an option (1-6): ").strip()
                
                if choice == '1':
                    self.display_labs_and_courses()
                elif choice == '2':
                    self.add_lab_to_course_interactive()
                elif choice == '3':
                    self.modify_lab_interactive()
                elif choice == '4':
                    self.delete_lab_interactive()
                elif choice == '5':
                    # Save changes back to file
                    self.save_data()
                    # Update the config dictionary with the modified data
                    if 'config' in self.data:
                        config.update(self.data['config'])
                    else:
                        config.update(self.data)
                    print("✅ Lab changes saved successfully.")
                    return config
                elif choice == '6':
                    print("Exiting without saving changes.")
                    return config
                else:
                    print("Invalid choice. Please select 1-6.")
                    
        except Exception as e:
            print(f"❌ Error initializing lab manager: {e}")
            return config