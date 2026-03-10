"""
Task Manager (console application)

A simple interactive, file-backed task manager designed for running in a terminal
(or inside a Docker container with `docker run -it ...`).

Data files:
- user.txt  : stores users as "username;password"
- tasks.txt : stores tasks as CSV rows:
              username,title,description,due_date,assigned_date,completed
Dates use ISO format: YYYY-MM-DD
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date, datetime
from getpass import getpass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "user.txt"
TASKS_FILE = BASE_DIR / "tasks.txt"

DATE_FMT = "%Y-%m-%d"


@dataclass
class Task:
    username: str
    title: str
    description: str
    due_date: date
    assigned_date: date
    completed: bool

    @staticmethod
    def from_row(row: List[str]) -> "Task":
        # Expected: username,title,description,due_date,assigned_date,completed
        if len(row) < 6:
            raise ValueError("Invalid task row (expected 6 columns).")
        return Task(
            username=row[0].strip(),
            title=row[1].strip(),
            description=row[2].strip(),
            due_date=parse_date(row[3].strip()),
            assigned_date=parse_date(row[4].strip()),
            completed=row[5].strip().lower() in ("yes", "true", "1", "y"),
        )

    def to_row(self) -> List[str]:
        return [
            self.username,
            self.title,
            self.description,
            self.due_date.strftime(DATE_FMT),
            self.assigned_date.strftime(DATE_FMT),
            "Yes" if self.completed else "No",
        ]


def ensure_data_files() -> None:
    """Ensure user.txt and tasks.txt exist with sensible defaults."""
    if not USERS_FILE.exists():
        USERS_FILE.write_text("admin;password\n", encoding="utf-8")
    if not TASKS_FILE.exists():
        # empty tasks file is fine
        TASKS_FILE.write_text("", encoding="utf-8")


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, DATE_FMT).date()
    except ValueError as e:
        raise ValueError(f"Date must be in YYYY-MM-DD format (got: {value}).") from e


def load_users() -> Dict[str, str]:
    users: Dict[str, str] = {}
    if not USERS_FILE.exists():
        return users
    for line in USERS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if ";" not in line:
            continue
        username, password = line.split(";", 1)
        users[username.strip()] = password.strip()
    return users


def save_user(username: str, password: str) -> None:
    with USERS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{username};{password}\n")


def load_tasks() -> List[Task]:
    tasks: List[Task] = []
    if not TASKS_FILE.exists():
        return tasks
    with TASKS_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            tasks.append(Task.from_row(row))
    return tasks


def save_tasks(tasks: List[Task]) -> None:
    with TASKS_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for t in tasks:
            writer.writerow(t.to_row())


def prompt_choice(prompt: str, valid: Tuple[str, ...]) -> str:
    valid_lower = tuple(v.lower() for v in valid)
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_lower:
            return choice
        print(f"Invalid option. Choose one of: {', '.join(valid)}")


def login(users: Dict[str, str]) -> str:
    print("\n=== Login ===")
    while True:
        username = input("Username: ").strip()
        password = getpass("Password: ").strip()
        if username in users and users[username] == password:
            print("Login successful.\n")
            return username
        print("Incorrect username or password. Try again.\n")


def register_user(users: Dict[str, str]) -> None:
    print("\n=== Register User ===")
    while True:
        new_username = input("New username: ").strip()
        if not new_username:
            print("Username cannot be empty.")
            continue
        if new_username in users:
            print("That username already exists. Choose another.")
            continue
        new_password = getpass("New password: ").strip()
        confirm = getpass("Confirm password: ").strip()
        if new_password != confirm:
            print("Passwords do not match. Try again.")
            continue
        if not new_password:
            print("Password cannot be empty.")
            continue
        users[new_username] = new_password
        save_user(new_username, new_password)
        print(f"User '{new_username}' registered.\n")
        return


def add_task(tasks: List[Task], users: Dict[str, str]) -> None:
    print("\n=== Add Task ===")
    while True:
        username = input("Assign to username: ").strip()
        if username not in users:
            print("User does not exist. Try again.")
            continue
        break

    title = input("Title: ").strip()
    description = input("Description: ").strip()

    while True:
        due_str = input("Due date (YYYY-MM-DD): ").strip()
        try:
            due = parse_date(due_str)
            break
        except ValueError as e:
            print(e)

    t = Task(
        username=username,
        title=title,
        description=description,
        due_date=due,
        assigned_date=date.today(),
        completed=False,
    )
    tasks.append(t)
    save_tasks(tasks)
    print("Task added.\n")


def format_task(task: Task, idx: Optional[int] = None) -> str:
    header = f"Task {idx}" if idx is not None else "Task"
    return (
        f"{header}\n"
        f"Assigned to: {task.username}\n"
        f"Title      : {task.title}\n"
        f"Description: {task.description}\n"
        f"Assigned   : {task.assigned_date.strftime(DATE_FMT)}\n"
        f"Due        : {task.due_date.strftime(DATE_FMT)}\n"
        f"Completed  : {'Yes' if task.completed else 'No'}\n"
    )


def view_all(tasks: List[Task]) -> None:
    print("\n=== View All Tasks ===")
    if not tasks:
        print("No tasks found.\n")
        return
    for i, t in enumerate(tasks, start=1):
        print(format_task(t, i))
    print()


def view_mine(tasks: List[Task], current_user: str) -> None:
    print("\n=== View My Tasks ===")
    my = [(i, t) for i, t in enumerate(tasks) if t.username == current_user]
    if not my:
        print("You have no tasks.\n")
        return

    for display_idx, (real_idx, t) in enumerate(my, start=1):
        print(format_task(t, display_idx))

    # Optional edit/mark complete
    print("Options:")
    print("- Enter a task number to edit/mark complete")
    print("- Enter -1 to return to the menu")
    while True:
        raw = input("Choice: ").strip()
        if raw == "-1":
            print()
            return
        if not raw.isdigit():
            print("Enter a number or -1.")
            continue
        pick = int(raw)
        if pick < 1 or pick > len(my):
            print("Invalid task number.")
            continue
        real_idx, task = my[pick - 1]
        edit_task(tasks, real_idx)
        save_tasks(tasks)
        print("Task updated.\n")
        return


def edit_task(tasks: List[Task], idx: int) -> None:
    task = tasks[idx]
    if task.completed:
        print("This task is already completed and cannot be edited.")
        return

    print("\nEdit options:")
    print("1) Mark as completed")
    print("2) Change due date")
    print("3) Change assigned user")
    choice = prompt_choice("Select (1/2/3): ", ("1", "2", "3"))

    if choice == "1":
        task.completed = True
        tasks[idx] = task
        return

    if choice == "2":
        while True:
            due_str = input("New due date (YYYY-MM-DD): ").strip()
            try:
                task.due_date = parse_date(due_str)
                tasks[idx] = task
                return
            except ValueError as e:
                print(e)

    if choice == "3":
        new_user = input("New assigned username: ").strip()
        if new_user:
            task.username = new_user
            tasks[idx] = task
        else:
            print("Username cannot be empty.")


def main() -> None:
    ensure_data_files()
    users = load_users()
    tasks = load_tasks()

    current_user = login(users)

    while True:
        print("=== Menu ===")
        print("r  - register user (admin only)")
        print("a  - add task")
        print("va - view all tasks")
        print("vm - view my tasks")
        print("e  - exit")
        choice = input("Select: ").strip().lower()

        if choice == "r":
            if current_user != "admin":
                print("Only admin can register users.\n")
            else:
                register_user(users)
        elif choice == "a":
            add_task(tasks, users)
            tasks = load_tasks()  # refresh
        elif choice == "va":
            view_all(tasks)
        elif choice == "vm":
            view_mine(tasks, current_user)
            tasks = load_tasks()  # refresh
        elif choice == "e":
            print("Goodbye.")
            break
        else:
            print("Invalid selection.\n")


if __name__ == "__main__":
    main()
