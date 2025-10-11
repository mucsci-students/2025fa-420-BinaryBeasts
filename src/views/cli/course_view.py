import sys

def print_header(title):
    print("=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def show_menu():
    print_header("Faculty Management")
    print("Please choose an option:")
    print("1. Add Faculty")
    print("2. Edit Faculty")
    print("3. Delete Faculty")
    print("4. Exit")
    print("-" * 50)

def get_faculty_name():
    return input("Enter Faculty Name: ").strip()

def get_faculty_type():
    while True:
        ftype = input("Enter Faculty Type (full-time/adjunct): ").strip().lower()
        if ftype in ['full-time', 'adjunct']:
            return ftype
        print("Invalid type. Please enter 'full-time' or 'adjunct'.")

def get_course_limit(ftype):
    return 2 if ftype == 'full-time' else 1

def get_times():
    times = input("Enter available times (default 9-5): ").strip()
    return times if times else "9-5"

def get_preferences():
    prefs = []
    print("Enter course preferences (course name and preference 1-10). Type 'done' to finish.")
    while True:
        cname = input("Course name (or 'done'): ").strip()
        if cname.lower() == 'done':
            break
        pref = input("Preference (1-10): ").strip()
        if pref.isdigit() and 1 <= int(pref) <= 10:
            prefs.append((cname, int(pref)))
        else:
            print("Invalid preference. Enter a number from 1 to 10.")
    return prefs

def add_faculty_input():
    print_header("Add Faculty")
    name = get_faculty_name()
    ftype = get_faculty_type()
    limit = get_course_limit(ftype)
    times = get_times()
    prefs = get_preferences()
    return {
        'name': name,
        'type': ftype,
        'course_limit': limit,
        'times': times,
        'preferences': prefs
    }

def edit_faculty_input():
    print_header("Edit Faculty")
    name = get_faculty_name()
    print("What would you like to edit?")
    print("1. Type")
    print("2. Times")
    print("3. Preferences")
    choice = input("Enter choice (1-3): ").strip()
    if choice == '1':
        ftype = get_faculty_type()
        limit = get_course_limit(ftype)
        return name, {'type': ftype, 'course_limit': limit}
    elif choice == '2':
        times = get_times()
        return name, {'times': times}
    elif choice == '3':
        prefs = get_preferences()
        return name, {'preferences': prefs}
    else:
        print("Invalid choice.")
        return name, {}

def delete_faculty_input():
    print_header("Delete Faculty")
    name = get_faculty_name()
    confirm = input(f"Are you sure you want to delete faculty '{name}'? (y/n): ").strip().lower()
    return name, confirm == 'y'

def entry_point():
    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()
        if choice == '1':
            faculty = add_faculty_input()
            # Pass to controller
            print(f"Add requested: {faculty}")
        elif choice == '2':
            name, changes = edit_faculty_input()
            # Pass to controller
            print(f"Edit requested for faculty {name}: {changes}")
        elif choice == '3':
            name, confirmed = delete_faculty_input()
            if confirmed:
                # Pass to controller
                print(f"Delete requested for faculty {name}")
            else:
                print("Delete cancelled.")
        elif choice == '4':
            print("Exiting Faculty Management. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    entry_point()