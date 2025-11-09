"""
Script de test pour vérifier l'optimiseur d'horaires
"""
from data_generator import generate_sample_data
from scheduler import ScheduleOptimizer


def test_optimizer(num_students: int):
    """Test l'optimiseur avec un nombre donné d'étudiants"""
    print(f"\n{'='*70}")
    print(f"TEST AVEC {num_students} ÉTUDIANTS")
    print(f"{'='*70}\n")

    # Générer les données
    print("Génération des données...")
    course_requirements, teachers, classrooms, students = generate_sample_data(num_students)

    total_courses = sum(course_requirements.values())
    print(f"[OK] {num_students} etudiants")
    print(f"[OK] {total_courses} cours requis par etudiant")
    print(f"[OK] {len(teachers)} enseignants")
    print(f"[OK] {len(classrooms)} salles")

    # Optimisation
    print("\nLancement de l'optimisation...")
    optimizer = ScheduleOptimizer(
        teachers,
        classrooms,
        students,
        course_requirements
    )

    success, sessions, student_schedules = optimizer.solve()

    if success:
        print(f"\n[OK] SUCCES ! Solution trouvee")
        print(f"\nResultats:")
        print(f"  - Sessions creees: {len(sessions)}")
        print(f"  - Etudiants avec horaire: {len(student_schedules)}")

        # Statistiques des sessions
        session_sizes = [len(session.students) for session in sessions]
        print(f"\n  Distribution des etudiants par session:")
        print(f"    - Min: {min(session_sizes)} etudiants")
        print(f"    - Max: {max(session_sizes)} etudiants")
        print(f"    - Moyenne: {sum(session_sizes)/len(session_sizes):.1f} etudiants")

        # Enseignants utilisés
        teachers_used = set()
        for session in sessions:
            if session.assigned_teacher:
                teachers_used.add(session.assigned_teacher.name)
        print(f"\n  Ressources utilisees:")
        print(f"    - Enseignants: {len(teachers_used)}/{len(teachers)}")

        # Salles utilisées
        rooms_used = set()
        for session in sessions:
            if session.assigned_room:
                rooms_used.add(session.assigned_room.name)
        print(f"    - Salles: {len(rooms_used)}/{len(classrooms)}")

        # Efficacité
        total_potential = num_students * total_courses
        efficiency = (1 - len(sessions) / total_potential) * 100
        print(f"\n  Efficacite de regroupement: {efficiency:.1f}%")

        # Vérifications
        print(f"\n  Verifications:")
        all_schedules_valid = True
        for student in students:
            schedule = student_schedules.get(student.id, [])
            if len(schedule) != total_courses:
                print(f"    [ERREUR] Etudiant {student.id} a {len(schedule)} cours au lieu de {total_courses}")
                all_schedules_valid = False

        if all_schedules_valid:
            print(f"    [OK] Tous les etudiants ont leurs {total_courses} cours")

        # Vérifier les conflits de timeslot pour chaque étudiant
        conflicts = 0
        for student in students:
            schedule = student_schedules.get(student.id, [])
            timeslots_used = {}
            for entry in schedule:
                key = (entry.timeslot.day, entry.timeslot.period)
                if key in timeslots_used:
                    conflicts += 1
                timeslots_used[key] = entry

        if conflicts == 0:
            print(f"    [OK] Aucun conflit de timeslot pour les etudiants")
        else:
            print(f"    [ERREUR] {conflicts} conflits de timeslot detectes")

        return True
    else:
        print(f"\n[ERREUR] ECHEC - Aucune solution trouvee")
        return False


if __name__ == "__main__":
    print("TESTS DE L'OPTIMISEUR D'HORAIRES")
    print("=" * 70)

    # Tests avec différents nombres d'étudiants
    test_cases = [5, 10, 20, 56]
    results = {}

    for num_students in test_cases:
        results[num_students] = test_optimizer(num_students)

    # Résumé
    print(f"\n\n{'='*70}")
    print("RESUME DES TESTS")
    print(f"{'='*70}")
    for num_students, success in results.items():
        status = "[OK] SUCCES" if success else "[ERREUR] ECHEC"
        print(f"  {num_students:3d} etudiants: {status}")

    print(f"\n{'='*70}\n")
