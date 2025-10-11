import sys

def print_header():
    print("=" * 40)
    print("        Faculty Management Menu        ")
    print("=" * 40)

def print_options():
    print("Please select an option:")
    print("  1. Edit Faculty")
    print("  2. Modify Faculty")
    print("  3. Delete Faculty")
    print("  4. Exit")
    print("-" * 40)

def get_user_choice():
    choice = input("Enter your choice (1-4): ").strip()
    return choice

def get_faculty_id(action):
    faculty_id = input(f"Enter Faculty ID to {action}: ").strip()
    return faculty_id

def get_faculty_details():
    name = input("Enter Faculty Name: ").strip()
    department = input("Enter Department: ").strip()
    email = input("Enter Email: ").strip()
    return {"name": name, "department": department, "email": email}

def show_message(message):
    print(f"\n{message}\n")

def faculty_view_entry():
    while True:
        print_header()
        print_options()
        choice = get_user_choice()

        if choice == "1":
            faculty_id = get_faculty_id("edit")
            details = get_faculty_details()
            # Pass faculty_id and details to controller
            show_message("Faculty edit request submitted.")
        elif choice == "2":
            faculty_id = get_faculty_id("modify")
            details = get_faculty_details()
            # Pass faculty_id and details to controller
            show_message("Faculty modify request submitted.")
        elif choice == "3":
            faculty_id = get_faculty_id("delete")
            # Pass faculty_id to controller
            show_message("Faculty delete request submitted.")
        elif choice == "4":
            print("Exiting Faculty Management. Goodbye!")
            break
        else:
            show_message("Invalid choice. Please try again.")

if __name__ == "__main__":
    faculty_view_entry()