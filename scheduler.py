"""
Optimiseur d'horaires utilisant Google OR-Tools
Nouvelle approche : horaires individuels par étudiant avec sessions de cours dynamiques
Processus en 3 étapes : 1) Options de regroupement, 2) Horaires étudiants, 3) Assignation enseignants
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple, Optional
from models import (CourseSession, TimeSlot, Teacher, Classroom, Student,
                   CourseType, StudentScheduleEntry)
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class GroupingStrategy(Enum):
    """Stratégies d'optimisation pour le regroupement"""
    MINIMIZE_SESSIONS = "Minimiser le nombre de sessions"
    BALANCE_GROUPS = "Équilibrer les groupes"
    MAXIMIZE_PREFERRED_ROOMS = "Maximiser l'utilisation des salles préférées"


class ProgramVariant(Enum):
    """Variantes de regroupement basées sur les programmes"""
    GROUP_BY_PROGRAM = "Regrouper par programme"
    MIX_PROGRAMS = "Mélanger les programmes"
    BALANCED = "Équilibré"


@dataclass
class GroupSizeOption:
    """Option de taille de groupe"""
    name: str
    min_students: int
    max_students: int
    description: str


@dataclass
class GroupingOption:
    """Configuration complète de regroupement"""
    id: int
    name: str
    group_size: GroupSizeOption
    strategy: GroupingStrategy
    program_variant: ProgramVariant
    estimated_sessions: int = 0
    avg_group_size: float = 0.0
    description: str = ""


