# src/views/cli/nl_view.py
"""
Natural Language View.
Handles user interaction for natural language commands.
"""


class NLView:
    """View layer for natural language command interface."""

    @staticmethod
    def display_welcome() -> None:
        """Display welcome message for natural language mode."""
        print("\n" + "="*60)
        print("💬 NATURAL LANGUAGE MODE")
        print("="*60)
        print("You can now use basic sentences to interact with the scheduler.")
        print("\nExamples:")
        print("  • 'Add a new course CMSC 201 with 4 credits'")
        print("  • 'Show all faculty members'")
        print("  • 'Delete the lab named Mac'")
        print("  • 'List all courses taught by Dr. Smith'")
        print("  • 'Exit' or 'Back' to return to main menu")
        print("="*60)

    @staticmethod
    def get_command() -> str:
        """
        Get natural language command from user.

        Returns:
            str: User's natural language command
        """
        return input("\n💬 You: ").strip()

    @staticmethod
    def display_parsing(command: str) -> None:
        """Display that command is being parsed."""
        print(f"🤔 Processing: '{command}'...")

    @staticmethod
    def display_confirmation(message: str) -> bool:
        """
        Display confirmation message and get user response.

        Args:
            message: Confirmation message to display

        Returns:
            bool: True if user confirms, False otherwise
        """
        print(f"\n✋ {message}")
        response = input("Confirm? (y/n): ").strip().lower()
        return response in ['y', 'yes']

    @staticmethod
    def display_result(result: dict) -> None:
        """
        Display the result of command execution.

        Args:
            result: Result dictionary from controller
                {
                    'success': bool,
                    'message': str,
                    'data': any
                }
        """
        if result.get('success'):
            print(result.get('message', 'Command executed successfully'))
        else:
            print(f"❌ {result.get('message', 'Command failed')}")

    @staticmethod
    def display_error(error_message: str) -> None:
        """Display error message."""
        print(f"❌ Error: {error_message}")

    @staticmethod
    def display_help() -> None:
        """Display help information for natural language mode."""
        print("\n" + "="*60)
        print("📖 AI HELP")
        print("="*60)
        print("\nSupported commands:")
        print("\nCourse Management:")
        print("  • Add course: 'Add CMSC 140 with 3 credits'")
        print("  • View courses: 'Show all courses' or 'List courses'")
        print("  • Delete course: 'Remove course CMSC 140'")
        print("\nFaculty Management:")
        print("  • Add faculty: 'Add faculty Dr. Smith'")
        print("  • View faculty: 'Show all faculty' or 'List professors'")
        print("  • Delete faculty: 'Remove Dr. Smith'")
        print("\nLab Management:")
        print("  • Add lab: 'Add a lab named Linux'")
        print("  • View labs: 'Show all labs'")
        print("  • Delete lab: 'Remove the Mac lab'")
        print("\nRoom Management:")
        print("  • Add room: 'Add room Roddy 147'")
        print("  • View rooms: 'List all rooms'")
        print("  • Delete room: 'Remove room Roddy 101'")
        print("\nGeneral:")
        print("  • Help: 'help' or 'what can you do?'")
        print("  • Exit: 'exit', 'back', or 'quit'")
        print("="*60)

    @staticmethod
    def run_nl_mode(controller) -> None:
        """
        Run the natural language interaction loop.

        Args:
            controller: NLController instance
        """
        NLView.display_welcome()

        while True:
            try:
                # Get user command
                command = NLView.get_command()

                # Check for exit commands
                if command.lower() in ['exit', 'quit', 'back', 'q']:
                    print("👋 Returning to main menu...")
                    break

                # Check for help
                if command.lower() in ['help', 'what can you do?', 'what can you do']:
                    NLView.display_help()
                    continue

                # Skip empty commands
                if not command:
                    continue

                # Process command
                NLView.display_parsing(command)
                result = controller.process_command(command)
                NLView.display_result(result)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Returning to main menu...")
                break
            except Exception as e:
                NLView.display_error(str(e))