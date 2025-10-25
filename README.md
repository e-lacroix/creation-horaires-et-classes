# Création d'Horaires et Classes - Secondaire Québec

Logiciel de création d'horaires optimisés pour les écoles secondaires du Québec (Secondaire 4), basé sur des algorithmes d'optimisation et des études scientifiques.

## Caractéristiques

- **Nombre d'étudiants configurable** dans l'interface (1-200)
- **Tous les étudiants participent à tous les cours**
- **Maximum 1 cours par matière par jour** pour chaque étudiant
- Respect des contraintes québécoises (max 28 étudiants/classe)
- Minimisation du nombre d'enseignants et de salles nécessaires
- Support pour tous les cours du secondaire québécois
- **Interface Material Design moderne** avec ttkbootstrap
- Export vers Excel avec statistiques détaillées

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

```bash
python main.py
```

### Configuration

L'application permet de configurer:
- **Nombre d'étudiants** : 1 à 200 (par défaut 56) - tous en Secondaire 4
- **36 cours** répartis comme suit:
  - 4 classes de Science
  - 2 classes de STE (Sciences et technologies de l'environnement)
  - 2 classes d'ASC (Applications technologiques et scientifiques)
  - 6 classes de Français
  - 6 classes de Mathématiques SN (Séquence Sciences Naturelles)
  - 4 classes d'Anglais
  - 4 classes d'Histoire
  - 2 classes de CCQ (Culture et citoyenneté québécoise)
  - 2 classes d'Espagnol
  - 2 classes d'Éducation physique
  - 2 classes d'Option

### Générer un horaire

1. Ouvrez l'application
2. Consultez la configuration dans l'onglet "Configuration"
3. Cliquez sur "Générer l'horaire optimisé"
4. Consultez les résultats dans l'onglet "Horaires"
5. Consultez les statistiques dans l'onglet "Statistiques"
6. Exportez vers Excel si désiré

## Architecture

Le système utilise:
- **Google OR-Tools** pour la résolution du problème de satisfaction de contraintes
- **ttkbootstrap** pour l'interface Material Design moderne
- **Pandas** pour l'export de données

### Contraintes respectées

1. Chaque cours est assigné à exactement un créneau horaire
2. Chaque cours a exactement un enseignant
3. Chaque cours a exactement une salle
4. Un enseignant ne peut enseigner qu'un cours à la fois
5. Une salle ne peut être utilisée qu'une fois par créneau
6. Un étudiant ne peut suivre qu'un cours à la fois
7. Maximum 28 étudiants par classe
8. **TOUS les étudiants participent à TOUS les cours** (36 cours par étudiant)
9. **Un étudiant ne peut pas avoir 2 cours de la même matière dans une journée**

### Objectifs d'optimisation

- Minimiser le nombre de salles utilisées
- Équilibrer la charge d'enseignement
- Répartir équitablement les étudiants dans les cours

## Structure du projet

```
creation-horaires-et-classes/
├── main.py              # Point d'entrée
├── gui.py               # Interface graphique
├── scheduler.py         # Algorithme d'optimisation
├── models.py            # Modèles de données
├── data_generator.py    # Génération de données
├── requirements.txt     # Dépendances
└── README.md           # Documentation
```

## Licence

GNU General Public License v3.0