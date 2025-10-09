import sys

def print_header(title):
    print("=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def show_lab_menu():
    print_header("Lab Management")
    print("Please choose an option:")
    print("1. Edit Lab")
    print("2. Modify Lab")
    print("3. Delete Lab")
    print("4. Exit")
    print("-" * 50)

def get_lab_id():
    lab_id = input("Enter Lab ID: ").strip()
    return lab_id

def edit_lab_view():
    print_header("Edit Lab")
    lab_id = get_lab_id()
    print(f"Editing Lab {lab_id}...")
    # Controller will handle actual logic

def modify_lab_view():
    print_header("Modify Lab")
    lab_id = get_lab_id()
    print(f"Modifying Lab {lab_id}...")
    # Controller will handle actual logic

def delete_lab_view():
    print_header("Delete Lab")
    lab_id = get_lab_id()
    print(f"Deleting Lab {lab_id}...")
    # Controller will handle actual logic

def main():
    while True:
        show_lab_menu()
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            edit_lab_view()
        elif choice == "2":
            modify_lab_view()
        elif choice == "3":
            delete_lab_view()
        elif choice == "4":
            print("Exiting Lab Management. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()