"""
Script de diagnostic pour identifier les problèmes avec l'étape 3
(assignation des enseignants et salles)
"""

from data_generator import generate_sample_data
from scheduler import ScheduleOptimizer
from models import CourseType, CourseSession, TimeSlot
from collections import defaultdict

def analyze_resources():
    """Analyse les ressources disponibles (enseignants et salles)"""
    print("=" * 80)
    print("ANALYSE DES RESSOURCES DISPONIBLES")
    print("=" * 80)

    # Charger les données
    programs_requirements, teachers, classrooms, students, min_group_size = generate_sample_data(num_students=56)

    # Extraire tous les types de cours requis
    all_course_types = set()
    for reqs in programs_requirements.values():
        all_course_types.update(reqs.keys())

    # Analyser les enseignants par type de cours
    print("\n1. ENSEIGNANTS PAR TYPE DE COURS:")
    print("-" * 80)
    teachers_by_course = defaultdict(list)
    for teacher in teachers:
        for course_type in teacher.can_teach:
            teachers_by_course[course_type].append(teacher.name)

    for course_type in CourseType:
        count = len(teachers_by_course[course_type])
        print(f"{course_type.value:25} : {count:2} enseignants")
        if count == 0:
            print(f"  ⚠️  AUCUN ENSEIGNANT QUALIFIÉ!")
        elif count < 3:
            print(f"  ⚠️  Peu d'enseignants (risque de conflit)")

    # Analyser les salles par type de cours
    print("\n2. SALLES PAR TYPE DE COURS:")
    print("-" * 80)
    rooms_by_course = defaultdict(list)
    for room in classrooms:
        for course_type in room.allowed_subjects:
            rooms_by_course[course_type].append(room.name)

    for course_type in CourseType:
        count = len(rooms_by_course[course_type])
        print(f"{course_type.value:25} : {count:2} salles")
        if count == 0:
            print(f"  ⚠️  AUCUNE SALLE AUTORISÉE!")
        elif count < 3:
            print(f"  ⚠️  Peu de salles (risque de conflit)")

    return programs_requirements, teachers, classrooms, students, min_group_size


def test_step2():
    """Test de l'étape 2 pour générer des sessions"""
    print("\n" + "=" * 80)
    print("TEST DE L'ÉTAPE 2 (Génération des horaires étudiants)")
    print("=" * 80)

    programs_requirements, teachers, classrooms, students, min_group_size = generate_sample_data(num_students=56)

    # Utiliser le premier programme disponible pour le test
    first_program = list(programs_requirements.keys())[0]
    course_requirements = programs_requirements[first_program]

    print(f"\nConfiguration:")
    print(f"  - {len(students)} étudiants")
    print(f"  - {len(teachers)} enseignants")
    print(f"  - {len(classrooms)} salles")
    print(f"  - {sum(course_requirements.values())} cours par étudiant (programme: {first_program})")

    # Créer l'optimiseur
    optimizer = ScheduleOptimizer(teachers, classrooms, students, course_requirements)

    # Exécuter l'étape 2
    print("\nExécution de l'étape 2...")
    success, sessions, student_schedules = optimizer.solve_student_schedules_only()

    if not success:
        print("❌ L'étape 2 a échoué!")
        return None, None, None, None

    print(f"✓ Étape 2 réussie: {len(sessions)} sessions créées")

    # Analyser les sessions par timeslot
    sessions_by_timeslot = defaultdict(list)
    for session in sessions:
        sessions_by_timeslot[session.timeslot].append(session)

    max_sessions_per_timeslot = max(len(sessions_list) for sessions_list in sessions_by_timeslot.values())
    print(f"\nMaximum de sessions simultanées: {max_sessions_per_timeslot}")

    # Vérifier s'il y a des timeslots avec beaucoup de sessions
    problematic_timeslots = []
    for timeslot, session_list in sessions_by_timeslot.items():
        if len(session_list) > len(teachers) or len(session_list) > len(classrooms):
            problematic_timeslots.append((timeslot, len(session_list)))

    if problematic_timeslots:
        print("\n⚠️  TIMESLOTS PROBLÉMATIQUES (plus de sessions que de ressources):")
        for timeslot, count in problematic_timeslots[:5]:
            print(f"  - {timeslot}: {count} sessions (vs {len(teachers)} enseignants, {len(classrooms)} salles)")

    return sessions, teachers, classrooms, students


