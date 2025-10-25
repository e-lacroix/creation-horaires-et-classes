"""
Modèles de données pour le système de création d'horaires
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class CourseType(Enum):
    """Types de cours disponibles au secondaire québécois"""
    SCIENCE = "Science"
    STE = "STE"  # Sciences et technologies de l'environnement
    ASC = "ASC"  # Applications technologiques et scientifiques
    FRANCAIS = "Français"
    MATH_SN = "Math SN"  # Séquence Sciences Naturelles
    ANGLAIS = "Anglais"
    HISTOIRE = "Histoire"
    CCQ = "CCQ"  # Culture et citoyenneté québécoise
    ESPAGNOL = "Espagnol"
    EDUC = "Éducation physique"
    OPTION = "Option"


@dataclass
class Student:
    """Représente un étudiant"""
    id: int
    name: str
    grade: int  # Secondaire 1-5

    def __hash__(self):
        return hash(self.id)


@dataclass
class Teacher:
    """Représente un enseignant"""
    id: int
    name: str
    can_teach: List[CourseType]  # Cours que l'enseignant peut enseigner

    def __hash__(self):
        return hash(self.id)


@dataclass
class Classroom:
    """Représente une salle de classe"""
    id: int
    name: str
    capacity: int = 28

    def __hash__(self):
        return hash(self.id)


@dataclass
class Course:
    """Représente un cours spécifique"""
    id: int
    course_type: CourseType
    max_students: int = 28
    assigned_teacher: Optional[Teacher] = None
    assigned_room: Optional[Classroom] = None
    assigned_students: List[Student] = None

    def __post_init__(self):
        if self.assigned_students is None:
            self.assigned_students = []

    def __hash__(self):
        return hash(self.id)


@dataclass
class TimeSlot:
    """Représente une plage horaire"""
    day: int  # 1-9
    period: int  # 1-4

    def __str__(self):
        return f"Jour {self.day}, Période {self.period}"

    def __hash__(self):
        return hash((self.day, self.period))

    def __eq__(self, other):
        return self.day == other.day and self.period == other.period


@dataclass
class ScheduleAssignment:
    """Représente une assignation d'horaire"""
    course: Course
    timeslot: TimeSlot