class ScheduleOptimizer:
    """Optimise l'attribution des cours avec horaires individuels par étudiant"""

    # Définition des options de taille de groupe
    GROUP_SIZE_OPTIONS = [
        GroupSizeOption("Petits groupes", 15, 20, "Groupes de 15-20 étudiants (plus de sessions, plus d'attention individuelle)"),
        GroupSizeOption("Groupes moyens", 20, 25, "Groupes de 20-25 étudiants (équilibre entre taille et ressources)"),
        GroupSizeOption("Grands groupes", 25, 32, "Groupes de 25-32 étudiants (moins de sessions, optimisation des ressources)")
    ]

    @staticmethod
    def generate_grouping_options(students: List[Student], course_requirements: Dict[CourseType, int]) -> List[GroupingOption]:
        """
        Génère 9 options de regroupement combinant tailles de groupe, stratégies et variantes de programme

        Returns:
            Liste de 9 GroupingOption avec estimations
        """
        options = []
        option_id = 0

        strategies = list(GroupingStrategy)
        program_variants = list(ProgramVariant)

        for group_size in ScheduleOptimizer.GROUP_SIZE_OPTIONS:
            for strategy in strategies:
                for variant in program_variants:
                    # Estimer le nombre de sessions et la taille moyenne des groupes
                    total_courses = sum(course_requirements.values())
                    total_student_courses = len(students) * total_courses

                    # Estimation du nombre de sessions basée sur la taille min/max
                    avg_size = (group_size.min_students + group_size.max_students) / 2
                    estimated_sessions = int(total_student_courses / avg_size)

                    # Ajuster selon la stratégie
                    if strategy == GroupingStrategy.MINIMIZE_SESSIONS:
                        estimated_sessions = int(estimated_sessions * 0.9)  # Viser moins de sessions
                    elif strategy == GroupingStrategy.BALANCE_GROUPS:
                        estimated_sessions = int(estimated_sessions * 1.0)  # Neutre
                    elif strategy == GroupingStrategy.MAXIMIZE_PREFERRED_ROOMS:
                        estimated_sessions = int(estimated_sessions * 1.1)  # Plus de flexibilité

                    # Construire le nom et la description
                    name = f"Option {option_id + 1}: {group_size.name}"
                    description = f"{strategy.value} | {variant.value}\n{group_size.description}"

                    option = GroupingOption(
                        id=option_id,
                        name=name,
                        group_size=group_size,
                        strategy=strategy,
                        program_variant=variant,
                        estimated_sessions=estimated_sessions,
                        avg_group_size=avg_size,
                        description=description
                    )
                    options.append(option)
                    option_id += 1

        return options

    def __init__(self, teachers: List[Teacher], classrooms: List[Classroom],
                 students: List[Student], course_requirements: Dict[CourseType, int],
                 grouping_option: Optional[GroupingOption] = None):
        """
        Args:
            teachers: Liste des enseignants disponibles
            classrooms: Liste des salles disponibles
            students: Liste des étudiants
            course_requirements: Dictionnaire {CourseType: nombre_de_cours}
            grouping_option: Option de regroupement sélectionnée (None pour valeur par défaut)
        """
        self.teachers = teachers
        self.classrooms = classrooms
        self.students = students
        self.course_requirements = course_requirements
        self.grouping_option = grouping_option or GroupingOption(
            id=0,
            name="Défaut",
            group_size=self.GROUP_SIZE_OPTIONS[1],  # Moyens
            strategy=GroupingStrategy.MINIMIZE_SESSIONS,
            program_variant=ProgramVariant.BALANCED
        )
        self.min_students_per_session = self.grouping_option.group_size.min_students
        self.max_students_per_session = self.grouping_option.group_size.max_students
        self.model = cp_model.CpModel()

        # Calculer le nombre optimal de jours nécessaires
        total_courses = sum(self.course_requirements.values())
        periods_per_day = 4
        min_days_needed = (total_courses + periods_per_day - 1) // periods_per_day  # Arrondi supérieur
        num_days = max(min_days_needed, 9)  # Au moins le minimum, max 9

        print(f"Utilisation de {num_days} jours pour {total_courses} cours par étudiant")
        self.timeslots = [TimeSlot(day=d, period=p) for d in range(1, num_days + 1) for p in range(1, periods_per_day + 1)]

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

        # Contrainte 9: Maximum d'étudiants par session (selon l'option choisie)
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
                    self.model.Add(sum(students_in_session) <= self.max_students_per_session)

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

        # Contrainte 11: Une session active doit avoir au minimum min_students_per_session étudiants
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
                    num_students = sum(students_in_session)
                    # Si la session est active, elle doit avoir au moins min_students_per_session étudiants
                    self.model.Add(num_students >= self.min_students_per_session).OnlyEnforceIf(
                        self.session_active[course_type][timeslot]
                    )

    def add_optimization_objectives(self):
        """Ajoute des objectifs d'optimisation selon la stratégie choisie"""
        print(f"Ajout des objectifs d'optimisation (stratégie: {self.grouping_option.strategy.value})...")

        # Objectif 1: Nombre de sessions actives
        total_sessions = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                total_sessions.append(self.session_active[course_type][timeslot])

        # Objectif 2: Variance dans la taille des groupes (pour équilibrage)
        # On veut que toutes les sessions aient approximativement la même taille
        session_size_vars = []
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
                    # Créer une variable pour la taille de cette session
                    size_var = self.model.NewIntVar(0, self.max_students_per_session,
                                                     f'size_{course_type.name}_{timeslot.day}_{timeslot.period}')
                    self.model.Add(size_var == sum(students_in_session))
                    session_size_vars.append(size_var)

        # Objectif 3: Préférer que les enseignants restent dans leur salle préférée
        away_from_home = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                for teacher in self.teachers:
                    if course_type in teacher.can_teach and teacher.id in self.session_teacher[course_type][timeslot]:
                        if teacher.preferred_classroom:
                            for room in self.classrooms:
                                if room.id != teacher.preferred_classroom.id:
                                    both_assigned = self.model.NewBoolVar(
                                        f'away_{course_type.name}_{timeslot.day}_{timeslot.period}_t{teacher.id}_r{room.id}'
                                    )
                                    self.model.AddMultiplicationEquality(
                                        both_assigned,
                                        [
                                            self.session_teacher[course_type][timeslot][teacher.id],
                                            self.session_room[course_type][timeslot][room.id]
                                        ]
                                    )
                                    away_from_home.append(both_assigned)

        # Combiner les objectifs selon la stratégie
        if self.grouping_option.strategy == GroupingStrategy.MINIMIZE_SESSIONS:
            # Priorité maximale sur la minimisation des sessions
            self.model.Minimize(1000 * sum(total_sessions) + sum(away_from_home))
        elif self.grouping_option.strategy == GroupingStrategy.BALANCE_GROUPS:
            # Priorité sur l'équilibrage des groupes (minimiser variance) et sessions
            # Note: Pour simplifier, on minimise les sessions et on compte sur la contrainte min/max
            self.model.Minimize(500 * sum(total_sessions) + sum(away_from_home))
        elif self.grouping_option.strategy == GroupingStrategy.MAXIMIZE_PREFERRED_ROOMS:
            # Priorité maximale sur les salles préférées
            self.model.Minimize(100 * sum(total_sessions) + 1000 * sum(away_from_home))

    def generate_greedy_initial_solution(self) -> Dict:
        """
        Génère une solution initiale gloutonne pour guider le solveur
        Approche: Assigner les cours aux premiers timeslots disponibles en respectant les contraintes de base
        """
        print("Génération d'une solution initiale gloutonne...")
        hints = {}

        # Pour chaque étudiant, assigner les cours de manière gloutonne
        for student in self.students:
            student_schedule = {}  # {timeslot: (course_type, course_num)}

            for course_type, num_courses in self.course_requirements.items():
                courses_assigned = 0
                day_usage = defaultdict(int)  # Combien de fois ce type de cours est utilisé par jour

                for course_num in range(num_courses):
                    # Chercher le premier timeslot disponible
                    for timeslot in self.timeslots:
                        # Vérifier si le timeslot est libre
                        if timeslot in student_schedule:
                            continue

                        # Vérifier la contrainte "1 cours par type par jour"
                        if day_usage[timeslot.day] >= 1:
                            continue

                        # Assigner ce cours à ce timeslot
                        student_schedule[timeslot] = (course_type, course_num)
                        day_usage[timeslot.day] += 1

                        # Stocker le hint
                        var = self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                        hints[var] = 1
                        courses_assigned += 1
                        break

        print(f"Solution initiale générée avec {len(hints)} hints")
        return hints

    def solve_student_schedules_only(self) -> Tuple[bool, List[CourseSession], Dict[int, List[StudentScheduleEntry]]]:
        """
        ÉTAPE 2: Résout UNIQUEMENT les horaires des étudiants sans assigner enseignants/salles

        Returns:
            (success, sessions, student_schedules)
            - success: True si une solution a été trouvée
            - sessions: Liste des sessions de cours créées (sans enseignant ni salle assignés)
            - student_schedules: Dict {student_id: [StudentScheduleEntry]}
        """
        # Créer un modèle simplifié sans variables d'enseignant/salle
        print("Création des variables pour horaires étudiants...")

        # Variables pour chaque étudiant et chaque type de cours
        for student in self.students:
            self.student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                self.student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    self.student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f'student_{student.id}_type_{course_type.name}_num_{course_num}_ts_{timeslot.day}_{timeslot.period}'
                        self.student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            self.model.NewBoolVar(var_name)

        # Variables pour les sessions actives
        for course_type in self.course_requirements.keys():
            self.session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'session_{course_type.name}_ts_{timeslot.day}_{timeslot.period}_active'
                self.session_active[course_type][timeslot] = self.model.NewBoolVar(var_name)

        print("Ajout des contraintes pour horaires étudiants...")

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
                if students_in_session:
                    num_students = sum(students_in_session)
                    self.model.Add(num_students >= 1).OnlyEnforceIf(self.session_active[course_type][timeslot])
                    self.model.Add(num_students == 0).OnlyEnforceIf(self.session_active[course_type][timeslot].Not())

        # Contrainte 4: Taille min/max des sessions
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
                    num_students = sum(students_in_session)
                    # Min étudiants si session active
                    self.model.Add(num_students >= self.min_students_per_session).OnlyEnforceIf(
                        self.session_active[course_type][timeslot]
                    )
                    # Max étudiants
                    self.model.Add(num_students <= self.max_students_per_session)

        # Contrainte 5: Un étudiant ne peut avoir qu'un cours de la même matière par jour
        for student in self.students:
            for day in range(1, 10):
                for course_type, num_courses in self.course_requirements.items():
                    courses_on_this_day = []
                    for course_num in range(num_courses):
                        for period in range(1, 5):
                            timeslot = TimeSlot(day=day, period=period)
                            courses_on_this_day.append(
                                self.student_course_timeslot[student.id][course_type][course_num][timeslot]
                            )
                    if courses_on_this_day:
                        self.model.Add(sum(courses_on_this_day) <= 1)

        # Générer une solution initiale pour guider le solveur (AVANT l'objectif)
        hints = self.generate_greedy_initial_solution()
        for var, value in hints.items():
            self.model.AddHint(var, value)

        # Objectif: Minimiser le nombre de sessions actives
        print("Ajout de l'objectif: minimiser les sessions...")
        total_sessions = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                total_sessions.append(self.session_active[course_type][timeslot])
        self.model.Minimize(sum(total_sessions))

        # Résolution
        print("Lancement du solveur pour horaires étudiants...")
        solver = cp_model.CpSolver()

        # Paramètres optimisés pour la performance
        solver.parameters.max_time_in_seconds = 300.0  # 5 minutes max
        solver.parameters.num_search_workers = 8
        solver.parameters.log_search_progress = True

        # Stratégies pour accélérer la recherche
        solver.parameters.cp_model_presolve = True  # Simplifie le modèle avant résolution
        solver.parameters.cp_model_probing_level = 2  # Niveau de probing modéré
        solver.parameters.linearization_level = 2  # Linéarisation pour simplifier
        solver.parameters.symmetry_level = 2  # Détecte et casse les symétries

        # Stratégie de recherche plus agressive (privilégie les solutions rapides)
        solver.parameters.search_branching = cp_model.PORTFOLIO_SEARCH
        solver.parameters.enumerate_all_solutions = False

        # Accepter une solution "assez bonne" plutôt que chercher l'optimal
        solver.parameters.relative_gap_limit = 0.05  # Accepte 5% de sous-optimalité

        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution trouvée ! Statut: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
            sessions, student_schedules = self.extract_student_schedules_solution(solver)
            return True, sessions, student_schedules
        else:
            print(f"Aucune solution trouvée. Statut: {status}")
            return False, [], {}

    def extract_student_schedules_solution(self, solver: cp_model.CpSolver) -> Tuple[List[CourseSession], Dict[int, List[StudentScheduleEntry]]]:
        """Extrait la solution pour horaires étudiants uniquement (sans enseignants/salles)"""
        print("Extraction de la solution des horaires étudiants...")

        sessions = []
        session_id = 0
        session_map = {}

        # Créer les sessions de cours (sans enseignant ni salle)
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                if solver.Value(self.session_active[course_type][timeslot]):
                    session = CourseSession(
                        id=session_id,
                        course_type=course_type,
                        timeslot=timeslot,
                        assigned_teacher=None,  # Pas encore assigné
                        assigned_room=None,      # Pas encore assigné
                        students=[]
                    )
                    sessions.append(session)
                    session_map[(course_type, timeslot)] = session
                    session_id += 1

        # Créer les horaires individuels des étudiants
        student_schedules = {}
        for student in self.students:
            schedule_entries = []
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    for timeslot in self.timeslots:
                        if solver.Value(self.student_course_timeslot[student.id][course_type][course_num][timeslot]):
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

        sessions = sorted(sessions, key=lambda x: (x.timeslot.day, x.timeslot.period))
        print(f"Solution extraite: {len(sessions)} sessions créées pour {len(self.students)} étudiants")
        return sessions, student_schedules

    @staticmethod
    def assign_teachers_and_rooms(sessions: List[CourseSession], teachers: List[Teacher],
                                   classrooms: List[Classroom]) -> Tuple[bool, List[CourseSession]]:
        """
        ÉTAPE 3: Assigne les enseignants et salles aux sessions existantes

        Args:
            sessions: Sessions avec étudiants et timeslots (sans enseignants/salles)
            teachers: Liste des enseignants disponibles
            classrooms: Liste des salles disponibles

        Returns:
            (success, updated_sessions)
        """
        print("Assignation des enseignants et salles aux sessions...")

        model = cp_model.CpModel()

        # Variables: pour chaque session, quel enseignant et quelle salle
        session_teacher = {}
        session_room = {}

        for session in sessions:
            session_teacher[session.id] = {}
            for teacher in teachers:
                if session.course_type in teacher.can_teach:
                    var_name = f'session_{session.id}_teacher_{teacher.id}'
                    session_teacher[session.id][teacher.id] = model.NewBoolVar(var_name)

            session_room[session.id] = {}
            for room in classrooms:
                if session.course_type in room.allowed_subjects:
                    var_name = f'session_{session.id}_room_{room.id}'
                    session_room[session.id][room.id] = model.NewBoolVar(var_name)

        # Contrainte 1: Chaque session doit avoir exactement un enseignant qualifié
        for session in sessions:
            if session_teacher[session.id]:
                model.AddExactlyOne(list(session_teacher[session.id].values()))

        # Contrainte 2: Chaque session doit avoir exactement une salle autorisée
        for session in sessions:
            if session_room[session.id]:
                model.AddExactlyOne(list(session_room[session.id].values()))

        # Contrainte 3: Un enseignant ne peut enseigner qu'une session à la fois
        for teacher in teachers:
            # Grouper les sessions par timeslot
            timeslot_sessions = defaultdict(list)
            for session in sessions:
                timeslot_sessions[session.timeslot].append(session)

            for timeslot, timeslot_sess in timeslot_sessions.items():
                sessions_with_teacher = []
                for session in timeslot_sess:
                    if teacher.id in session_teacher[session.id]:
                        sessions_with_teacher.append(session_teacher[session.id][teacher.id])
                if sessions_with_teacher:
                    model.Add(sum(sessions_with_teacher) <= 1)

        # Contrainte 4: Une salle ne peut accueillir qu'une session à la fois
        for room in classrooms:
            timeslot_sessions = defaultdict(list)
            for session in sessions:
                timeslot_sessions[session.timeslot].append(session)

            for timeslot, timeslot_sess in timeslot_sessions.items():
                sessions_in_room = []
                for session in timeslot_sess:
                    if room.id in session_room[session.id]:
                        sessions_in_room.append(session_room[session.id][room.id])
                if sessions_in_room:
                    model.Add(sum(sessions_in_room) <= 1)

        # Objectif: Maximiser l'utilisation des salles préférées
        print("Ajout de l'objectif: maximiser salles préférées...")
        preferred_room_usage = []
        for session in sessions:
            for teacher in teachers:
                if teacher.id in session_teacher[session.id] and teacher.preferred_classroom:
                    if teacher.preferred_classroom.id in session_room[session.id]:
                        # Variable pour: ce teacher dans cette session ET sa salle préférée
                        both_var = model.NewBoolVar(f'pref_sess{session.id}_t{teacher.id}')
                        model.AddMultiplicationEquality(
                            both_var,
                            [
                                session_teacher[session.id][teacher.id],
                                session_room[session.id][teacher.preferred_classroom.id]
                            ]
                        )
                        preferred_room_usage.append(both_var)

        if preferred_room_usage:
            model.Maximize(sum(preferred_room_usage))

        # Résolution
        print("Lancement du solveur pour enseignants et salles...")
        solver = cp_model.CpSolver()

        # Paramètres optimisés (cette étape est plus rapide)
        solver.parameters.max_time_in_seconds = 120.0  # 2 minutes max
        solver.parameters.num_search_workers = 8
        solver.parameters.log_search_progress = True

        # Optimisations similaires
        solver.parameters.cp_model_presolve = True
        solver.parameters.linearization_level = 2
        solver.parameters.symmetry_level = 2
        solver.parameters.search_branching = cp_model.PORTFOLIO_SEARCH

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Assignation réussie ! Statut: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")

            # Mettre à jour les sessions avec enseignants et salles
            for session in sessions:
                # Trouver l'enseignant assigné
                for teacher in teachers:
                    if teacher.id in session_teacher[session.id]:
                        if solver.Value(session_teacher[session.id][teacher.id]):
                            session.assigned_teacher = teacher
                            break

                # Trouver la salle assignée
                for room in classrooms:
                    if room.id in session_room[session.id]:
                        if solver.Value(session_room[session.id][room.id]):
                            session.assigned_room = room
                            break

            print(f"Assignation terminée: {len(sessions)} sessions avec enseignants et salles")
            return True, sessions
        else:
            print(f"Échec de l'assignation. Statut: {status}")
            return False, sessions

    def solve(self) -> Tuple[bool, List[CourseSession], Dict[int, List[StudentScheduleEntry]]]:
        """
        Résout le problème d'optimisation (méthode complète originale - conservée pour compatibilité)

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
        solver.parameters.max_time_in_seconds = 7200.0  # 10 minutes pour 176 élèves
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
