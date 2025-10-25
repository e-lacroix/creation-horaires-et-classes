# Guide de démarrage rapide

## Installation rapide

1. **Installer Python 3.8 ou supérieur**
   - Télécharger depuis https://www.python.org/downloads/

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python main.py
   ```

## Utilisation de l'application

### Étape 1: Configuration
- L'onglet "Configuration" affiche automatiquement les cours requis
- 36 classes pour 56 étudiants (Secondaire 4)
- Répartition selon les exigences du secondaire québécois

### Étape 2: Génération de l'horaire
- Cliquez sur **"Générer l'horaire optimisé"**
- L'optimisation peut prendre jusqu'à 60 secondes
- Une barre de progression indique le statut

### Étape 3: Consultation des résultats
- **Onglet "Horaires"**: Voir l'horaire complet jour par jour
  - Colonnes: Jour, Période, Cours, Enseignant, Salle, Nombre d'étudiants
- **Onglet "Statistiques"**: Voir les statistiques détaillées
  - Charge d'enseignement par professeur
  - Utilisation des salles
  - Distribution des étudiants

### Étape 4: Export
- Cliquez sur **"Exporter vers Excel"**
- Le fichier `horaire_optimise.xlsx` sera créé
- Contient 2 feuilles: Horaire général et Vue par enseignant

## Comprendre les résultats

### Structure de l'horaire
- **9 jours** de cours
- **4 périodes** par jour
- **36 créneaux** horaires au total

### Contraintes respectées
✓ Maximum 28 étudiants par classe
✓ Aucun conflit d'enseignant
✓ Aucun conflit de salle
✓ Aucun conflit d'étudiant
✓ Tous les cours requis sont planifiés

### Optimisations
- Minimisation du nombre de salles utilisées
- Équilibrage de la charge des enseignants
- Répartition équitable des étudiants

## Résolution de problèmes

### "Impossible de trouver une solution optimale"
- Les contraintes peuvent être trop restrictives
- Solutions possibles:
  - Augmenter le nombre d'enseignants disponibles
  - Augmenter le nombre de salles
  - Ajuster la répartition des cours

### "L'optimisation prend trop de temps"
- Le timeout est fixé à 60 secondes
- Modifier dans `scheduler.py` ligne 150:
  ```python
  solver.parameters.max_time_in_seconds = 120.0  # 2 minutes
  ```

### Erreur d'import de modules
- Vérifier que toutes les dépendances sont installées:
  ```bash
  pip install -r requirements.txt
  ```

## Personnalisation

### Modifier le nombre d'étudiants
Éditer `data_generator.py` ligne 20:
```python
for i in range(56):  # Changer 56 pour le nombre désiré
```

### Modifier la répartition des cours
Éditer `data_generator.py` lignes 24-36

### Ajouter des enseignants
Éditer `data_generator.py` section "Créer les enseignants"

## Support

Pour signaler un problème ou suggérer une amélioration:
- Créer une issue sur GitHub
- Consulter le fichier README.md pour plus de détails
