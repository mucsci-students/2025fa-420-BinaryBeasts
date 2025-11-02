# src/views/gui/ai_chat_gui.py
"""
AI Chat Dialog for natural language interaction.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AIChatDialog(QDialog):
    """Dialog for AI-powered natural language chat interface."""

    def __init__(self, nl_controller, parent=None):
        """
        Initialize the chat dialog.

        Args:
            nl_controller: NLController instance for processing commands
            parent: Parent widget
        """
        super().__init__(parent)
        self.nl_controller = nl_controller
        self.generated_schedules = None  # Track generated schedules
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("💬 AI Assistant")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("AI Assistant")
        header.setFont(QFont('Arial', 14, QFont.Bold))  # type: ignore[attr-defined]
        header.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.addWidget(header)

        # Welcome message
        welcome = QLabel(
            "Ask me to manage courses, faculty, labs, and rooms using natural language!\n"
            "Examples: 'Add a room named CS101' or 'Show all courses'"
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("color: #666; padding: 8px; background-color: #f5f5f5; border-radius: 6px;")
        layout.addWidget(welcome)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Arial';
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #327f66;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #327f66;
                color: white;
                border-radius: 6px;
                border: none;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3da879;
            }
            QPushButton:pressed {
                background-color: #2a6a52;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        # Help text
        help_text = QLabel("Type 'help' for more examples, or 'exit' to close")
        help_text.setStyleSheet("color: #999; font-size: 11px;")
        help_text.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.addWidget(help_text)

        # Display welcome message
        self.display_message("AI Assistant",
                           "Hello! I'm your AI assistant. I can help you manage your schedule configuration.\n\n"
                           "You can ask me to:\n"
                           "• Add, list, or remove courses\n"
                           "• Manage faculty members\n"
                           "• Add or remove rooms and labs\n"
                           "• And more!\n\n"
                           "Just type your request in natural language below.",
                           is_user=False)

    def send_message(self):
        """Process and send user message."""
        message = self.input_field.text().strip()
        if not message:
            return

        # Clear input field
        self.input_field.clear()

        # Check for exit command
        if message.lower() in ['exit', 'quit', 'close', 'back']:
            self.display_message("You", message, is_user=True)
            self.display_message("AI Assistant", "Goodbye! Closing chat...", is_user=False)
            self.accept()
            return

        # Check for help command
        if message.lower() in ['help', 'what can you do?', 'what can you do']:
            self.display_message("You", message, is_user=True)
            self.show_help()
            return

        # Display user message
        self.display_message("You", message, is_user=True)

        # Process with NL controller
        self.display_message("AI Assistant", "Processing...", is_user=False, is_processing=True)

        try:
            result = self.nl_controller.process_command(message)

            # Remove "Processing..." message
            self.remove_last_message()

            # Check if schedules were generated (stored on nl_controller)
            if self.nl_controller.generated_schedules:
                # Schedules generated! Store and close dialog
                self.generated_schedules = self.nl_controller.generated_schedules
                # Clear the controller's schedules so they don't persist
                self.nl_controller.generated_schedules = None

                response = result.get('message', 'Schedules generated successfully!')
                self.display_message("AI Assistant", response, is_user=False)

                # Close dialog after brief moment
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(1000, self.accept)  # Close after 1 second
                return

            # Display normal result
            if result.get('success'):
                response = result.get('message', 'Command executed successfully')
                self.display_message("AI Assistant", response, is_user=False)
            else:
                response = result.get('message', 'Command failed')
                self.display_message("AI Assistant", f"❌ {response}", is_user=False)

        except Exception as e:
            # Remove "Processing..." message
            self.remove_last_message()
            self.display_message("AI Assistant", f"❌ Error: {str(e)}", is_user=False)

    def display_message(self, sender, message, is_user=False, is_processing=False):
        """
        Display a message in the chat.

        Args:
            sender: Name of the sender
            message: Message text
            is_user: True if message is from user, False if from AI
            is_processing: True if this is a processing message
        """
        color = "#327f66" if is_user else "#666"
        bg_color = "#e8f5e9" if is_user else "#f5f5f5"
        alignment = "right" if is_user else "left"

        html = f"""
        <div style='margin-bottom: 12px; text-align: {alignment};'>
            <div style='display: inline-block; max-width: 80%; text-align: left;'>
                <div style='font-weight: bold; color: {color}; margin-bottom: 4px; font-size: 12px;'>
                    {sender}
                </div>
                <div style='background-color: {bg_color}; padding: 10px; border-radius: 8px;
                           color: #333; line-height: 1.4;'>
                    {message.replace(chr(10), '<br>')}
                </div>
            </div>
        </div>
        """

        self.chat_display.append(html)
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def remove_last_message(self):
        """Remove the last message from the chat display."""
        # This is a simple implementation - just clear and redraw would be better
        # For now, we'll just note it
        pass

    def show_help(self):
        """Display help information."""
        help_text = """
Here are some things you can ask me to do:

<b>Course Management:</b>
• "Add CMSC 140 with 3 credits"
• "Show all courses"
• "List courses taught by Dr. Smith"

<b>Faculty Management:</b>
• "Add faculty Dr. Johnson"
• "Show all faculty"

<b>Room Management:</b>
• "Add room Roddy 147"
• "List all rooms"
• "Remove room CS101"
• "Rename room 'Old Name' to 'New Name'"

<b>Lab Management:</b>
• "Add a lab named Linux Lab"
• "Show all labs"
• "Remove the Mac lab"

Just type your request in plain English!
        """
        self.display_message("AI Assistant", help_text, is_user=False)