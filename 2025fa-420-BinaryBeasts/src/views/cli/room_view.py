import sys

def print_header():
    print("=" * 40)
    print(" " * 10 + "Room Manager")
    print("=" * 40)

def print_menu():
    print("\nPlease choose an option:")
    print("  1. Add Room")
    print("  2. Edit Room")
    print("  3. Delete Room")
    print("  4. List Rooms")
    print("  5. Quit")

def print_rooms(rooms):
    print("\nCurrent Rooms:")
    if not rooms:
        print("  (No rooms available)")
    else:
        for idx, room in enumerate(rooms, 1):
            print(f"  {idx}. {room}")

def main():
    rooms = []
    while True:
        print_header()
        print_rooms(rooms)
        print_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            name = input("Enter new room name: ").strip()
            if name:
                rooms.append(name)
                print(f"Room '{name}' added.")
        elif choice == "2":
            print_rooms(rooms)
            idx = input("Enter room number to edit: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(rooms):
                new_name = input("Enter new name for room: ").strip()
                if new_name:
                    rooms[int(idx)-1] = new_name
                    print("Room updated.")
            else:
                print("Invalid selection.")
        elif choice == "3":
            print_rooms(rooms)
            idx = input("Enter room number to delete: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(rooms):
                removed = rooms.pop(int(idx)-1)
                print(f"Room '{removed}' deleted.")
            else:
                print("Invalid selection.")
        elif choice == "4":
            print_rooms(rooms)
            input("\nPress Enter to continue...")
        elif choice == "5":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()