"""
Script de diagnostic simplifié pour l'étape 3
Test direct de l'assignation enseignants/salles avec des sessions simulées
"""

from data_generator import generate_sample_data
from scheduler import ScheduleOptimizer
from models import CourseType, CourseSession, TimeSlot, Student
from collections import defaultdict

def test_assignment_feasibility():
    """Test de faisabilité de l'assignation avec des sessions simulées"""
    print("=" * 80)
    print("DIAGNOSTIC SIMPLIFIÉ - ÉTAPE 3")
    print("=" * 80)

    # Charger les données
    print("\nChargement des données...")
    programs_requirements, teachers, classrooms, students, min_group_size = generate_sample_data(num_students=56)

    print(f"  - {len(students)} étudiants")
    print(f"  - {len(teachers)} enseignants")
    print(f"  - {len(classrooms)} salles")

    # Analyser les ressources
    print("\n" + "=" * 80)
    print("ANALYSE DES RESSOURCES PAR TYPE DE COURS")
    print("=" * 80)

    teachers_by_course = defaultdict(list)
    for teacher in teachers:
        for course_type in teacher.can_teach:
            teachers_by_course[course_type].append(teacher)

    rooms_by_course = defaultdict(list)
    for room in classrooms:
        for course_type in room.allowed_subjects:
            rooms_by_course[course_type].append(room)

    print(f"\n{'Type de cours':<25} {'Enseignants':>12} {'Salles':>12}")
    print("-" * 80)

    resource_problems = []
    for course_type in CourseType:
        num_teachers = len(teachers_by_course[course_type])
        num_rooms = len(rooms_by_course[course_type])
        status = ""

        if num_teachers == 0 or num_rooms == 0:
            status = " ❌ BLOQUANT"
            resource_problems.append((course_type, num_teachers, num_rooms))
        elif num_teachers < 3 or num_rooms < 3:
            status = " ⚠️  RISQUE"

        print(f"{course_type.value:<25} {num_teachers:>12} {num_rooms:>12}{status}")

    if resource_problems:
        print("\n❌ PROBLÈMES CRITIQUES DÉTECTÉS:")
        print("=" * 80)
        for course_type, num_teachers, num_rooms in resource_problems:
            if num_teachers == 0:
                print(f"  • {course_type.value}: AUCUN enseignant qualifié!")
            if num_rooms == 0:
                print(f"  • {course_type.value}: AUCUNE salle autorisée!")
        print("\nSOLUTION:")
        print("  1. Vérifiez le fichier data/enseignants/enseignants.csv")
        print("  2. Vérifiez le fichier data/classes/classes.csv")
        print("  3. Assurez-vous que chaque type de cours a au moins un enseignant qualifié et une salle")
        return

    # Créer des sessions simulées pour tester l'assignation
    print("\n" + "=" * 80)
    print("SIMULATION DE SESSIONS POUR TESTER L'ASSIGNATION")
    print("=" * 80)

    # Créer des sessions simulées (une par type de cours au même timeslot pour tester les conflits)
    test_timeslot = TimeSlot(day=1, period=1)
    simulated_sessions = []

    # Prendre le premier programme pour le test
    first_program = list(programs_requirements.keys())[0]
    course_requirements = programs_requirements[first_program]

    session_id = 0
    for course_type in course_requirements.keys():
        session = CourseSession(
            id=session_id,
            course_type=course_type,
            timeslot=test_timeslot,
            assigned_teacher=None,
            assigned_room=None,
            students=students[:25]  # 25 étudiants par session pour le test
        )
        simulated_sessions.append(session)
        session_id += 1

    print(f"\nCréation de {len(simulated_sessions)} sessions simultanées au {test_timeslot}")
    print("(Pire scénario : toutes les matières en même temps)")

    # Vérifier la faisabilité
    print("\n" + "=" * 80)
    print("VÉRIFICATION DE FAISABILITÉ")
    print("=" * 80)

    conflicts = []
    course_counts = defaultdict(int)
    for session in simulated_sessions:
        course_counts[session.course_type] += 1

    for course_type, count in course_counts.items():
        available_teachers = len(teachers_by_course[course_type])
        available_rooms = len(rooms_by_course[course_type])

        if count > available_teachers:
            conflicts.append(f"  ❌ {course_type.value}: {count} sessions mais seulement {available_teachers} enseignants")
        if count > available_rooms:
            conflicts.append(f"  ❌ {course_type.value}: {count} sessions mais seulement {available_rooms} salles")

    if conflicts:
        print("\n❌ CONFLITS DÉTECTÉS (scénario pire cas):")
        for conflict in conflicts:
            print(conflict)
        print("\nCe scénario est impossible à résoudre, mais ne se produira probablement pas")
        print("car l'étape 2 répartit les sessions sur plusieurs timeslots.")
    else:
        print("\n✓ Pas de conflit dans le pire scénario")
        print("L'assignation devrait être possible si l'étape 2 répartit bien les sessions")

    # Test avec assignation réelle
    print("\n" + "=" * 80)
    print("TEST D'ASSIGNATION AVEC QUELQUES SESSIONS")
    print("=" * 80)

    # Créer quelques sessions réparties sur différents timeslots
    test_sessions = []
    session_id = 0

    # Créer 1 session par type de cours sur des timeslots différents
    period = 1
    day = 1
    for course_type in list(course_requirements.keys())[:5]:  # Prendre seulement 5 types pour le test
        session = CourseSession(
            id=session_id,
            course_type=course_type,
            timeslot=TimeSlot(day=day, period=period),
            assigned_teacher=None,
            assigned_room=None,
            students=students[:25]
        )
        test_sessions.append(session)
        session_id += 1
        period += 1
        if period > 4:
            period = 1
            day += 1

    print(f"\nTest avec {len(test_sessions)} sessions réparties sur {day} jour(s)")
    print("Lancement de l'assignation...")

    success, updated_sessions = ScheduleOptimizer.assign_teachers_and_rooms(
        test_sessions, teachers, classrooms
    )

    if success:
        print("✓ ASSIGNATION RÉUSSIE!")
        print("\nVérification des résultats:")
        for session in updated_sessions:
            teacher_status = "✓" if session.assigned_teacher else "❌"
            room_status = "✓" if session.assigned_room else "❌"
            print(f"  Session {session.id} ({session.course_type.value}): "
                  f"Enseignant {teacher_status}  Salle {room_status}")
    else:
        print("❌ ASSIGNATION ÉCHOUÉE!")
        print("\nPossibles causes:")
        print("  1. Contraintes trop restrictives dans le solveur")
        print("  2. Problème avec les contraintes de salles préférées")
        print("  3. Bug dans la logique d'assignation")
        print("\nRecommandations:")
        print("  - Examiner le code de scheduler.py:assign_teachers_and_rooms()")
        print("  - Vérifier les logs du solveur OR-Tools")
        print("  - Augmenter le timeout du solveur")


if __name__ == "__main__":
    test_assignment_feasibility()

    print("\n" + "=" * 80)
    print("FIN DU DIAGNOSTIC")
    print("=" * 80)
