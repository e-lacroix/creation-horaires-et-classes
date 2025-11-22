"""
Génère des données d'exemple pour le système d'horaires
Charge les données depuis les fichiers CSV et JSON ou génère des données par défaut
"""
# Configurer l'encodage UTF-8 en premier
import setup_encoding

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
                        use_csv_data: bool = True) -> Tuple[Dict[str, Dict[CourseType, int]], List[Teacher], List[Classroom], List[Student], int]:
    """
    Génère les données d'exemple selon les spécifications:
    - Charge depuis les CSV si use_csv_data=True et que les fichiers existent
    - Sinon, génère des données par défaut
    - Nombre d'étudiants/enseignants/salles configurable
    - Tous en Secondaire 4
    - Exigences de cours par programme (chaque programme a ses propres exigences)
    - Enseignants capables d'enseigner les cours
    - Salles de classe

    Args:
        num_students: Nombre d'étudiants à générer (défaut: 56)
        num_teachers: Nombre d'enseignants à générer (défaut: 13)
        num_classrooms: Nombre de salles à générer (défaut: 8)
        use_csv_data: Si True, essaie de charger depuis les CSV (défaut: True)

    Returns:
        (programs_requirements, teachers, classrooms, students, min_students_per_session)
        où programs_requirements est un Dict[str, Dict[CourseType, int]] = {program_name: {course: count}}
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
                       num_students, num_teachers, num_classrooms) -> Tuple[Dict[str, Dict[CourseType, int]], List[Teacher], List[Classroom], List[Student], int]:
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
        (programs_requirements, teachers, classrooms, students, min_students_per_session)
        où programs_requirements = {program_name: {course_type: count}}
    """
    from data_manager import DataManager

    data_manager = DataManager()

    # 1. Charger TOUS les programmes utilisés par les étudiants
    programmes = data_manager.lister_programmes()
    min_students_per_session = 20  # Valeur par défaut
    programs_requirements = {}  # Dict[str, Dict[CourseType, int]]

    if programmes:
        # Identifier les programmes uniques dans les données étudiantes
        unique_programs = set(eleve.programme for eleve in eleves_data if eleve.programme in programmes)

        # Charger chaque programme
        for program_name in unique_programs:
            programme = data_manager.charger_programme(program_name)
            if programme:
                programs_requirements[program_name] = programme.cours
                min_students_per_session = programme.min_etudiants_par_session

        # Si aucun programme chargé, utiliser les valeurs par défaut
        if not programs_requirements:
            programs_requirements["Défaut"] = get_course_requirements()
    else:
        programs_requirements["Défaut"] = get_course_requirements()

    # 2. Convertir les enseignants
    teachers = []
    mapping_matieres = {
        "Science": CourseType.SCIENCE,
        "STE": CourseType.STE,
        "ASC": CourseType.ASC,
        "Français": CourseType.FRANCAIS,
        "Math SN": CourseType.MATH_SN,
        "Math CST": CourseType.MATH_CST,
        "Anglais": CourseType.ANGLAIS,
        "Anglais avancé": CourseType.ANGLAIS_AVANCE,
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
        # Déterminer les matières autorisées en fonction du nom de la salle
        allowed_subjects = None
        if classe_data.matieres_autorisees:
            # Si les matières sont spécifiées dans le CSV
            allowed_subjects = []
            for matiere in classe_data.matieres_autorisees:
                if matiere in mapping_matieres:
                    allowed_subjects.append(mapping_matieres[matiere])
        else:
            # Sinon, déterminer automatiquement selon le nom
            nom_lower = classe_data.nom.lower()
            if "laboratoire" in nom_lower or "labo" in nom_lower:
                allowed_subjects = [CourseType.SCIENCE, CourseType.STE, CourseType.ASC]
            elif "gymnase" in nom_lower or "gym" in nom_lower:
                allowed_subjects = [CourseType.EDUC]
            elif "arts" in nom_lower or "art" in nom_lower:
                allowed_subjects = [CourseType.OPTION]
            elif "multimédia" in nom_lower or "multimedia" in nom_lower or "informatique" in nom_lower:
                allowed_subjects = [CourseType.HISTOIRE, CourseType.CCQ]
            else:
                # Salle régulière par défaut
                allowed_subjects = [CourseType.ESPAGNOL, CourseType.FRANCAIS, CourseType.MATH_SN, CourseType.MATH_CST, CourseType.ANGLAIS, CourseType.ANGLAIS_AVANCE]

        classrooms.append(Classroom(
            id=i + 1,
            name=classe_data.nom,
            capacity=classe_data.capacite,
            allowed_subjects=allowed_subjects
        ))

    # 4. Assigner les salles préférées aux enseignants
    classroom_dict = {c.id: c for c in classrooms}
    for i, ens_data in enumerate(enseignants_data[:num_teachers]):
        if i < len(teachers) and ens_data.classe_preferee:
            # Extraire le numéro de la classe (ex: "C003" -> 3)
            try:
                classe_id = int(ens_data.classe_preferee[1:])
                if classe_id in classroom_dict:
                    classroom = classroom_dict[classe_id]
                    # Ne pas permettre les gymnases comme salles préférées
                    if "gymnase" not in classroom.name.lower() and "gym" not in classroom.name.lower():
                        teachers[i].preferred_classroom = classroom
            except:
                pass

    # 5. Convertir les étudiants (en conservant le programme)
    students = []
    for i, eleve_data in enumerate(eleves_data[:num_students]):
        students.append(Student(
            id=i + 1,
            name=eleve_data.nom,
            grade=4,  # Tous en Secondaire 4
            program=eleve_data.programme  # Conserver le programme
        ))

    return programs_requirements, teachers, classrooms, students, min_students_per_session


def generate_default_data(num_students: int, num_teachers: int, num_classrooms: int) -> Tuple[Dict[str, Dict[CourseType, int]], List[Teacher], List[Classroom], List[Student], int]:
    """
    Génère des données par défaut (ancienne fonction generate_sample_data).

    Args:
        num_students: Nombre d'étudiants à générer
        num_teachers: Nombre d'enseignants à générer
        num_classrooms: Nombre de salles à générer

    Returns:
        (programs_requirements, teachers, classrooms, students, min_students_per_session)
        où programs_requirements = {program_name: {course_type: count}}
    """

    # Obtenir les exigences de cours par défaut
    course_requirements = get_course_requirements()
    programs_requirements = {"Secondaire 4 Régulier": course_requirements}

    # Créer les étudiants (nombre configurable, tous en Secondaire 4)
    students = []
    for i in range(num_students):
        students.append(Student(
            id=i + 1,
            name=f"Étudiant {i + 1}",
            grade=4,  # Tous en Secondaire 4
            program="Secondaire 4 Régulier"  # Programme par défaut
        ))

    # Créer les enseignants avec distribution intelligente
    teachers = []
    teacher_id = 1

    # Définir les spécialités d'enseignants avec leur poids (basé sur le nombre de cours)
    teacher_specialties = [
        ("Sciences", [CourseType.SCIENCE, CourseType.STE, CourseType.ASC], 8),  # 4+2+2 = 8 cours
        ("Français", [CourseType.FRANCAIS], 6),
        ("Mathématiques SN", [CourseType.MATH_SN], 6),
        ("Mathématiques CST", [CourseType.MATH_CST], 6),
        ("Anglais", [CourseType.ANGLAIS], 4),
        ("Anglais avancé", [CourseType.ANGLAIS_AVANCE], 4),
        ("Histoire", [CourseType.HISTOIRE, CourseType.CCQ], 6),  # 4+2 = 6 cours
        ("Espagnol", [CourseType.ESPAGNOL], 2),
        ("Éducation physique", [CourseType.EDUC], 2),  # 2 cours
        ("Option", [CourseType.OPTION], 2),  # 2 cours
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

    # Créer les salles de classe avec types spécifiques
    classrooms = []
    classroom_id = 1

    # Définir les types de salles nécessaires
    # Format: (nom_base, matières_autorisées, nombre_min, est_salle_preferee_possible)
    classroom_types = [
        ("Laboratoire", [CourseType.SCIENCE, CourseType.STE, CourseType.ASC], 2, True),
        ("Gymnase", [CourseType.EDUC], 1, False),  # Gymnase ne peut pas être une salle préférée
        ("Salle d'arts", [CourseType.OPTION], 1, True),
        ("Salle multimédia", [CourseType.HISTOIRE, CourseType.CCQ], 1, True),
        ("Salle régulière", [CourseType.ESPAGNOL, CourseType.FRANCAIS, CourseType.MATH_SN, CourseType.MATH_CST, CourseType.ANGLAIS, CourseType.ANGLAIS_AVANCE], 3, True),
    ]

    # Créer les salles selon les types
    for room_type_name, allowed_subjects, min_count, can_be_preferred in classroom_types:
        # Calculer combien de salles de ce type créer
        num_rooms = max(min_count, num_classrooms // len(classroom_types))

        # Limiter pour ne pas dépasser le total
        if classroom_id + num_rooms - 1 > num_classrooms:
            num_rooms = num_classrooms - classroom_id + 1

        for i in range(num_rooms):
            if classroom_id > num_classrooms:
                break

            room_name = f"{room_type_name} {i + 1}" if num_rooms > 1 else room_type_name
            classrooms.append(Classroom(
                id=classroom_id,
                name=room_name,
                capacity=32,
                allowed_subjects=allowed_subjects.copy()
            ))
            classroom_id += 1

        if classroom_id > num_classrooms:
            break

    # Si on n'a pas assez de salles, ajouter des salles régulières
    while len(classrooms) < num_classrooms:
        classrooms.append(Classroom(
            id=classroom_id,
            name=f"Salle régulière {classroom_id}",
            capacity=32,
            allowed_subjects=[CourseType.ESPAGNOL, CourseType.FRANCAIS, CourseType.MATH_SN, CourseType.MATH_CST, CourseType.ANGLAIS, CourseType.ANGLAIS_AVANCE]
        ))
        classroom_id += 1

    # Assigner une salle préférée à chaque enseignant
    # Filtrer les salles qui peuvent être préférées (pas les gymnases)
    preferable_classrooms = [c for c in classrooms if "Gymnase" not in c.name and "gymnase" not in c.name.lower()]

    for i, teacher in enumerate(teachers):
        if preferable_classrooms:
            # Essayer de trouver une salle compatible avec les matières enseignées
            compatible_rooms = [
                room for room in preferable_classrooms
                if any(course in room.allowed_subjects for course in teacher.can_teach)
            ]

            if compatible_rooms:
                teacher.preferred_classroom = compatible_rooms[i % len(compatible_rooms)]
            else:
                # Si aucune salle compatible, utiliser n'importe quelle salle préférable
                teacher.preferred_classroom = preferable_classrooms[i % len(preferable_classrooms)]

    return programs_requirements, teachers, classrooms, students, 20  # Minimum 20 étudiants par session par défaut


def group_students_by_program(students: List[Student]) -> Dict[str, List[Student]]:
    """
    Regroupe les étudiants par programme.

    Args:
        students: Liste de tous les étudiants

    Returns:
        Dictionnaire {program_name: [liste d'étudiants]}
    """
    from collections import defaultdict
    students_by_program = defaultdict(list)

    for student in students:
        program = student.program if student.program else "Défaut"
        students_by_program[program].append(student)

    return dict(students_by_program)


if __name__ == "__main__":
    # Test de génération
    programs_requirements, teachers, classrooms, students, min_students_per_session = generate_sample_data()

    print(f"Généré:")
    print(f"  - {len(programs_requirements)} programmes")
    print(f"  - {len(teachers)} enseignants")
    print(f"  - {len(classrooms)} salles")
    print(f"  - {len(students)} étudiants")
    print(f"  - Minimum {min_students_per_session} étudiants par session")

    # Afficher les étudiants par programme
    students_by_program = group_students_by_program(students)
    print("\nÉtudiants par programme:")
    for program_name, program_students in students_by_program.items():
        print(f"  {program_name}: {len(program_students)} étudiants")

    print("\nExigences de cours par programme:")
    for program_name, course_requirements in programs_requirements.items():
        total_courses = sum(course_requirements.values())
        print(f"\n  {program_name} ({total_courses} cours par étudiant):")
        for course_type, count in sorted(course_requirements.items(), key=lambda x: x[0].value):
            print(f"    {course_type.value}: {count} cours")
