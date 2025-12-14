"""
Script de profilage pour identifier quelle contrainte ralentit le calcul
"""
import setup_encoding

from ortools.sat.python import cp_model
from typing import List, Dict
from models import TimeSlot, Student, CourseType
from data_generator import generate_sample_data
import time


class ConstraintProfiler:
    """Teste l'impact de chaque contrainte sur le temps de résolution"""

    def __init__(self, students: List[Student], course_requirements: Dict[CourseType, int]):
        self.students = students
        self.course_requirements = course_requirements

        # Calculer le nombre de jours nécessaires
        total_courses = sum(self.course_requirements.values())
        periods_per_day = 4
        num_days = max((total_courses + periods_per_day - 1) // periods_per_day, 9)

        self.timeslots = [TimeSlot(day=d, period=p)
                         for d in range(1, num_days + 1)
                         for p in range(1, periods_per_day + 1)]

        self.min_students_per_session = 20
        self.max_students_per_session = 25

    def count_variables(self, model: cp_model.CpModel, student_course_timeslot: Dict,
                       session_active: Dict) -> Dict[str, int]:
        """Compte le nombre de variables créées"""

        # Variables étudiant-cours-timeslot
        num_student_vars = 0
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    num_student_vars += len(self.timeslots)

        # Variables session active
        num_session_vars = len(self.course_requirements) * len(self.timeslots)

        return {
            "variables_etudiant": num_student_vars,
            "variables_session": num_session_vars,
            "total_variables": num_student_vars + num_session_vars
        }

    def test_without_constraints(self) -> float:
        """Test 0: Créer seulement les variables, sans contraintes"""
        print("\n" + "="*70)
        print("TEST 0: Création des variables uniquement (SANS contraintes)")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}
        session_active = {}

        # Créer les variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        for course_type in self.course_requirements.keys():
            session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'sess_{course_type.name}_t{timeslot.day}_{timeslot.period}'
                session_active[course_type][timeslot] = model.NewBoolVar(var_name)

        # Compter les variables
        var_counts = self.count_variables(model, student_course_timeslot, session_active)
        print(f"Variables étudiants: {var_counts['variables_etudiant']:,}")
        print(f"Variables sessions: {var_counts['variables_session']:,}")
        print(f"TOTAL VARIABLES: {var_counts['total_variables']:,}")

        # Pas de résolution, juste retourner 0
        return 0.0

    def test_constraint_1(self) -> float:
        """Test 1: Un timeslot par cours requis"""
        print("\n" + "="*70)
        print("TEST 1: Contrainte 'Exactement un timeslot par cours requis'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        # CONTRAINTE 1
        constraint_count = 0
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])
                    constraint_count += 1

        print(f"Nombre de contraintes ajoutées: {constraint_count:,}")

        return self._solve_and_time(model)

    def test_constraint_2(self) -> float:
        """Test 2: Un seul cours à la fois par étudiant"""
        print("\n" + "="*70)
        print("TEST 2: Contrainte 'Un seul cours à la fois par étudiant'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        # Contrainte 1 (nécessaire)
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        # CONTRAINTE 2
        constraint_count = 0
        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                model.Add(sum(courses_at_this_time) <= 1)
                constraint_count += 1

        print(f"Nombre de contraintes ajoutées: {constraint_count:,}")

        return self._solve_and_time(model)

    def test_constraint_3(self) -> float:
        """Test 3: Lien entre étudiants et sessions actives"""
        print("\n" + "="*70)
        print("TEST 3: Contrainte 'Lien étudiants-sessions actives'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}
        session_active = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        for course_type in self.course_requirements.keys():
            session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'sess_{course_type.name}_t{timeslot.day}_{timeslot.period}'
                session_active[course_type][timeslot] = model.NewBoolVar(var_name)

        # Contraintes précédentes
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                model.Add(sum(courses_at_this_time) <= 1)

        # CONTRAINTE 3
        constraint_count = 0
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= 1).OnlyEnforceIf(session_active[course_type][timeslot])
                    model.Add(num_students == 0).OnlyEnforceIf(session_active[course_type][timeslot].Not())
                    constraint_count += 2

        print(f"Nombre de contraintes ajoutées: {constraint_count:,}")

        return self._solve_and_time(model)

    def test_constraint_4(self) -> float:
        """Test 4: Taille min/max des sessions"""
        print("\n" + "="*70)
        print("TEST 4: Contrainte 'Taille min/max des sessions'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}
        session_active = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        for course_type in self.course_requirements.keys():
            session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'sess_{course_type.name}_t{timeslot.day}_{timeslot.period}'
                session_active[course_type][timeslot] = model.NewBoolVar(var_name)

        # Contraintes précédentes
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                model.Add(sum(courses_at_this_time) <= 1)

        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= 1).OnlyEnforceIf(session_active[course_type][timeslot])
                    model.Add(num_students == 0).OnlyEnforceIf(session_active[course_type][timeslot].Not())

        # CONTRAINTE 4
        constraint_count = 0
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= self.min_students_per_session).OnlyEnforceIf(
                        session_active[course_type][timeslot]
                    )
                    model.Add(num_students <= self.max_students_per_session)
                    constraint_count += 2

        print(f"Nombre de contraintes ajoutées: {constraint_count:,}")

        return self._solve_and_time(model)

    def test_constraint_5(self) -> float:
        """Test 5: Un cours par matière par jour"""
        print("\n" + "="*70)
        print("TEST 5: Contrainte 'Max 1 cours par matière par jour'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}
        session_active = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        for course_type in self.course_requirements.keys():
            session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'sess_{course_type.name}_t{timeslot.day}_{timeslot.period}'
                session_active[course_type][timeslot] = model.NewBoolVar(var_name)

        # Contraintes précédentes
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                model.Add(sum(courses_at_this_time) <= 1)

        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= 1).OnlyEnforceIf(session_active[course_type][timeslot])
                    model.Add(num_students == 0).OnlyEnforceIf(session_active[course_type][timeslot].Not())

        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= self.min_students_per_session).OnlyEnforceIf(
                        session_active[course_type][timeslot]
                    )
                    model.Add(num_students <= self.max_students_per_session)

        # CONTRAINTE 5
        constraint_count = 0
        for student in self.students:
            for day in range(1, 10):
                for course_type, num_courses in self.course_requirements.items():
                    courses_on_this_day = []
                    for course_num in range(num_courses):
                        for period in range(1, 5):
                            timeslot = TimeSlot(day=day, period=period)
                            courses_on_this_day.append(
                                student_course_timeslot[student.id][course_type][course_num][timeslot]
                            )
                    if courses_on_this_day:
                        model.Add(sum(courses_on_this_day) <= 1)
                        constraint_count += 1

        print(f"Nombre de contraintes ajoutées: {constraint_count:,}")

        return self._solve_and_time(model)

    def test_with_objective(self) -> float:
        """Test 6: Toutes les contraintes + objectif d'optimisation"""
        print("\n" + "="*70)
        print("TEST 6: Toutes les contraintes + Objectif 'Minimiser sessions'")
        print("="*70)

        model = cp_model.CpModel()
        student_course_timeslot = {}
        session_active = {}

        # Variables
        for student in self.students:
            student_course_timeslot[student.id] = {}
            for course_type, num_courses in self.course_requirements.items():
                student_course_timeslot[student.id][course_type] = {}
                for course_num in range(num_courses):
                    student_course_timeslot[student.id][course_type][course_num] = {}
                    for timeslot in self.timeslots:
                        var_name = f's{student.id}_c{course_type.name}_n{course_num}_t{timeslot.day}_{timeslot.period}'
                        student_course_timeslot[student.id][course_type][course_num][timeslot] = \
                            model.NewBoolVar(var_name)

        for course_type in self.course_requirements.keys():
            session_active[course_type] = {}
            for timeslot in self.timeslots:
                var_name = f'sess_{course_type.name}_t{timeslot.day}_{timeslot.period}'
                session_active[course_type][timeslot] = model.NewBoolVar(var_name)

        # Toutes les contraintes
        for student in self.students:
            for course_type, num_courses in self.course_requirements.items():
                for course_num in range(num_courses):
                    model.AddExactlyOne([
                        student_course_timeslot[student.id][course_type][course_num][ts]
                        for ts in self.timeslots
                    ])

        for student in self.students:
            for timeslot in self.timeslots:
                courses_at_this_time = []
                for course_type, num_courses in self.course_requirements.items():
                    for course_num in range(num_courses):
                        courses_at_this_time.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )
                model.Add(sum(courses_at_this_time) <= 1)

        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= 1).OnlyEnforceIf(session_active[course_type][timeslot])
                    model.Add(num_students == 0).OnlyEnforceIf(session_active[course_type][timeslot].Not())

        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                students_in_session = []
                for student in self.students:
                    num_courses = self.course_requirements[course_type]
                    for course_num in range(num_courses):
                        students_in_session.append(
                            student_course_timeslot[student.id][course_type][course_num][timeslot]
                        )

                if students_in_session:
                    num_students = sum(students_in_session)
                    model.Add(num_students >= self.min_students_per_session).OnlyEnforceIf(
                        session_active[course_type][timeslot]
                    )
                    model.Add(num_students <= self.max_students_per_session)

        for student in self.students:
            for day in range(1, 10):
                for course_type, num_courses in self.course_requirements.items():
                    courses_on_this_day = []
                    for course_num in range(num_courses):
                        for period in range(1, 5):
                            timeslot = TimeSlot(day=day, period=period)
                            courses_on_this_day.append(
                                student_course_timeslot[student.id][course_type][course_num][timeslot]
                            )
                    if courses_on_this_day:
                        model.Add(sum(courses_on_this_day) <= 1)

        # OBJECTIF
        total_sessions = []
        for course_type in self.course_requirements.keys():
            for timeslot in self.timeslots:
                total_sessions.append(session_active[course_type][timeslot])

        model.Minimize(sum(total_sessions))
        print(f"Objectif: Minimiser {len(total_sessions):,} sessions potentielles")

        return self._solve_and_time(model)

    def _solve_and_time(self, model: cp_model.CpModel) -> float:
        """Résout le modèle et mesure le temps"""
        print("\nRésolution en cours...")

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0  # Court timeout pour les tests
        solver.parameters.num_search_workers = 8
        solver.parameters.log_search_progress = False  # Désactiver les logs

        start_time = time.time()
        status = solver.Solve(model)
        elapsed_time = time.time() - start_time

        # Afficher les statistiques
        print(f"\n📊 RÉSULTATS:")
        print(f"  Statut: {solver.StatusName(status)}")
        print(f"  ⏱️  Temps de résolution: {elapsed_time:.2f}s")
        print(f"  🌳 Branches explorées: {solver.NumBranches():,}")
        print(f"  🔄 Conflits: {solver.NumConflicts():,}")

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"  ✅ Solution trouvée!")
            if hasattr(solver, 'ObjectiveValue'):
                try:
                    print(f"  🎯 Valeur objectif: {solver.ObjectiveValue()}")
                except:
                    pass
        else:
            print(f"  ❌ Aucune solution dans le délai imparti")

        return elapsed_time

    def run_all_tests(self):
        """Exécute tous les tests et génère un rapport comparatif"""
        print("\n" + "="*70)
        print("🔬 PROFILAGE DES CONTRAINTES D'OPTIMISATION")
        print("="*70)
        print(f"Configuration:")
        print(f"  - Nombre d'étudiants: {len(self.students)}")
        print(f"  - Nombre de timeslots: {len(self.timeslots)}")
        print(f"  - Cours par étudiant: {sum(self.course_requirements.values())}")
        print(f"  - Timeout par test: 30 secondes")

        results = {}

        # Test 0
        results["0_variables_seules"] = self.test_without_constraints()

        # Test 1
        results["1_timeslot_par_cours"] = self.test_constraint_1()

        # Test 2
        results["2_un_cours_a_la_fois"] = self.test_constraint_2()

        # Test 3
        results["3_lien_sessions"] = self.test_constraint_3()

        # Test 4
        results["4_taille_sessions"] = self.test_constraint_4()

        # Test 5
        results["5_max_1_par_jour"] = self.test_constraint_5()

        # Test 6
        results["6_avec_objectif"] = self.test_with_objective()

        # Générer le rapport final
        self._generate_report(results)

    def _generate_report(self, results: Dict[str, float]):
        """Génère un rapport comparatif des temps"""
        print("\n" + "="*70)
        print("📈 RAPPORT COMPARATIF DES TEMPS DE RÉSOLUTION")
        print("="*70)

        test_names = {
            "0_variables_seules": "Variables uniquement (AUCUNE contrainte)",
            "1_timeslot_par_cours": "Contrainte 1: Un timeslot par cours",
            "2_un_cours_a_la_fois": "Contrainte 2: + Un cours à la fois",
            "3_lien_sessions": "Contrainte 3: + Lien sessions actives",
            "4_taille_sessions": "Contrainte 4: + Taille min/max sessions",
            "5_max_1_par_jour": "Contrainte 5: + Max 1 cours/matière/jour",
            "6_avec_objectif": "Test complet: + Objectif minimisation"
        }

        # Trier par temps
        sorted_results = sorted(results.items(), key=lambda x: x[1] if x[1] > 0 else -1)

        print("\n🏆 Classement par temps de résolution:")
        for i, (test_key, test_time) in enumerate(sorted_results, 1):
            if test_time > 0:
                print(f"  {i}. {test_names[test_key]}")
                print(f"     ⏱️  {test_time:.2f}s")

        # Calculer les augmentations
        print("\n📊 Impact cumulatif de chaque contrainte:")
        prev_time = 0
        for test_key in ["1_timeslot_par_cours", "2_un_cours_a_la_fois", "3_lien_sessions",
                        "4_taille_sessions", "5_max_1_par_jour", "6_avec_objectif"]:
            current_time = results[test_key]
            if prev_time > 0 and current_time > 0:
                delta = current_time - prev_time
                percent = (delta / prev_time) * 100 if prev_time > 0 else 0
                print(f"\n  {test_names[test_key]}")
                print(f"    Temps: {current_time:.2f}s")
                print(f"    Δ par rapport au test précédent: +{delta:.2f}s ({percent:+.1f}%)")
            prev_time = current_time

        # Identifier la contrainte la plus coûteuse
        print("\n" + "="*70)
        max_delta = 0
        max_delta_name = ""
        prev_time = 0

        for test_key in ["1_timeslot_par_cours", "2_un_cours_a_la_fois", "3_lien_sessions",
                        "4_taille_sessions", "5_max_1_par_jour", "6_avec_objectif"]:
            current_time = results[test_key]
            if prev_time > 0 and current_time > 0:
                delta = current_time - prev_time
                if delta > max_delta:
                    max_delta = delta
                    max_delta_name = test_names[test_key]
            prev_time = current_time

        if max_delta_name:
            print(f"🔥 CONTRAINTE LA PLUS COÛTEUSE:")
            print(f"   {max_delta_name}")
            print(f"   Impact: +{max_delta:.2f}s")

        print("\n" + "="*70)
        print("✅ Profilage terminé!")
        print("="*70)


def main():
    """Point d'entrée principal"""
    print("Chargement des données...")
    programs_requirements, teachers, classrooms, students, _ = generate_sample_data(
        num_students=56,
        use_csv_data=True
    )

    # Fusionner tous les requirements des programmes en un seul dict
    # (prendre le premier programme pour simplifier)
    course_requirements = list(programs_requirements.values())[0] if programs_requirements else {}

    print(f"✓ Données chargées: {len(students)} étudiants")

    # Créer le profileur et lancer les tests
    profiler = ConstraintProfiler(students, course_requirements)
    profiler.run_all_tests()


if __name__ == "__main__":
    main()
