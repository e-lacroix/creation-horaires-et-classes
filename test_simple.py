"""
Test simple pour verifier rapidement l'optimiseur
"""
from data_generator import generate_sample_data
from scheduler import ScheduleOptimizer

print("Test rapide de l'optimiseur avec 3 etudiants")
print("=" * 60)

# Générer les données pour 3 étudiants
course_requirements, teachers, classrooms, students = generate_sample_data(3)

total_courses = sum(course_requirements.values())
print(f"\n[OK] Donnees generees:")
print(f"  - 3 etudiants")
print(f"  - {total_courses} cours par etudiant")
print(f"  - {len(teachers)} enseignants")
print(f"  - {len(classrooms)} salles")

# Optimisation
print(f"\nLancement de l'optimisation...")
optimizer = ScheduleOptimizer(
    teachers,
    classrooms,
    students,
    course_requirements
)

success, sessions, student_schedules = optimizer.solve()

if success:
    print(f"\n[OK] Solution trouvee !\n")
    print(f"Resultats:")
    print(f"  - Sessions creees: {len(sessions)}")
    print(f"  - Etudiants avec horaire: {len(student_schedules)}")

    # Vérifier que chaque étudiant a tous ses cours
    print(f"\nVerification des horaires:")
    for student in students:
        schedule = student_schedules.get(student.id, [])
        status = "[OK]" if len(schedule) == total_courses else "[ERREUR]"
        print(f"  {status} Etudiant {student.id}: {len(schedule)}/{total_courses} cours")

    # Afficher quelques détails des sessions
    print(f"\nExemple de sessions (premiers 10):")
    for i, session in enumerate(sessions[:10]):
        print(f"  Session {i+1}: {session.course_type.value} - Jour {session.timeslot.day} Periode {session.timeslot.period}")
        print(f"             {len(session.students)} etudiants, Prof: {session.assigned_teacher.name if session.assigned_teacher else 'N/A'}")

    print(f"\n[OK] Test reussi !")
else:
    print(f"\n[ERREUR] Echec de l'optimisation")

print(f"\n" + "=" * 60)
