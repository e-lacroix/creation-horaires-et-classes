"""
Génère des données d'exemple pour le système d'horaires
"""
from typing import List, Tuple, Dict
from models import Teacher, Classroom, Student, CourseType


def get_course_requirements() -> Dict[CourseType, int]:
    """
    Retourne les exigences de cours pour Secondaire 4 au Québec

    Returns:
        Dictionnaire {CourseType: nombre_de_cours}
    """
    return {
        CourseType.SCIENCE: 4,
        CourseType.STE: 2,
        CourseType.ASC: 2,
        CourseType.FRANCAIS: 6,
        CourseType.MATH_SN: 6,
        CourseType.ANGLAIS: 4,
        CourseType.HISTOIRE: 4,
        CourseType.CCQ: 2,
        CourseType.ESPAGNOL: 2,
        CourseType.EDUC: 2,
        CourseType.OPTION: 2,
    }


def generate_sample_data(num_students: int = 56, num_teachers: int = 13, num_classrooms: int = 8) -> Tuple[Dict[CourseType, int], List[Teacher], List[Classroom], List[Student]]:
    """
    Génère les données d'exemple selon les spécifications:
    - Nombre d'étudiants configurable (par défaut 56)
    - Nombre d'enseignants configurable (par défaut 13)
    - Nombre de salles configurable (par défaut 8)
    - Tous en Secondaire 4
    - Exigences de cours (chaque étudiant doit suivre tous les cours)
    - Enseignants capables d'enseigner les cours
    - Salles de classe

    Args:
        num_students: Nombre d'étudiants à générer (défaut: 56)
        num_teachers: Nombre d'enseignants à générer (défaut: 13)
        num_classrooms: Nombre de salles à générer (défaut: 8)

    Returns:
        (course_requirements, teachers, classrooms, students)
    """

    # Créer les étudiants (nombre configurable, tous en Secondaire 4)
    students = []
    for i in range(num_students):
        students.append(Student(
            id=i + 1,
            name=f"Étudiant {i + 1}",
            grade=4  # Tous en Secondaire 4
        ))

    # Obtenir les exigences de cours
    course_requirements = get_course_requirements()

    # Créer les enseignants avec distribution intelligente
    teachers = []
    teacher_id = 1

    # Définir les spécialités d'enseignants avec leur poids (basé sur le nombre de cours)
    teacher_specialties = [
        ("Sciences", [CourseType.SCIENCE, CourseType.STE, CourseType.ASC], 8),  # 4+2+2 = 8 cours
        ("Français", [CourseType.FRANCAIS], 6),
        ("Mathématiques", [CourseType.MATH_SN], 6),
        ("Anglais", [CourseType.ANGLAIS], 4),
        ("Histoire", [CourseType.HISTOIRE, CourseType.CCQ], 6),  # 4+2 = 6 cours
        ("Espagnol", [CourseType.ESPAGNOL], 2),
        ("Éducation physique", [CourseType.EDUC, CourseType.OPTION], 4),  # 2+2 = 4 cours
    ]

    # Calculer le poids total
    total_weight = sum(weight for _, _, weight in teacher_specialties)

    # Distribuer les enseignants selon le poids de chaque spécialité
    teachers_assigned = 0
    for specialty_name, can_teach, weight in teacher_specialties:
        # Calculer combien d'enseignants pour cette spécialité (au minimum 1)
        num_for_specialty = max(1, round((weight / total_weight) * num_teachers))

        # S'assurer qu'on ne dépasse pas le nombre total
        if teachers_assigned + num_for_specialty > num_teachers:
            num_for_specialty = num_teachers - teachers_assigned

        for i in range(num_for_specialty):
            teachers.append(Teacher(
                id=teacher_id,
                name=f"Prof. {specialty_name} {i + 1}" if num_for_specialty > 1 else f"Prof. {specialty_name}",
                can_teach=can_teach
            ))
            teacher_id += 1
            teachers_assigned += 1

            if teachers_assigned >= num_teachers:
                break

        if teachers_assigned >= num_teachers:
            break

    # S'il manque des enseignants, ajouter des généralistes (peuvent enseigner plusieurs matières)
    while teachers_assigned < num_teachers:
        # Créer un enseignant polyvalent avec plusieurs compétences
        multi_subjects = [CourseType.SCIENCE, CourseType.STE, CourseType.ASC,
                         CourseType.FRANCAIS, CourseType.MATH_SN, CourseType.ANGLAIS]
        teachers.append(Teacher(
            id=teacher_id,
            name=f"Prof. Polyvalent {teachers_assigned - len(teacher_specialties) + 1}",
            can_teach=multi_subjects
        ))
        teacher_id += 1
        teachers_assigned += 1

    # Créer les salles de classe
    classrooms = []
    for i in range(num_classrooms):
        classrooms.append(Classroom(
            id=i + 1,
            name=f"Salle {i + 1}",
            capacity=28
        ))

    # Assigner une salle préférée à chaque enseignant
    # Les enseignants partagent des salles si nécessaire (distribution cyclique)
    for i, teacher in enumerate(teachers):
        teacher.preferred_classroom = classrooms[i % len(classrooms)]

    return course_requirements, teachers, classrooms, students


if __name__ == "__main__":
    # Test de génération
    course_requirements, teachers, classrooms, students = generate_sample_data()

    print(f"Généré:")
    total_courses = sum(course_requirements.values())
    print(f"  - {total_courses} cours requis par étudiant")
    print(f"  - {len(teachers)} enseignants")
    print(f"  - {len(classrooms)} salles")
    print(f"  - {len(students)} étudiants")

    print("\nExigences de cours (par étudiant):")
    for course_type, count in sorted(course_requirements.items(), key=lambda x: x[0].value):
        print(f"  {course_type.value}: {count} cours")
