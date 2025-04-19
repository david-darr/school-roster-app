# === File: models.py ===
# Contains Student, Roster, SubSchool, School classes

import re
import json
from PIL import Image
import pytesseract

class Student:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {"first_name": self.first_name, "last_name": self.last_name}

    @staticmethod
    def from_dict(data):
        return Student(data['first_name'], data['last_name'])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Roster:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def remove_student(self, student_name):
        self.students = [s for s in self.students if str(s) != student_name]

    def load_from_image(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or "first name" in line.lower() or "last name" in line.lower():
                continue
            if "|" in line:
                parts = [part.strip() for part in line.split("|")]
                if len(parts) == 2:
                    self.add_student(Student(parts[0].title(), parts[1].title()))
                    continue
            cleaned = re.sub(r'[^A-Za-z\s\-]', '', line).strip()
            parts = cleaned.split()
            if len(parts) >= 2:
                self.add_student(Student(parts[0].title(), ' '.join(parts[1:]).title()))

    def to_dict(self):
        return [s.to_dict() for s in self.students]

    @staticmethod
    def from_dict(data):
        roster = Roster()
        for student_data in data:
            roster.add_student(Student.from_dict(student_data))
        return roster

    def __str__(self):
        return "\n".join(f"{i+1}. {s}" for i, s in enumerate(self.students))


class SubSchool:
    def __init__(self, sport):
        self.sport = sport
        self.roster = Roster()
        self.schedule = {}  # date -> time

    def to_dict(self):
        return {
            "sport": self.sport,
            "roster": self.roster.to_dict(),
            "schedule": self.schedule
        }

    @staticmethod
    def from_dict(data):
        sub = SubSchool(data.get("sport", "General"))
        sub.roster = Roster.from_dict(data.get("roster", []))
        sub.schedule = data.get("schedule", {})
        return sub

    def __str__(self):
        return f"Session: {self.sport}\nSchedule: {self.schedule}\nRoster: {self.roster}"


class School:
    def __init__(self, name, address, phone_number):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.sub_schools = {}

    def add_sub_school(self, sport):
        if sport not in self.sub_schools:
            self.sub_schools[sport] = SubSchool(sport)

    def load_roster_from_image(self, image_path, sport):
        self.add_sub_school(sport)
        self.sub_schools[sport].roster.load_from_image(image_path)

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "phone_number": self.phone_number,
            "sub_schools": {sport: s.to_dict() for sport, s in self.sub_schools.items()}
        }

    @staticmethod
    def from_dict(data):
        school = School(data.get("name", ""), data.get("address", ""), data.get("phone_number", ""))
        for sport, sub_data in data.get("sub_schools", {}).items():
            school.sub_schools[sport] = SubSchool.from_dict(sub_data)
        return school

    def __str__(self):
        return f"{self.name}\n{self.address}\n{self.phone_number}"
