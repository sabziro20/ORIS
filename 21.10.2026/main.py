import json
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

TASKS_FILE = Path(__file__).resolve().parent / "tasks.json"


def load_tasks():
    try:
        with open(TASKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Task Manager 2.0"))
        layout.addWidget(QLabel("Автор: Сабиров Амир, группа 11-521"))
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager 2.0")

        self.tasks = load_tasks()
        self.editing_index = None

        about_action = self.menuBar().addAction("О программе")
        about_action.triggered.connect(self.show_about)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)

        list_buttons = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_task)
        list_buttons.addWidget(self.edit_button)
        list_buttons.addWidget(self.delete_button)
        main_layout.addLayout(list_buttons)

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
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText("Medium")
        priority_layout.addWidget(self.priority_combo)
        main_layout.addLayout(priority_layout)

        self.important_checkbox = QCheckBox("Important")
        self.notification_checkbox = QCheckBox("Send notification")
        main_layout.addWidget(self.important_checkbox)
        main_layout.addWidget(self.notification_checkbox)

        self.create_button = QPushButton("Create task")
        self.create_button.clicked.connect(self.create_task)
        main_layout.addWidget(self.create_button)

        self.refresh_list()

    def refresh_list(self):
        self.task_list.clear()
        for task in self.tasks:
            self.task_list.addItem(f"[{task['priority']}] {task['title']}")

    def create_task(self):
        task = {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "priority": self.priority_combo.currentText(),
            "important": self.important_checkbox.isChecked(),
            "send_notification": self.notification_checkbox.isChecked(),
        }
        if self.editing_index is None:
            self.tasks.append(task)
        else:
            self.tasks[self.editing_index] = task
            self.editing_index = None
            self.create_button.setText("Create task")

        save_tasks(self.tasks)
        self.refresh_list()

        self.title_input.clear()
        self.description_input.clear()
        self.priority_combo.setCurrentText("Medium")
        self.important_checkbox.setChecked(False)
        self.notification_checkbox.setChecked(False)

    def edit_task(self):
        row = self.task_list.currentRow()
        if row < 0:
            return
        task = self.tasks[row]
        self.title_input.setText(task["title"])
        self.description_input.setPlainText(task["description"])
        self.priority_combo.setCurrentText(task["priority"])
        self.important_checkbox.setChecked(task["important"])
        self.notification_checkbox.setChecked(task["send_notification"])
        self.editing_index = row
        self.create_button.setText("Save changes")

    def delete_task(self):
        row = self.task_list.currentRow()
        if row < 0:
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить выбранную задачу?"
        )
        if answer == QMessageBox.StandardButton.Yes:
            del self.tasks[row]
            save_tasks(self.tasks)
            self.refresh_list()

    def show_about(self):
        AboutDialog(self).exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManagerWindow()
    window.show()
    sys.exit(app.exec())
