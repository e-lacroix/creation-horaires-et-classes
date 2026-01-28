"""
Script pour créer des données d'exemple pour les élèves, enseignants et classes.
"""
# Configurer l'encodage UTF-8 en premier
import setup_encoding

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

    matieres_talents = ["Science", "STE", "ASC", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé", "Histoire",
                       "CCQ", "Espagnol", "Éducation physique", "Option", "Arts"]

    # Répartition des élèves :
    # - 63 élèves en Excellence
    # - 57 élèves en Régulier
    # - 56 élèves en Régulier SN
    # Total : 176 élèves

    total_eleves = 176
    programmes_repartition = [
        ("Secondaire 4 Excellence", 63),
        ("Secondaire 4 Régulier", 57),
        ("Secondaire 4 Régulier SN", 56)
    ]

    eleve_id = 1
    for programme_nom, nb_eleves in programmes_repartition:
        for i in range(nb_eleves):
            prenom = random.choice(prenoms)
            nom = random.choice(noms)
            identifiant = f"E{eleve_id:04d}"
            programme = programme_nom
            eleve_id += 1

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
    # Double le nombre d'enseignants pour 176 élèves (environ 76 enseignants)
    print("\nCréation des enseignants d'exemple...")
    enseignants = []
    noms_enseignants = [
        # Sciences (12 enseignants - doublé)
        ("Marie Dubois", ["Science", "STE", "ASC"], False),
        ("Jean Martin", ["Science", "STE"], False),
        ("Claude Fortin", ["Science", "ASC"], False),
        ("Diane Gagnon", ["Science", "STE", "ASC"], False),
        ("Luc Bergeron", ["STE", "ASC"], False),
        ("Élise Morin", ["Science"], False),
        ("Antoine Rousseau", ["Science", "STE", "ASC"], False),
        ("Camille Leclerc", ["Science", "STE"], False),
        ("Gabriel Fontaine", ["Science", "ASC"], False),
        ("Charlotte Mercier", ["Science", "STE"], False),
        ("Alexandre Dupont", ["STE", "ASC"], False),
        ("Léa Fournier", ["Science"], False),

        # Français (12 enseignants - doublé)
        ("Sophie Bernard", ["Français"], False),
        ("Pierre Lefevre", ["Français"], False),
        ("Hélène Tremblay", ["Français"], False),
        ("Marc Bouchard", ["Français"], False),
        ("Nathalie Roy", ["Français"], False),
        ("Pascal Leblanc", ["Français"], False),
        ("Olivier Moreau", ["Français"], False),
        ("Chloé Girard", ["Français"], False),
        ("Nicolas Petit", ["Français"], False),
        ("Émilie Durand", ["Français"], False),
        ("Benjamin Laurent", ["Français"], False),
        ("Laurence Simon", ["Français"], False),

        # Math SN (8 enseignants - doublé)
        ("Isabelle Morin", ["Math SN"], False),
        ("François Girard", ["Math SN"], False),
        ("Stéphane Côté", ["Math SN"], False),
        ("Valérie Gauthier", ["Math SN"], False),
        ("Mathieu Thomas", ["Math SN"], False),
        ("Audrey Robert", ["Math SN"], False),
        ("Samuel Richard", ["Math SN"], False),
        ("Mélanie Blanc", ["Math SN"], False),

        # Math CST (8 enseignants - doublé)
        ("André Lavoie", ["Math CST"], False),
        ("Julie Pelletier", ["Math CST"], False),
        ("Simon Ouellet", ["Math CST"], False),
        ("Caroline Gagné", ["Math CST"], False),
        ("Vincent Lefebvre", ["Math CST"], False),
        ("Gabrielle Roux", ["Math CST"], False),
        ("William Chevalier", ["Math CST"], False),
        ("Alice Garnier", ["Math CST"], False),

        # Anglais (8 enseignants - doublé)
        ("Catherine Leblanc", ["Anglais"], False),
        ("Michel Roy", ["Anglais"], False),
        ("Thomas Bélanger", ["Anglais"], False),
        ("Sarah Martin", ["Anglais"], False),
        ("Xavier Bertrand", ["Anglais"], False),
        ("Rosalie Faure", ["Anglais"], False),
        ("Félix Lambert", ["Anglais"], False),
        ("Juliette Renard", ["Anglais"], False),

        # Anglais avancé (4 enseignants - doublé)
        ("Elizabeth Johnson", ["Anglais avancé"], False),
        ("David Thompson", ["Anglais avancé"], False),
        ("Lucas Bonnet", ["Anglais avancé"], False),
        ("Florence Mercier", ["Anglais avancé"], False),

        # Histoire (8 enseignants - doublé)
        ("Julie Gagnon", ["Histoire", "CCQ"], False),
        ("Robert Tremblay", ["Histoire"], False),
        ("Philippe Dubois", ["Histoire", "CCQ"], False),
        ("Amélie Fortin", ["Histoire"], False),
        ("Raphaël Roussel", ["Histoire", "CCQ"], False),
        ("Anaïs Dumas", ["Histoire"], False),
        ("Hugo Perrin", ["Histoire", "CCQ"], False),
        ("Coralie Mathieu", ["Histoire"], False),

        # CCQ (4 enseignants supplémentaires)
        ("Nathan Aubert", ["CCQ"], False),
        ("Maude Leroy", ["CCQ"], False),
        ("Zachary Bourgeois", ["CCQ"], False),
        ("Ariane Benoit", ["CCQ"], False),

        # Espagnol (4 enseignants - doublé)
        ("Nathalie Bouchard", ["Espagnol"], False),
        ("Carlos Rodriguez", ["Espagnol"], False),
        ("Maxime Rousseau", ["Espagnol"], False),
        ("Clara Martinez", ["Espagnol"], False),

        # Éducation physique (6 enseignants - doublé)
        ("Daniel Fortin", ["Éducation physique"], True),
        ("Maxime Gauthier", ["Éducation physique"], True),
        ("Jessica Lavoie", ["Éducation physique"], True),
        ("Tristan Lefebvre", ["Éducation physique"], True),
        ("Mélodie Gagnon", ["Éducation physique"], True),
        ("Étienne Barbier", ["Éducation physique"], True),

        # Option (6 enseignants - doublé)
        ("Sylvie Pelletier", ["Option"], False),
        ("Martin Côté", ["Option"], False),
        ("Isabelle Gagné", ["Option"], False),
        ("Jade Brunet", ["Option"], False),
        ("Noémie Caron", ["Option"], False),
        ("Édouard Lemoine", ["Option"], False),

        # Arts (4 enseignants - nouveau)
        ("Louis Blanchard", ["Arts"], False),
        ("Emma Vincent", ["Arts"], False),
        ("Antoine Morel", ["Arts"], False),
        ("Camille Renaud", ["Arts"], False)
    ]

    for i, (nom, matieres, est_enseignant_gym) in enumerate(noms_enseignants):
        identifiant = f"T{i+1:03d}"

        # AUCUNE restriction (comme demandé)
        restrictions = ""

        # Classe préférée aléatoire (mais pas le gymnase)
        # Avec 44 classes maintenant
        if est_enseignant_gym:
            # Pas de classe préférée pour les enseignants de gym
            classe_preferee = ""
        else:
            # Choisir une classe entre 1 et 44 (on évitera les gymnases - approximativement classes 31-36)
            choix_classes = list(range(1, 31)) + list(range(37, 45))  # Classes 1-30 et 37-44
            classe_preferee = f"C{random.choice(choix_classes):03d}"

        enseignants.append(EnseignantData(
            nom=nom,
            identifiant=identifiant,
            matieres=matieres,
            restrictions=restrictions,
            classe_preferee=classe_preferee
        ))

    data_manager.sauvegarder_enseignants(enseignants, "enseignants.csv")
    print(f"[OK] {len(enseignants)} enseignants crees dans data/enseignants/enseignants.csv")

    # 4. Créer des classes d'exemple (44 classes pour 176 élèves - doublé)
    print("\nCréation des classes d'exemple...")
    classes = []

    # Définition des types de salles avec matières autorisées
    # Double le nombre de salles pour plus de flexibilité
    types_salles = [
        # 6 Laboratoires pour les sciences (doublé)
        ("Laboratoire 1", 32, ["Science", "STE", "ASC"]),
        ("Laboratoire 2", 32, ["Science", "STE", "ASC"]),
        ("Laboratoire 3", 32, ["Science", "STE", "ASC"]),
        ("Laboratoire 4", 32, ["Science", "STE", "ASC"]),
        ("Laboratoire 5", 32, ["Science", "STE", "ASC"]),
        ("Laboratoire 6", 32, ["Science", "STE", "ASC"]),

        # 20 Salles régulières pour Français, Math SN, Math CST, Anglais, Anglais avancé, Espagnol (doublé)
        ("Salle régulière 1", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 2", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 3", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 4", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 5", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 6", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 7", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 8", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 9", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 10", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 11", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 12", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 13", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 14", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 15", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 16", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 17", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 18", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 19", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),
        ("Salle régulière 20", 32, ["Espagnol", "Français", "Math SN", "Math CST", "Anglais", "Anglais avancé"]),

        # 4 Salles multimédia pour Histoire et CCQ (doublé)
        ("Salle multimédia 1", 32, ["Histoire", "CCQ"]),
        ("Salle multimédia 2", 32, ["Histoire", "CCQ"]),
        ("Salle multimédia 3", 32, ["Histoire", "CCQ"]),
        ("Salle multimédia 4", 32, ["Histoire", "CCQ"]),

        # 6 Gymnases pour Éducation physique (doublé)
        ("Gymnase 1", 32, ["Éducation physique"]),
        ("Gymnase 2", 32, ["Éducation physique"]),
        ("Gymnase 3", 32, ["Éducation physique"]),
        ("Gymnase 4", 32, ["Éducation physique"]),
        ("Gymnase 5", 32, ["Éducation physique"]),
        ("Gymnase 6", 32, ["Éducation physique"]),

        # 8 Salles d'arts pour Option et Arts (doublé + Arts)
        ("Salle d'arts 1", 32, ["Option", "Arts"]),
        ("Salle d'arts 2", 32, ["Option", "Arts"]),
        ("Salle d'arts 3", 32, ["Option", "Arts"]),
        ("Salle d'arts 4", 32, ["Option", "Arts"]),
        ("Salle d'arts 5", 32, ["Option", "Arts"]),
        ("Salle d'arts 6", 32, ["Option", "Arts"]),
        ("Salle d'arts 7", 32, ["Option", "Arts"]),
        ("Salle d'arts 8", 32, ["Option", "Arts"])
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