def test_step3(sessions, teachers, classrooms):
    """Test de l'étape 3 avec analyse détaillée"""
    print("\n" + "=" * 80)
    print("TEST DE L'ÉTAPE 3 (Assignation des enseignants et salles)")
    print("=" * 80)

    if not sessions:
        print("❌ Pas de sessions disponibles pour le test")
        return

    # Analyser les conflits potentiels par timeslot
    print("\nAnalyse des conflits potentiels:")
    print("-" * 80)

    sessions_by_timeslot = defaultdict(list)
    for session in sessions:
        sessions_by_timeslot[session.timeslot].append(session)

    # Vérifier chaque timeslot
    critical_timeslots = []
    for timeslot, session_list in sessions_by_timeslot.items():
        # Compter les enseignants et salles nécessaires
        required_teachers = defaultdict(int)
        required_rooms = defaultdict(int)

        for session in session_list:
            # Compter combien d'enseignants qualifiés pour ce type de cours
            qualified_teachers = [t for t in teachers if session.course_type in t.can_teach]
            required_teachers[session.course_type] = len(qualified_teachers)

            # Compter combien de salles autorisées pour ce type de cours
            allowed_rooms = [r for r in classrooms if session.course_type in r.allowed_subjects]
            required_rooms[session.course_type] = len(allowed_rooms)

        # Vérifier les conflits
        course_counts = defaultdict(int)
        for session in session_list:
            course_counts[session.course_type] += 1

        has_conflict = False
        for course_type, count in course_counts.items():
            if count > required_teachers[course_type]:
                print(f"⚠️  {timeslot}: {count} sessions de {course_type.value} mais seulement {required_teachers[course_type]} enseignants qualifiés")
                has_conflict = True
            if count > required_rooms[course_type]:
                print(f"⚠️  {timeslot}: {count} sessions de {course_type.value} mais seulement {required_rooms[course_type]} salles autorisées")
                has_conflict = True

        if has_conflict:
            critical_timeslots.append(timeslot)

    if critical_timeslots:
        print(f"\n❌ {len(critical_timeslots)} timeslots avec des conflits détectés")
        print("\nRECOMMANDATIONS:")
        print("1. Augmenter le nombre d'enseignants pour les matières en conflit")
        print("2. Augmenter le nombre de salles autorisées pour ces matières")
        print("3. Modifier les paramètres de taille de groupe pour réduire le nombre de sessions simultanées")
    else:
        print("\n✓ Aucun conflit évident détecté")
        print("\nExécution de l'étape 3...")
        success, updated_sessions = ScheduleOptimizer.assign_teachers_and_rooms(
            sessions, teachers, classrooms
        )

        if success:
            print("✓ Étape 3 réussie!")
        else:
            print("❌ Étape 3 a échoué malgré l'absence de conflits évidents")
            print("\nCauses possibles:")
            print("1. Contraintes trop restrictives (salles préférées)")
            print("2. Restrictions d'enseignants non prises en compte")
            print("3. Problème dans la logique du solveur")


if __name__ == "__main__":
    # Étape 1: Analyser les ressources
    analyze_resources()

    # Étape 2: Tester la génération des sessions
    sessions, teachers, classrooms, students = test_step2()

    # Étape 3: Tester l'assignation
    if sessions:
        test_step3(sessions, teachers, classrooms)

    print("\n" + "=" * 80)
    print("FIN DU DIAGNOSTIC")
    print("=" * 80)
