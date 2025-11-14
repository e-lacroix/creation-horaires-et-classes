"""
Génère des données d'exemple pour le système d'horaires
Charge les données depuis les fichiers CSV et JSON ou génère des données par défaut
"""
from typing import List, Tuple, Dict
from models import Teacher, Classroom, Student, CourseType
from data_manager import DataManager
import os


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


def generate_sample_data(num_students: int = 56, num_teachers: int = 13, num_classrooms: int = 8,
                        use_csv_data: bool = True) -> Tuple[Dict[CourseType, int], List[Teacher], List[Classroom], List[Student]]:
    """
    Génère les données d'exemple selon les spécifications:
    - Charge depuis les CSV si use_csv_data=True et que les fichiers existent
    - Sinon, génère des données par défaut
    - Nombre d'étudiants/enseignants/salles configurable
    - Tous en Secondaire 4
    - Exigences de cours (chaque étudiant doit suivre tous les cours)
    - Enseignants capables d'enseigner les cours
    - Salles de classe

    Args:
        num_students: Nombre d'étudiants à générer (défaut: 56)
        num_teachers: Nombre d'enseignants à générer (défaut: 13)
        num_classrooms: Nombre de salles à générer (défaut: 8)
        use_csv_data: Si True, essaie de charger depuis les CSV (défaut: True)

    Returns:
        (course_requirements, teachers, classrooms, students)
    """

    # Essayer de charger depuis les CSV
    if use_csv_data:
        try:
            data_manager = DataManager()

            # Charger les données CSV
            eleves_data = data_manager.charger_eleves()
            enseignants_data = data_manager.charger_enseignants()
            classes_data = data_manager.charger_classes()

            # Si les données existent, les convertir
            if eleves_data and enseignants_data and classes_data:
                return load_data_from_csv(eleves_data, enseignants_data, classes_data,
                                         num_students, num_teachers, num_classrooms)
        except Exception as e:
            print(f"Erreur lors du chargement des CSV, utilisation des données par défaut: {e}")

    # Si pas de CSV ou erreur, générer des données par défaut
    return generate_default_data(num_students, num_teachers, num_classrooms)


def load_data_from_csv(eleves_data, enseignants_data, classes_data,
                       num_students, num_teachers, num_classrooms) -> Tuple[Dict[CourseType, int], List[Teacher], List[Classroom], List[Student]]:
    """
    Charge les données depuis les fichiers CSV et les convertit au format attendu.

    Args:
        eleves_data: Liste d'EleveData
        enseignants_data: Liste d'EnseignantData
        classes_data: Liste de ClasseData
        num_students: Nombre maximum d'étudiants à charger
        num_teachers: Nombre maximum d'enseignants à charger
        num_classrooms: Nombre maximum de salles à charger

    Returns:
        (course_requirements, teachers, classrooms, students)
    """
    from data_manager import DataManager

    data_manager = DataManager()

    # 1. Charger les exigences de cours depuis le premier programme trouvé
    programmes = data_manager.lister_programmes()
    if programmes:
        # Utiliser le premier élève pour déterminer quel programme charger
        if eleves_data and eleves_data[0].programme in programmes:
            programme = data_manager.charger_programme(eleves_data[0].programme)
        else:
            # Sinon charger le premier programme disponible
            programme = data_manager.charger_programme(programmes[0])

        if programme:
            course_requirements = programme.cours
        else:
            course_requirements = get_course_requirements()
    else:
        course_requirements = get_course_requirements()

    # 2. Convertir les enseignants
    teachers = []
    mapping_matieres = {
        "Science": CourseType.SCIENCE,
        "STE": CourseType.STE,
        "ASC": CourseType.ASC,
        "Français": CourseType.FRANCAIS,
        "Math SN": CourseType.MATH_SN,
        "Anglais": CourseType.ANGLAIS,
        "Histoire": CourseType.HISTOIRE,
        "CCQ": CourseType.CCQ,
        "Espagnol": CourseType.ESPAGNOL,
        "Éducation physique": CourseType.EDUC,
        "Option": CourseType.OPTION
    }

    for i, ens_data in enumerate(enseignants_data[:num_teachers]):
        # Convertir les matières en CourseType
        can_teach = []
        for matiere in ens_data.matieres:
            if matiere in mapping_matieres:
                can_teach.append(mapping_matieres[matiere])

        teachers.append(Teacher(
            id=i + 1,
            name=ens_data.nom,
            can_teach=can_teach
        ))

    # 3. Convertir les salles de classe
    classrooms = []
    for i, classe_data in enumerate(classes_data[:num_classrooms]):
        classrooms.append(Classroom(
            id=i + 1,
            name=classe_data.nom,
            capacity=classe_data.capacite
        ))

    # 4. Assigner les salles préférées aux enseignants
    classroom_dict = {c.id: c for c in classrooms}
    for i, ens_data in enumerate(enseignants_data[:num_teachers]):
        if i < len(teachers) and ens_data.classe_preferee:
            # Extraire le numéro de la classe (ex: "C003" -> 3)
            try:
                classe_id = int(ens_data.classe_preferee[1:])
                if classe_id in classroom_dict:
                    teachers[i].preferred_classroom = classroom_dict[classe_id]
            except:
                pass

    # 5. Convertir les étudiants
    students = []
    for i, eleve_data in enumerate(eleves_data[:num_students]):
        students.append(Student(
            id=i + 1,
            name=eleve_data.nom,
            grade=4  # Tous en Secondaire 4
        ))

    return course_requirements, teachers, classrooms, students


def generate_default_data(num_students: int, num_teachers: int, num_classrooms: int) -> Tuple[Dict[CourseType, int], List[Teacher], List[Classroom], List[Student]]:
    """
    Génère des données par défaut (ancienne fonction generate_sample_data).

    Args:
        num_students: Nombre d'étudiants à générer
        num_teachers: Nombre d'enseignants à générer
        num_classrooms: Nombre de salles à générer

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
