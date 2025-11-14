"""
Module de gestion des données pour les programmes, élèves, enseignants et classes.
"""
import json
import csv
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from models import CourseType


@dataclass
class Programme:
    """Représente un programme d'études avec ses cours requis."""
    nom: str
    cours: Dict[CourseType, int]  # CourseType -> nombre de cours
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le programme en dictionnaire pour la sérialisation JSON."""
        return {
            'nom': self.nom,
            'cours': {ct.value: count for ct, count in self.cours.items()},
            'description': self.description
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Programme':
        """Crée un programme à partir d'un dictionnaire."""
        cours = {CourseType(ct): count for ct, count in data['cours'].items()}
        return Programme(
            nom=data['nom'],
            cours=cours,
            description=data.get('description', '')
        )


@dataclass
class EleveData:
    """Données d'un élève."""
    nom: str
    identifiant: str
    programme: str
    restrictions: str  # Séparé par des virgules, ex: "lundi_matin,jeudi_apres_midi"
    talents: Dict[str, float]  # Matière -> niveau (0.0 à 1.0)

    def to_csv_row(self) -> List[str]:
        """Convertit en ligne CSV."""
        talents_str = "|".join([f"{mat}:{val}" for mat, val in self.talents.items()])
        return [self.nom, self.identifiant, self.programme, self.restrictions, talents_str]

    @staticmethod
    def from_csv_row(row: List[str]) -> 'EleveData':
        """Crée un élève à partir d'une ligne CSV."""
        talents = {}
        if row[4]:  # Si talents non vide
            for talent_str in row[4].split("|"):
                if ":" in talent_str:
                    mat, val = talent_str.split(":")
                    talents[mat] = float(val)
        return EleveData(
            nom=row[0],
            identifiant=row[1],
            programme=row[2],
            restrictions=row[3],
            talents=talents
        )


@dataclass
class EnseignantData:
    """Données d'un enseignant."""
    nom: str
    identifiant: str
    matieres: List[str]  # Liste des matières qu'il peut enseigner
    restrictions: str  # Séparé par des virgules
    classe_preferee: str  # Identifiant de la classe préférée

    def to_csv_row(self) -> List[str]:
        """Convertit en ligne CSV."""
        matieres_str = "|".join(self.matieres)
        return [self.nom, self.identifiant, matieres_str, self.restrictions, self.classe_preferee]

    @staticmethod
    def from_csv_row(row: List[str]) -> 'EnseignantData':
        """Crée un enseignant à partir d'une ligne CSV."""
        matieres = row[2].split("|") if row[2] else []
        return EnseignantData(
            nom=row[0],
            identifiant=row[1],
            matieres=matieres,
            restrictions=row[3],
            classe_preferee=row[4]
        )


@dataclass
class ClasseData:
    """Données d'une salle de classe."""
    identifiant: str
    nom: str
    capacite: int
    matieres_autorisees: List[str]  # Liste des matières qui peuvent y être enseignées

    def to_csv_row(self) -> List[str]:
        """Convertit en ligne CSV."""
        matieres_str = "|".join(self.matieres_autorisees)
        return [self.identifiant, self.nom, str(self.capacite), matieres_str]

    @staticmethod
    def from_csv_row(row: List[str]) -> 'ClasseData':
        """Crée une classe à partir d'une ligne CSV."""
        matieres = row[3].split("|") if row[3] else []
        return ClasseData(
            identifiant=row[0],
            nom=row[1],
            capacite=int(row[2]),
            matieres_autorisees=matieres
        )


