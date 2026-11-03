"""
student_manager.py
------------------
Manages student records, input validations, CRUD business logic,
and real-time statistical calculations for the dashboard.
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple

# Ensure local imports resolve whether executed directly or as a package
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import Database


class Student:
    """Represents a single student entity with field-level validations."""

    def __init__(self, roll_no: int, name: str, course: str, marks: float):
        self.roll_no = roll_no
        self.name = name
        self.course = course
        self.marks = marks

    def to_dict(self) -> Dict[str, Any]:
        """Convert student object to a standard dictionary."""
        return {
            "roll_no": self.roll_no,
            "name": self.name,
            "course": self.course,
            "marks": self.marks
        }

    @staticmethod
    def validate_fields(roll_no_raw: Any, name_raw: str, course_raw: str, marks_raw: Any) -> Tuple[int, str, str, float]:
        """
        Validate all inputs strictly:
        - Roll Number: positive integer
        - Name: non-empty string
        - Course: non-empty string
        - Marks: float between 0 and 100
        Raises ValueError with clear message on invalid input.
        """
        # Validate Roll Number
        try:
            roll_no = int(str(roll_no_raw).strip())
            if roll_no <= 0:
                raise ValueError("Roll Number must be a positive integer greater than 0.")
        except (ValueError, TypeError):
            raise ValueError("Roll Number must be a valid positive integer.")

        # Validate Name
        name = str(name_raw).strip()
        if not name:
            raise ValueError("Student Name cannot be empty.")
        if any(char.isdigit() for char in name):
            raise ValueError("Student Name should not contain numbers.")

        # Validate Course
        course = str(course_raw).strip()
        if not course:
            raise ValueError("Course field cannot be empty.")

        # Validate Marks
        try:
            marks = float(str(marks_raw).strip())
            if not (0.0 <= marks <= 100.0):
                raise ValueError("Marks must be between 0.0 and 100.0.")
        except (ValueError, TypeError):
            raise ValueError("Marks must be a valid numerical value between 0 and 100.")

        return roll_no, name, course, marks


class StudentManager:
    """Provides complete CRUD operations, persistence link, and KPI calculations."""

    def __init__(self, database: Optional[Database] = None):
        self.db = database if database is not None else Database()
        self.students: List[Dict[str, Any]] = []
        self.refresh()

    def refresh(self) -> None:
        """Reload student records from the CSV file."""
        self.students = self.db.load_students()

    def get_all(self) -> List[Dict[str, Any]]:
        """Return a copy of all student records."""
        return [dict(s) for s in self.students]

    def get_by_roll(self, roll_no: int) -> Optional[Dict[str, Any]]:
        """Find a single student record by roll number."""
        for s in self.students:
            if s["roll_no"] == roll_no:
                return dict(s)
        return None

    def exists(self, roll_no: int) -> bool:
        """Check if a roll number already exists."""
        return any(s["roll_no"] == roll_no for s in self.students)

    def add_student(self, roll_no_raw: Any, name_raw: str, course_raw: str, marks_raw: Any) -> Dict[str, Any]:
        """
        Validate and insert a new student record.
        Prevents duplicate roll numbers.
        """
        roll_no, name, course, marks = Student.validate_fields(roll_no_raw, name_raw, course_raw, marks_raw)

        if self.exists(roll_no):
            raise ValueError(f"Student with Roll Number {roll_no} already exists! Roll numbers must be unique.")

        new_student = {
            "roll_no": roll_no,
            "name": name,
            "course": course,
            "marks": marks
        }

        self.students.append(new_student)
        self.db.save_students(self.students)
        return new_student

    def update_student(self, roll_no: int, name_raw: str, course_raw: str, marks_raw: Any) -> Dict[str, Any]:
        """
        Update an existing student's name, course, and marks.
        Preserves the existing roll number.
        """
        if not self.exists(roll_no):
            raise ValueError(f"Student with Roll Number {roll_no} does not exist.")

        # Validate remaining fields
        name = str(name_raw).strip()
        if not name:
            raise ValueError("Student Name cannot be empty.")
        if any(char.isdigit() for char in name):
            raise ValueError("Student Name should not contain numbers.")

        course = str(course_raw).strip()
        if not course:
            raise ValueError("Course field cannot be empty.")

        try:
            marks = float(str(marks_raw).strip())
            if not (0.0 <= marks <= 100.0):
                raise ValueError("Marks must be between 0.0 and 100.0.")
        except (ValueError, TypeError):
            raise ValueError("Marks must be a valid numerical value between 0 and 100.")

        for s in self.students:
            if s["roll_no"] == roll_no:
                s["name"] = name
                s["course"] = course
                s["marks"] = marks
                self.db.save_students(self.students)
                return dict(s)

        raise ValueError(f"Student with Roll Number {roll_no} could not be updated.")

    def delete_student(self, roll_no: int) -> bool:
        """Delete student record with the specified roll number."""
        initial_len = len(self.students)
        self.students = [s for s in self.students if s["roll_no"] != roll_no]

        if len(self.students) < initial_len:
            self.db.save_students(self.students)
            return True
        return False

    def load_sample_data(self) -> int:
        """Load default sample dataset without duplicating existing records."""
        added = self.db.load_sample_dataset(self.students)
        self.refresh()
        return added

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Compute summary statistics for the dashboard cards."""
        if not self.students:
            return {
                "total_students": 0,
                "average_marks": 0.0,
                "highest_marks": 0.0,
                "highest_student": "N/A",
                "lowest_marks": 0.0,
                "lowest_student": "N/A"
            }

        total = len(self.students)
        marks_list = [s["marks"] for s in self.students]
        avg_marks = sum(marks_list) / total

        highest_record = max(self.students, key=lambda s: s["marks"])
        lowest_record = min(self.students, key=lambda s: s["marks"])

        return {
            "total_students": total,
            "average_marks": round(avg_marks, 2),
            "highest_marks": highest_record["marks"],
            "highest_student": f"{highest_record['name']} (Roll: {highest_record['roll_no']})",
            "lowest_marks": lowest_record["marks"],
            "lowest_student": f"{lowest_record['name']} (Roll: {lowest_record['roll_no']})"
        }
