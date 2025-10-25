"""
Optimiseur d'horaires utilisant Google OR-Tools
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
from models import Course, TimeSlot, Teacher, Classroom, Student, ScheduleAssignment
import random


class ScheduleOptimizer:
    """Optimise l'attribution des cours aux plages horaires, enseignants et salles"""

    def __init__(self, courses: List[Course], teachers: List[Teacher],
                 classrooms: List[Classroom], students: List[Student]):
        self.courses = courses
        self.teachers = teachers
        self.classrooms = classrooms
        self.students = students
        self.model = cp_model.CpModel()
        self.timeslots = [TimeSlot(day=d, period=p) for d in range(1, 10) for p in range(1, 5)]

        # Variables de décision
        self.course_to_timeslot = {}
        self.course_to_teacher = {}
        self.course_to_room = {}
        self.student_to_course = {}

    def create_variables(self):
        """Crée les variables de décision pour le modèle"""
        # Pour chaque cours, assigner un créneau horaire
        for course in self.courses:
            self.course_to_timeslot[course.id] = {}
            for timeslot in self.timeslots:
                var_name = f'course_{course.id}_timeslot_{timeslot.day}_{timeslot.period}'
                self.course_to_timeslot[course.id][timeslot] = self.model.NewBoolVar(var_name)

        # Pour chaque cours, assigner un enseignant
        for course in self.courses:
            self.course_to_teacher[course.id] = {}
            for teacher in self.teachers:
                if course.course_type in teacher.can_teach:
                    var_name = f'course_{course.id}_teacher_{teacher.id}'
                    self.course_to_teacher[course.id][teacher.id] = self.model.NewBoolVar(var_name)

        # Pour chaque cours, assigner une salle
        for course in self.courses:
            self.course_to_room[course.id] = {}
            for room in self.classrooms:
                var_name = f'course_{course.id}_room_{room.id}'
                self.course_to_room[course.id][room.id] = self.model.NewBoolVar(var_name)

        # Pour chaque étudiant et cours, assigner ou non
        for student in self.students:
            self.student_to_course[student.id] = {}
            for course in self.courses:
                var_name = f'student_{student.id}_course_{course.id}'
                self.student_to_course[student.id][course.id] = self.model.NewBoolVar(var_name)

    def add_constraints(self):
        """Ajoute les contraintes au modèle"""
        # Contrainte 1: Chaque cours doit être assigné à exactement un créneau
        for course in self.courses:
            self.model.AddExactlyOne(
                [self.course_to_timeslot[course.id][ts] for ts in self.timeslots]
            )

        # Contrainte 2: Chaque cours doit avoir exactement un enseignant
        for course in self.courses:
            if self.course_to_teacher[course.id]:
                self.model.AddExactlyOne(
                    [self.course_to_teacher[course.id][teacher_id]
                     for teacher_id in self.course_to_teacher[course.id]]
                )

        # Contrainte 3: Chaque cours doit avoir exactement une salle
        for course in self.courses:
            self.model.AddExactlyOne(
                [self.course_to_room[course.id][room_id]
                 for room_id in self.course_to_room[course.id]]
            )

        # Contrainte 4: Un enseignant ne peut enseigner qu'un cours à la fois
        for teacher in self.teachers:
            for timeslot in self.timeslots:
                courses_for_teacher = []
                for course in self.courses:
                    if teacher.id in self.course_to_teacher[course.id]:
                        # Ce cours est au créneau ET assigné à ce prof
                        course_at_time_with_teacher = self.model.NewBoolVar(
                            f'teacher_{teacher.id}_busy_{timeslot.day}_{timeslot.period}_course_{course.id}'
                        )
                        self.model.AddMultiplicationEquality(
                            course_at_time_with_teacher,
                            [self.course_to_timeslot[course.id][timeslot],
                             self.course_to_teacher[course.id][teacher.id]]
                        )
                        courses_for_teacher.append(course_at_time_with_teacher)

                if courses_for_teacher:
                    self.model.Add(sum(courses_for_teacher) <= 1)

        # Contrainte 5: Une salle ne peut être utilisée qu'une fois par créneau
        for room in self.classrooms:
            for timeslot in self.timeslots:
                courses_in_room = []
                for course in self.courses:
                    course_at_time_in_room = self.model.NewBoolVar(
                        f'room_{room.id}_used_{timeslot.day}_{timeslot.period}_course_{course.id}'
                    )
                    self.model.AddMultiplicationEquality(
                        course_at_time_in_room,
                        [self.course_to_timeslot[course.id][timeslot],
                         self.course_to_room[course.id][room.id]]
                    )
                    courses_in_room.append(course_at_time_in_room)

                self.model.Add(sum(courses_in_room) <= 1)

        # Contrainte 6: Un étudiant ne peut suivre qu'un cours à la fois
        for student in self.students:
            for timeslot in self.timeslots:
                courses_for_student = []
                for course in self.courses:
                    student_in_course_at_time = self.model.NewBoolVar(
                        f'student_{student.id}_at_{timeslot.day}_{timeslot.period}_course_{course.id}'
                    )
                    self.model.AddMultiplicationEquality(
                        student_in_course_at_time,
                        [self.course_to_timeslot[course.id][timeslot],
                         self.student_to_course[student.id][course.id]]
                    )
                    courses_for_student.append(student_in_course_at_time)

                self.model.Add(sum(courses_for_student) <= 1)

        # Contrainte 7: Maximum 28 étudiants par cours
        for course in self.courses:
            students_in_course = [
                self.student_to_course[student.id][course.id]
                for student in self.students
            ]
            self.model.Add(sum(students_in_course) <= course.max_students)

        # Contrainte 8: Chaque étudiant doit suivre tous les types de cours requis
        # Pour simplifier, on assure que chaque étudiant suit au moins un cours de chaque type
        course_types_needed = {}
        for course in self.courses:
            if course.course_type not in course_types_needed:
                course_types_needed[course.course_type] = []
            course_types_needed[course.course_type].append(course)

        for student in self.students:
            for course_type, courses_of_type in course_types_needed.items():
                # Chaque étudiant doit suivre au moins 1 cours de ce type
                courses_of_this_type = [
                    self.student_to_course[student.id][course.id]
                    for course in courses_of_type
                ]
                self.model.Add(sum(courses_of_this_type) >= 1)

    def add_optimization_objectives(self):
        """Ajoute des objectifs d'optimisation"""
        # Objectif: Équilibrer le nombre d'étudiants par cours
        variance_terms = []
        for course in self.courses:
            num_students = sum(
                self.student_to_course[student.id][course.id]
                for student in self.students
            )
            # On veut que chaque cours ait environ 75/38 ≈ 2 étudiants
            # mais comme certains cours doivent être suivis par plus d'étudiants,
            # on minimise simplement la variance
            variance_terms.append(num_students)

        # Minimiser l'utilisation de salles différentes (préférer réutiliser)
        room_usage = []
        for room in self.classrooms:
            room_used = self.model.NewBoolVar(f'room_{room.id}_used')
            for course in self.courses:
                self.model.Add(room_used >= self.course_to_room[course.id][room.id])
            room_usage.append(room_used)

        # Objectif combiné: maximiser l'équilibre et minimiser les salles
        self.model.Minimize(sum(room_usage))

    def solve(self) -> Tuple[bool, List[ScheduleAssignment]]:
        """Résout le problème d'optimisation"""
        self.create_variables()
        self.add_constraints()
        self.add_optimization_objectives()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        solver.parameters.num_search_workers = 8

        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            assignments = self.extract_solution(solver)
            return True, assignments
        else:
            return False, []

    def extract_solution(self, solver: cp_model.CpSolver) -> List[ScheduleAssignment]:
        """Extrait la solution du solveur"""
        assignments = []

        for course in self.courses:
            # Trouver le créneau assigné
            assigned_timeslot = None
            for timeslot in self.timeslots:
                if solver.Value(self.course_to_timeslot[course.id][timeslot]):
                    assigned_timeslot = timeslot
                    break

            # Trouver l'enseignant assigné
            assigned_teacher = None
            for teacher in self.teachers:
                if teacher.id in self.course_to_teacher[course.id]:
                    if solver.Value(self.course_to_teacher[course.id][teacher.id]):
                        assigned_teacher = teacher
                        break

            # Trouver la salle assignée
            assigned_room = None
            for room in self.classrooms:
                if solver.Value(self.course_to_room[course.id][room.id]):
                    assigned_room = room
                    break

            # Trouver les étudiants assignés
            assigned_students = []
            for student in self.students:
                if solver.Value(self.student_to_course[student.id][course.id]):
                    assigned_students.append(student)

            # Mettre à jour le cours
            course.assigned_teacher = assigned_teacher
            course.assigned_room = assigned_room
            course.assigned_students = assigned_students

            if assigned_timeslot:
                assignments.append(ScheduleAssignment(course, assigned_timeslot))

        return sorted(assignments, key=lambda x: (x.timeslot.day, x.timeslot.period))
