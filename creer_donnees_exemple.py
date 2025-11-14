"""
Script pour créer des données d'exemple pour les élèves, enseignants et classes.
"""
from data_manager import (
    DataManager, Programme, EleveData, EnseignantData, ClasseData,
    creer_programmes_par_defaut
)
from models import CourseType
import random


def creer_donnees_exemple():
    """Crée des fichiers CSV d'exemple avec des données réalistes."""

    data_manager = DataManager()

    # 1. Créer les programmes par défaut
    print("Création des programmes par défaut...")
    creer_programmes_par_defaut(data_manager)
    print(f"Programmes créés: {', '.join(data_manager.lister_programmes())}")

    # 2. Créer des élèves d'exemple
    print("\nCréation des élèves d'exemple...")
    eleves = []
    prenoms = ["Alice", "Bob", "Charlie", "David", "Emma", "Félix", "Gabriel", "Hannah",
               "Isaac", "Jade", "Kevin", "Laura", "Marc", "Nina", "Olivier", "Patricia",
               "Quentin", "Rose", "Simon", "Thérèse"]
    noms = ["Tremblay", "Gagnon", "Roy", "Côté", "Bouchard", "Gauthier", "Morin", "Lavoie",
            "Fortin", "Gagné", "Ouellet", "Pelletier", "Bélanger", "Leblanc", "Bergeron"]

    matieres_talents = ["Science", "STE", "ASC", "Français", "Math SN", "Anglais", "Histoire",
                       "CCQ", "Espagnol", "Éducation physique", "Option"]

    programmes_disponibles = ["Secondaire 4 Régulier", "Secondaire 4 Sciences"]

    for i in range(56):  # 56 élèves par défaut
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        identifiant = f"E{i+1:04d}"
        programme = random.choice(programmes_disponibles)

        # Générer quelques restrictions (20% des élèves ont des restrictions)
        restrictions = ""
        if random.random() < 0.2:
            jours_possibles = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
            periodes_possibles = ["matin", "apres_midi"]
            nb_restrictions = random.randint(1, 2)
            rest_list = []
            for _ in range(nb_restrictions):
                jour = random.choice(jours_possibles)
                periode = random.choice(periodes_possibles)
                rest_list.append(f"{jour}_{periode}")
            restrictions = ",".join(rest_list)

        # Générer des talents (notes de 0.3 à 1.0)
        talents = {}
        for matiere in matieres_talents:
            talents[matiere] = round(random.uniform(0.3, 1.0), 2)

        eleves.append(EleveData(
            nom=f"{prenom} {nom}",
            identifiant=identifiant,
            programme=programme,
            restrictions=restrictions,
            talents=talents
        ))

    data_manager.sauvegarder_eleves(eleves, "eleves.csv")
    print(f"[OK] {len(eleves)} eleves crees dans data/eleves/eleves.csv")

    # 3. Créer des enseignants d'exemple
    print("\nCréation des enseignants d'exemple...")
    enseignants = []
    noms_enseignants = [
        ("Marie Dubois", ["Science", "STE", "ASC"]),
        ("Jean Martin", ["Science", "STE"]),
        ("Sophie Bernard", ["Français"]),
        ("Pierre Lefevre", ["Français"]),
        ("Isabelle Morin", ["Math SN"]),
        ("François Girard", ["Math SN"]),
        ("Catherine Leblanc", ["Anglais"]),
        ("Michel Roy", ["Anglais"]),
        ("Julie Gagnon", ["Histoire", "CCQ"]),
        ("Robert Tremblay", ["Histoire"]),
        ("Nathalie Bouchard", ["Espagnol"]),
        ("Daniel Fortin", ["Éducation physique", "Option"]),
        ("Sylvie Pelletier", ["Option", "CCQ"])
    ]

    for i, (nom, matieres) in enumerate(noms_enseignants):
        identifiant = f"T{i+1:03d}"

        # 10% des enseignants ont des restrictions
        restrictions = ""
        if random.random() < 0.1:
            restrictions = "mercredi_matin"

        # Classe préférée aléatoire
        classe_preferee = f"C{random.randint(1, 8):03d}"

        enseignants.append(EnseignantData(
            nom=nom,
            identifiant=identifiant,
            matieres=matieres,
            restrictions=restrictions,
            classe_preferee=classe_preferee
        ))

    data_manager.sauvegarder_enseignants(enseignants, "enseignants.csv")
    print(f"[OK] {len(enseignants)} enseignants crees dans data/enseignants/enseignants.csv")

    # 4. Créer des classes d'exemple
    print("\nCréation des classes d'exemple...")
    classes = []

    # Définition des types de salles avec matières autorisées
    types_salles = [
        ("Laboratoire Science 1", 28, ["Science", "STE", "ASC"]),
        ("Laboratoire Science 2", 28, ["Science", "STE", "ASC"]),
        ("Salle régulière 1", 30, ["Français", "Math SN", "Anglais", "Histoire", "CCQ", "Espagnol"]),
        ("Salle régulière 2", 30, ["Français", "Math SN", "Anglais", "Histoire", "CCQ", "Espagnol"]),
        ("Salle régulière 3", 30, ["Français", "Math SN", "Anglais", "Histoire", "CCQ", "Espagnol"]),
        ("Salle multimédia", 25, ["Anglais", "Espagnol", "Option"]),
        ("Gymnase", 35, ["Éducation physique"]),
        ("Salle d'arts", 25, ["Option"])
    ]

    for i, (nom, capacite, matieres) in enumerate(types_salles):
        identifiant = f"C{i+1:03d}"
        classes.append(ClasseData(
            identifiant=identifiant,
            nom=nom,
            capacite=capacite,
            matieres_autorisees=matieres
        ))

    data_manager.sauvegarder_classes(classes, "classes.csv")
    print(f"[OK] {len(classes)} classes creees dans data/classes/classes.csv")

    print("\n" + "="*60)
    print("[OK] Toutes les donnees d'exemple ont ete creees avec succes!")
    print("="*60)
    print("\nStructure des dossiers:")
    print("data/")
    print("  - programmes/")
    print("      - Secondaire 4 Regulier.json")
    print("      - Secondaire 4 Sciences.json")
    print("  - eleves/")
    print("      - eleves.csv")
    print("  - enseignants/")
    print("      - enseignants.csv")
    print("  - classes/")
    print("      - classes.csv")
    print("\nVous pouvez maintenant modifier ces fichiers selon vos besoins!")


if __name__ == "__main__":
    creer_donnees_exemple()