class DataManager:
    """Gestionnaire de données pour charger et sauvegarder les données."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.programmes_dir = os.path.join(data_dir, "programmes")
        self.eleves_dir = os.path.join(data_dir, "eleves")
        self.enseignants_dir = os.path.join(data_dir, "enseignants")
        self.classes_dir = os.path.join(data_dir, "classes")

        # Créer les dossiers s'ils n'existent pas
        for dir_path in [self.programmes_dir, self.eleves_dir, self.enseignants_dir, self.classes_dir]:
            os.makedirs(dir_path, exist_ok=True)

    # ===== Gestion des Programmes =====

    def sauvegarder_programme(self, programme: Programme) -> None:
        """Sauvegarde un programme dans un fichier JSON."""
        file_path = os.path.join(self.programmes_dir, f"{programme.nom}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(programme.to_dict(), f, ensure_ascii=False, indent=2)

    def charger_programme(self, nom: str) -> Optional[Programme]:
        """Charge un programme à partir de son nom."""
        file_path = os.path.join(self.programmes_dir, f"{nom}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Programme.from_dict(data)

    def lister_programmes(self) -> List[str]:
        """Liste tous les programmes disponibles."""
        programmes = []
        for filename in os.listdir(self.programmes_dir):
            if filename.endswith('.json'):
                programmes.append(filename[:-5])  # Enlever .json
        return sorted(programmes)

    def supprimer_programme(self, nom: str) -> bool:
        """Supprime un programme."""
        file_path = os.path.join(self.programmes_dir, f"{nom}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    # ===== Gestion des Élèves =====

    def sauvegarder_eleves(self, eleves: List[EleveData], nom_fichier: str = "eleves.csv") -> None:
        """Sauvegarde les élèves dans un fichier CSV."""
        file_path = os.path.join(self.eleves_dir, nom_fichier)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Nom', 'Identifiant', 'Programme', 'Restrictions', 'Talents'])
            for eleve in eleves:
                writer.writerow(eleve.to_csv_row())

    def charger_eleves(self, nom_fichier: str = "eleves.csv") -> List[EleveData]:
        """Charge les élèves à partir d'un fichier CSV."""
        file_path = os.path.join(self.eleves_dir, nom_fichier)
        if not os.path.exists(file_path):
            return []
        eleves = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 5:
                    eleves.append(EleveData.from_csv_row(row))
        return eleves

    # ===== Gestion des Enseignants =====

    def sauvegarder_enseignants(self, enseignants: List[EnseignantData], nom_fichier: str = "enseignants.csv") -> None:
        """Sauvegarde les enseignants dans un fichier CSV."""
        file_path = os.path.join(self.enseignants_dir, nom_fichier)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Nom', 'Identifiant', 'Matières', 'Restrictions', 'Classe Préférée'])
            for enseignant in enseignants:
                writer.writerow(enseignant.to_csv_row())

    def charger_enseignants(self, nom_fichier: str = "enseignants.csv") -> List[EnseignantData]:
        """Charge les enseignants à partir d'un fichier CSV."""
        file_path = os.path.join(self.enseignants_dir, nom_fichier)
        if not os.path.exists(file_path):
            return []
        enseignants = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 5:
                    enseignants.append(EnseignantData.from_csv_row(row))
        return enseignants

    # ===== Gestion des Classes =====

    def sauvegarder_classes(self, classes: List[ClasseData], nom_fichier: str = "classes.csv") -> None:
        """Sauvegarde les classes dans un fichier CSV."""
        file_path = os.path.join(self.classes_dir, nom_fichier)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Identifiant', 'Nom', 'Capacité', 'Matières Autorisées'])
            for classe in classes:
                writer.writerow(classe.to_csv_row())

    def charger_classes(self, nom_fichier: str = "classes.csv") -> List[ClasseData]:
        """Charge les classes à partir d'un fichier CSV."""
        file_path = os.path.join(self.classes_dir, nom_fichier)
        if not os.path.exists(file_path):
            return []
        classes = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 4:
                    classes.append(ClasseData.from_csv_row(row))
        return classes


# Fonction pour créer des programmes par défaut
def creer_programmes_par_defaut(data_manager: DataManager) -> None:
    """Crée les programmes par défaut (Secondaire 4 régulier)."""

    # Programme Secondaire 4 Régulier (programme actuel)
    programme_sec4 = Programme(
        nom="Secondaire 4 Régulier",
        cours={
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
            CourseType.OPTION: 2
        },
        description="Programme régulier pour les élèves de Secondaire 4 au Québec"
    )
    data_manager.sauvegarder_programme(programme_sec4)

    # Programme Secondaire 4 Sciences
    programme_sciences = Programme(
        nom="Secondaire 4 Sciences",
        cours={
            CourseType.SCIENCE: 6,
            CourseType.STE: 4,
            CourseType.ASC: 4,
            CourseType.FRANCAIS: 4,
            CourseType.MATH_SN: 6,
            CourseType.ANGLAIS: 4,
            CourseType.HISTOIRE: 4,
            CourseType.CCQ: 2,
            CourseType.EDUC: 2
        },
        description="Programme enrichi en sciences pour les élèves de Secondaire 4"
    )
    data_manager.sauvegarder_programme(programme_sciences)
