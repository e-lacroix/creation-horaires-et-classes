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
    MATH_CST = "Math CST"  # Séquence Culture, Société et Technique
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
    preferred_classroom: Optional['Classroom'] = None  # Salle préférée de l'enseignant

    def __hash__(self):
        return hash(self.id)


@dataclass
class Classroom:
    """Représente une salle de classe"""
    id: int
    name: str
    capacity: int = 32
    allowed_subjects: Optional[List[CourseType]] = None  # Matières autorisées dans cette salle (None = toutes)

    def __post_init__(self):
        if self.allowed_subjects is None:
            # Par défaut, toutes les matières sont autorisées
            self.allowed_subjects = list(CourseType)

    def __hash__(self):
        return hash(self.id)


@dataclass
class Course:
    """Représente un cours spécifique"""
    id: int
    course_type: CourseType
    max_students: int = 32
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
class CourseSession:
    """Représente une session de cours (regroupement d'étudiants au même moment)"""
    id: int
    course_type: CourseType
    timeslot: TimeSlot
    assigned_teacher: Optional[Teacher] = None
    assigned_room: Optional[Classroom] = None
    students: List[Student] = None

    def __post_init__(self):
        if self.students is None:
            self.students = []

    def __hash__(self):
        return hash(self.id)


@dataclass
class StudentScheduleEntry:
    """Représente une entrée dans l'horaire d'un étudiant"""
    course_type: CourseType
    timeslot: TimeSlot
    session: Optional['CourseSession'] = None


@dataclass
class ScheduleAssignment:
    """Représente une assignation d'horaire (pour rétrocompatibilité)"""
    course: Course
    timeslot: TimeSlot
