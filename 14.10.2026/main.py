import sys

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Task"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        main_layout.addLayout(title_layout)

        main_layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        main_layout.addWidget(self.description_input)

        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority"))
        self.low_priority_radio = QRadioButton("Low")
        self.medium_priority_radio = QRadioButton("Medium")
        self.high_priority_radio = QRadioButton("High")
        self.medium_priority_radio.setChecked(True)
        priority_layout.addWidget(self.low_priority_radio)
        priority_layout.addWidget(self.medium_priority_radio)
        priority_layout.addWidget(self.high_priority_radio)
        main_layout.addLayout(priority_layout)

        self.important_checkbox = QCheckBox("Important")
        self.notification_checkbox = QCheckBox("Send notification")
        main_layout.addWidget(self.important_checkbox)
        main_layout.addWidget(self.notification_checkbox)

        self.create_button = QPushButton("Create task")
        self.create_button.clicked.connect(self.create_task)
        main_layout.addWidget(self.create_button)

    def get_selected_priority(self):
        if self.low_priority_radio.isChecked():
            return "Low"
        if self.high_priority_radio.isChecked():
            return "High"
        return "Medium"

    def create_task(self):
        task = {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "priority": self.get_selected_priority(),
            "important": self.important_checkbox.isChecked(),
            "send_notification": self.notification_checkbox.isChecked(),
        }
        print("Task created:")
        for field_name, value in task.items():
            print(f"  {field_name}: {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManagerWindow()
    window.show()
    sys.exit(app.exec())