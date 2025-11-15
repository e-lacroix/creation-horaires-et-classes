"""
Optimiseur d'horaires utilisant Google OR-Tools
Nouvelle approche : horaires individuels par étudiant avec sessions de cours dynamiques
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
from models import (CourseSession, TimeSlot, Teacher, Classroom, Student,
                   CourseType, StudentScheduleEntry)
from collections import defaultdict


class ScheduleOptimizer:
    """Optimise l'attribution des cours avec horaires individuels par étudiant"""

    def __init__(self, teachers: List[Teacher], classrooms: List[Classroom],
                 students: List[Student], course_requirements: Dict[CourseType, int]):
        """
        Args:
            teachers: Liste des enseignants disponibles
            classrooms: Liste des salles disponibles
            students: Liste des étudiants
            course_requirements: Dictionnaire {CourseType: nombre_de_cours}
        """
        self.teachers = teachers
        self.classrooms = classrooms
        self.students = students
        self.course_requirements = course_requirements  # Ex: {SCIENCE: 4, FRANCAIS: 6, ...}
        self.model = cp_model.CpModel()
        self.timeslots = [TimeSlot(day=d, period=p) for d in range(1, 10) for p in range(1, 5)]

        # Variables de décision
        self.student_course_timeslot = {}  # [student_id][course_type][course_num][timeslot]
        self.session_active = {}  # [course_type][timeslot]
        self.session_teacher = {}  # [course_type][timeslot][teacher_id]
        self.session_room = {}  # [course_type][timeslot][room_id]
        self.student_in_session = {}  # [student_id][course_type][course_num][timeslot]

    def create_variables(self):
        """Crée les variables de décision pour le modèle"""
        print("Création des variables de décision...")

        # Pour chaque étudiant et chaque type de cours requis, assigner des timeslots
        for student in self.students:
            self.student_course_timeslot[student.id] = {}
            self.student_in_session[student.id] = {}

            for course_type, num_courses in self.course_requirements.items():
                self.student_course_timeslot[student.id][course_type] = {}
                self.student_in_session[student.id][course_type] = {}

                # Chaque étudiant doit suivre num_courses cours de ce type
                for course_num in range(num_courses):
                    self.student_course_timeslot[student.id][course_type][course_num] = {}
                    self.student_in_session[student.id][course_type][course_num] = {}

                    for timeslot in self.timeslots:
                        var_name = f'student_{student.id}_type_{course_type.name}_num_{course_num}_ts_{timeslot.day}_{timeslot.period}'
                        self.student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            self.model.NewBoolVar(var_name)

        # Variables pour les sessions de cours
        for course_type in self.course_requirements.keys():
            self.session_active[course_type] = {}
            self.session_teacher[course_type] = {}
            self.session_room[course_type] = {}

            for timeslot in self.timeslots:
                # Session active ou non
                var_name = f'session_{course_type.name}_ts_{timeslot.day}_{timeslot.period}_active'
                self.session_active[course_type][timeslot] = self.model.NewBoolVar(var_name)

                # Enseignant pour cette session
                self.session_teacher[course_type][timeslot] = {}
                for teacher in self.teachers:
                    if course_type in teacher.can_teach:
                        var_name = f'session_{course_type.name}_ts_{timeslot.day}_{timeslot.period}_teacher_{teacher.id}'
                        self.session_teacher[course_type][timeslot][teacher.id] = \
                            self.model.NewBoolVar(var_name)

                # Salle pour cette session
                self.session_room[course_type][timeslot] = {}
                for room in self.classrooms:
                    var_name = f'session_{course_type.name}_ts_{timeslot.day}_{timeslot.period}_room_{room.id}'
                    self.session_room[course_type][timeslot][room.id] = \
                        self.model.NewBoolVar(var_name)

    def add_constraints(self):
        """Ajoute les contraintes au modèle"""
        print("Ajout des contraintes...")

        # Contrainte 1: Chaque étudiant doit avoir exactement un timeslot pour chaque cours requis
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    self.model.AddExactlyOne([
                        self.student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        # Contrainte 2: Un étudiant ne peut avoir qu'un seul cours à la fois
        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                # Au maximum un cours à ce timeslot
                self.model.Add(sum(courses_at_this_time) <= 1)

        # Contrainte 3: Lien entre présence d'étudiants et activation de session
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []

                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                # Si au moins un étudiant, la session est active
                if students_in_session:
                    num_students = sum(students_in_session)
                    # session_active == 1 ssi num_students >= 1
                    self.model.Add(num_students >= 1).OnlyEnforceIf(self.session_active[course_type][timeslot])
                    self.model.Add(num_students == 0).OnlyEnforceIf(self.session_active[course_type][timeslot].Not())

        # Contrainte 4: Une session active doit avoir exactement un enseignant
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                if self.session_teacher[course_type][timeslot]:
                    teacher_vars = list(self.session_teacher[course_type][timeslot].values())
                    # Si session active, exactement un enseignant
                    self.model.Add(sum(teacher_vars) == 1).OnlyEnforceIf(self.session_active[course_type][timeslot])
                    # Si session inactive, aucun enseignant
                    self.model.Add(sum(teacher_vars) == 0).OnlyEnforceIf(self.session_active[course_type][timeslot].Not())

        # Contrainte 5: Une session active doit avoir exactement une salle
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                room_vars = list(self.session_room[course_type][timeslot].values())
                # Si session active, exactement une salle
                self.model.Add(sum(room_vars) == 1).OnlyEnforceIf(self.session_active[course_type][timeslot])
                # Si session inactive, aucune salle
                self.model.Add(sum(room_vars) == 0).OnlyEnforceIf(self.session_active[course_type][timeslot].Not())

        # Contrainte 6: Un enseignant ne peut enseigner qu'une session à la fois
        for teacher in self.teachers:
            for timeslot in self.timeslots:
                sessions_with_teacher = []
                for course_type in teacher.can_teach:
                    if course_type in self.course_requirements:
                        if teacher.id in self.session_teacher[course_type][timeslot]:
                            sessions_with_teacher.append(
                                self.session_teacher[course_type][timeslot][teacher.id]
                            )
                if sessions_with_teacher:
                    self.model.Add(sum(sessions_with_teacher) <= 1)

        # Contrainte 7: Une salle ne peut accueillir qu'une session à la fois
        for room in self.classrooms:
            for timeslot in self.timeslots:
                sessions_in_room = []
                for course_type in self.course_requirements.keys():
                    if room.id in self.session_room[course_type][timeslot]:
                        sessions_in_room.append(
                            self.session_room[course_type][timeslot][room.id]
                        )
                if sessions_in_room:
                    self.model.Add(sum(sessions_in_room) <= 1)

        # Contrainte 8: Une salle ne peut accueillir qu'un cours autorisé
        # (les matières doivent être dans allowed_subjects de la salle)
        for room in self.classrooms:
            for course_type in self.course_requirements.keys():
                # Si ce type de cours n'est pas autorisé dans cette salle
                if course_type not in room.allowed_subjects:
                    for timeslot in self.timeslots:
                        if room.id in self.session_room[course_type][timeslot]:
                            # Forcer cette variable à 0 (cette salle ne peut pas accueillir ce cours)
                            self.model.Add(self.session_room[course_type][timeslot][room.id] == 0)

        # Contrainte 9: Maximum 28 étudiants par session
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                if students_in_session:
                    self.model.Add(sum(students_in_session) <= 28)

        # Contrainte 10: Un étudiant ne peut avoir qu'un cours de la même matière par jour
        for student in self.students:
            for day in range(1, 10):  # 9 jours
                for course_type, num_courses in self.course_requirements.items():
                    courses_on_this_day = []
                    for course_num in range(num_courses):
                        for period in range(1, 5):  # 4 périodes
                            timeslot = TimeSlot(day=day, period=period)
                            courses_on_this_day.append(
                                self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                            )
                    # Maximum 1 cours de ce type ce jour
                    if courses_on_this_day:
                        self.model.Add(sum(courses_on_this_day) <= 1)

    def add_optimization_objectives(self):
        """Ajoute des objectifs d'optimisation"""
        print("Ajout des objectifs d'optimisation...")

        # Objectif principal: Minimiser le nombre de sessions actives
        # (moins de sessions = moins de salles et d'enseignants utilisés)
        total_sessions = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                total_sessions.append(self.session_active[course_type][timeslot])

        # Objectif secondaire: Préférer que les enseignants restent dans leur salle préférée
        # Compter combien de fois un enseignant est dans une salle qui n'est PAS sa salle préférée
        away_from_home = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                for teacher in self.teachers:
                    if course_type in teacher.can_teach and teacher.id in self.session_teacher[course_type][timeslot]:
                        if teacher.preferred_classroom:
                            # Créer une variable qui est 1 si: enseignant assigné ET salle != salle préférée
                            for room in self.classrooms:
                                if room.id != teacher.preferred_classroom.id:
                                    # Variable temporaire: teacher assigned AND room assigned
                                    both_assigned = self.model.NewBoolVar(
                                        f'away_{course_type.name}_{timeslot.day}_{timeslot.period}_t{teacher.id}_r{room.id}'
                                    )
                                    # both_assigned == 1 ssi les deux sont vrais
                                    self.model.AddMultiplicationEquality(
                                        both_assigned,
                                        [
                                            self.session_teacher[course_type][timeslot][teacher.id],
                                            self.session_room[course_type][timeslot][room.id]
                                        ]
                                    )
                                    away_from_home.append(both_assigned)

        # Objectif combiné: minimiser les sessions (priorité haute) + minimiser les changements de salle (priorité basse)
        # Poids: 1000 pour les sessions, 1 pour les changements de salle
        # Cela garantit qu'on minimise d'abord les sessions, puis on optimise les salles
        self.model.Minimize(1000 * sum(total_sessions) + sum(away_from_home))

    def solve(self) -> Tuple[bool, List[CourseSession], Dict[int, List[StudentScheduleEntry]]]:
        """
        Résout le problème d'optimisation

        Returns:
            (success, sessions, student_schedules)
            - success: True si une solution a été trouvée
            - sessions: Liste des sessions de cours créées
            - student_schedules: Dict {student_id: [StudentScheduleEntry]}
        """
        self.create_variables()
        self.add_constraints()
        self.add_optimization_objectives()

        print("Lancement du solveur...")
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 120.0  # Augmenté à 2 minutes
        solver.parameters.num_search_workers = 8
        solver.parameters.log_search_progress = True

        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution trouvée ! Statut: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
            sessions, student_schedules = self.extract_solution(solver)
            return True, sessions, student_schedules
        else:
            print(f"Aucune solution trouvée. Statut: {status}")
            return False, [], {}

    def extract_solution(self, solver: cp_model.CpSolver) -> Tuple[List[CourseSession], Dict[int, List[StudentScheduleEntry]]]:
        """Extrait la solution du solveur"""
        print("Extraction de la solution...")

        sessions = []
        session_id = 0
        session_map = {}  # {(course_type, timeslot): CourseSession}

        # Créer les sessions de cours
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                if solver.Value(self.session_active[course_type][timeslot]):
                    # Trouver l'enseignant assigné
                    assigned_teacher = None
                    for teacher in self.teachers:
                        if teacher.id in self.session_teacher[course_type][timeslot]:
                            if solver.Value(self.session_teacher[course_type][timeslot][teacher.id]):
                                assigned_teacher = teacher
                                break

                    # Trouver la salle assignée
                    assigned_room = None
                    for room in self.classrooms:
                        if solver.Value(self.session_room[course_type][timeslot][room.id]):
                            assigned_room = room
                            break

                    # Créer la session
                    session = CourseSession(
                        id=session_id,
                        course_type=course_type,
                        timeslot=timeslot,
                        assigned_teacher=assigned_teacher,
                        assigned_room=assigned_room,
                        students=[]
                    )
                    sessions.append(session)
                    session_map[(course_type, timeslot)] = session
                    session_id += 1

        # Créer les horaires individuels des étudiants et peupler les sessions
        student_schedules = {}
        for student in self.students:
            schedule_entries = []

            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    # Trouver le timeslot assigné pour ce cours
                    for timeslot in self.timeslots:
                        if solver.Value(self.student_course_timeslot[student.id][course_type][course_num][timeslot]):
                            # Trouver la session correspondante
                            session = session_map.get((course_type, timeslot))
                            if session:
                                session.students.append(student)

                            entry = StudentScheduleEntry(
                                course_type=course_type,
                                timeslot=timeslot,
                                session=session
                            )
                            schedule_entries.append(entry)
                            break

            student_schedules[student.id] = sorted(schedule_entries,
                                                   key=lambda x: (x.timeslot.day, x.timeslot.period))

        # Trier les sessions par timeslot
        sessions = sorted(sessions, key=lambda x: (x.timeslot.day, x.timeslot.period))

        print(f"Solution extraite: {len(sessions)} sessions créées pour {len(self.students)} étudiants")
        return sessions, student_schedules
