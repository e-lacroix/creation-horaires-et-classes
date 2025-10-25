"""
Génère des données d'exemple pour le système d'horaires
"""
from typing import List, Tuple
from models import Course, Teacher, Classroom, Student, CourseType


def generate_sample_data(num_students: int = 56) -> Tuple[List[Course], List[Teacher], List[Classroom], List[Student]]:
    """
    Génère les données d'exemple selon les spécifications:
    - Nombre d'étudiants configurable (par défaut 56)
    - Tous en Secondaire 4
    - Cours requis avec le bon nombre de classes
    - Enseignants capables d'enseigner les cours
    - Salles de classe

    Args:
        num_students: Nombre d'étudiants à générer (défaut: 56)
    """

    # Créer les étudiants (nombre configurable, tous en Secondaire 4)
    students = []
    for i in range(num_students):
        students.append(Student(
            id=i + 1,
            name=f"Étudiant {i + 1}",
            grade=4  # Tous en Secondaire 4
        ))

    # Créer les cours selon les spécifications
    courses = []
    course_id = 1

    course_specs = [
        (CourseType.SCIENCE, 4),
        (CourseType.STE, 2),
        (CourseType.ASC, 2),
        (CourseType.FRANCAIS, 6),
        (CourseType.MATH_SN, 6),
        (CourseType.ANGLAIS, 4),
        (CourseType.HISTOIRE, 4),
        (CourseType.CCQ, 2),
        (CourseType.ESPAGNOL, 2),
        (CourseType.EDUC, 2),
        (CourseType.OPTION, 2),
    ]

    for course_type, count in course_specs:
        for _ in range(count):
            courses.append(Course(
                id=course_id,
                course_type=course_type,
                max_students=28
            ))
            course_id += 1

    # Créer les enseignants (minimiser le nombre)
    teachers = []
    teacher_id = 1

    # Enseignants de sciences (peuvent enseigner Science, STE, ASC)
    for i in range(3):
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Sciences {i + 1}",
            can_teach=[CourseType.SCIENCE, CourseType.STE, CourseType.ASC]
        ))
        teacher_id += 1

    # Enseignants de français
    for i in range(2):
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Français {i + 1}",
            can_teach=[CourseType.FRANCAIS]
        ))
        teacher_id += 1

    # Enseignants de mathématiques
    for i in range(2):
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Mathématiques {i + 1}",
            can_teach=[CourseType.MATH_SN]
        ))
        teacher_id += 1

    # Enseignants d'anglais
    for i in range(2):
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Anglais {i + 1}",
            can_teach=[CourseType.ANGLAIS]
        ))
        teacher_id += 1

    # Enseignants d'histoire et CCQ
    for i in range(2):
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Histoire {i + 1}",
            can_teach=[CourseType.HISTOIRE, CourseType.CCQ]
        ))
        teacher_id += 1

    # Enseignant d'espagnol
    teachers.append(Teacher(
        id=teacher_id,
        name="Prof. Espagnol",
        can_teach=[CourseType.ESPAGNOL]
    ))
    teacher_id += 1

    # Enseignant d'éducation physique et option
    teachers.append(Teacher(
        id=teacher_id,
        name="Prof. Éducation physique",
        can_teach=[CourseType.EDUC, CourseType.OPTION]
    ))
    teacher_id += 1

    # Créer les salles de classe (minimiser le nombre)
    classrooms = []
    # On a besoin de max 4 salles utilisées simultanément (4 périodes par jour)
    for i in range(8):
        classrooms.append(Classroom(
            id=i + 1,
            name=f"Salle {i + 1}",
            capacity=28
        ))

    return courses, teachers, classrooms, students


if __name__ == "__main__":
    # Test de génération
    courses, teachers, classrooms, students = generate_sample_data()

    print(f"Généré:")
    print(f"  - {len(courses)} cours")
    print(f"  - {len(teachers)} enseignants")
    print(f"  - {len(classrooms)} salles")
    print(f"  - {len(students)} étudiants")

    print("\nRépartition des cours:")
    course_counts = {}
    for course in courses:
        course_type = course.course_type.value
        course_counts[course_type] = course_counts.get(course_type, 0) + 1

    for course_type, count in sorted(course_counts.items()):
        print(f"  {course_type}: {count}")
