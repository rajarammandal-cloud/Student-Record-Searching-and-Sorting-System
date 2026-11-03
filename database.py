"""
database.py
-----------
Handles persistent data storage for the Student Record System using CSV files.
Provides automatic creation, safe loading, saving, and sample dataset seeding.
"""

import os
import csv
from typing import List, Dict, Any, Optional


class Database:
    """Manages reading and writing student records to a CSV file."""

    CSV_HEADER = ["Roll No", "Name", "Course", "Marks"]

    DEFAULT_SAMPLE_DATA = [
        {"roll_no": 101, "name": "Rahul", "course": "MCA", "marks": 85.0},
        {"roll_no": 102, "name": "Priya", "course": "MCA", "marks": 92.0},
        {"roll_no": 103, "name": "Aman", "course": "MCA", "marks": 75.0},
        {"roll_no": 104, "name": "Neha", "course": "MCA", "marks": 88.0},
        {"roll_no": 105, "name": "Rohit", "course": "MCA", "marks": 65.0},
        {"roll_no": 106, "name": "Anjali", "course": "MCA", "marks": 90.0},
        {"roll_no": 107, "name": "Karan", "course": "MCA", "marks": 78.0},
        {"roll_no": 108, "name": "Simran", "course": "MCA", "marks": 95.0},
        {"roll_no": 109, "name": "Arjun", "course": "MCA", "marks": 72.0},
        {"roll_no": 110, "name": "Pooja", "course": "MCA", "marks": 86.0},
    ]

    def __init__(self, filepath: Optional[str] = None):
        """Initialize database with a specified or default CSV path."""
        if filepath is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.filepath = os.path.join(base_dir, "students.csv")
        else:
            self.filepath = filepath
        self.ensure_file_exists()

    def ensure_file_exists(self) -> None:
        """Create the CSV file with headers if it does not exist."""
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADER)
                # Seed with default sample data on initial file creation
                for student in self.DEFAULT_SAMPLE_DATA:
                    writer.writerow([
                        student["roll_no"],
                        student["name"],
                        student["course"],
                        student["marks"]
                    ])

    def load_students(self) -> List[Dict[str, Any]]:
        """
        Load all student records from the CSV file.
        Returns a list of student dictionaries.
        """
        self.ensure_file_exists()
        records: List[Dict[str, Any]] = []

        try:
            with open(self.filepath, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)

                for row in reader:
                    if not row or len(row) < 4:
                        continue
                    try:
                        roll_no = int(row[0].strip())
                        name = row[1].strip()
                        course = row[2].strip()
                        marks = float(row[3].strip())
                        records.append({
                            "roll_no": roll_no,
                            "name": name,
                            "course": course,
                            "marks": marks
                        })
                    except (ValueError, IndexError):
                        # Skip malformed lines safely
                        continue
        except Exception as e:
            print(f"[Database Error] Could not read CSV file: {e}")

        return records

    def save_students(self, students: List[Dict[str, Any]]) -> bool:
        """
        Overwrite the CSV file with the updated list of students.
        Ensures atomicity and consistent formatting.
        """
        temp_filepath = self.filepath + ".tmp"
        try:
            with open(temp_filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADER)
                for s in students:
                    writer.writerow([
                        s["roll_no"],
                        s["name"],
                        s["course"],
                        f"{float(s['marks']):.1f}"
                    ])

            # Replace original file atomically
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(temp_filepath, self.filepath)
            return True
        except Exception as e:
            print(f"[Database Error] Could not save CSV file: {e}")
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass
            return False

    def load_sample_dataset(self, current_students: List[Dict[str, Any]]) -> int:
        """
        Append default sample records without duplicating existing roll numbers.
        Returns the count of newly added sample students.
        """
        existing_rolls = {s["roll_no"] for s in current_students}
        added_count = 0

        for sample in self.DEFAULT_SAMPLE_DATA:
            if sample["roll_no"] not in existing_rolls:
                current_students.append(dict(sample))
                existing_rolls.add(sample["roll_no"])
                added_count += 1

        if added_count > 0:
            self.save_students(current_students)

        return added_count
