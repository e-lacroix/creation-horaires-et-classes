# Guide de Lancement Rapide

## Windows

### Première utilisation

1. **Créer les données d'exemple:**
   ```bash
   creer_donnees.bat
   ```
   OU
   ```bash
   python creer_donnees_exemple.py
   ```

2. **Lancer l'application:**
   ```bash
   run_app.bat
   ```
   OU
   ```bash
   python main.py
   ```

### Utilisation quotidienne

Double-cliquez simplement sur `run_app.bat` pour lancer l'application.

## macOS / Linux

### Première utilisation

1. **Créer les données d'exemple:**
   ```bash
   python creer_donnees_exemple.py
   ```

2. **Lancer l'application:**
   ```bash
   python main.py
   ```

## Fonctionnalités Principales

### Dans l'Application

1. **Configuration** (panneau gauche):
   - Ajustez le nombre d'étudiants (1-200)
   - Ajustez le nombre d'enseignants (5-50)
   - Ajustez le nombre de salles (5-20)

2. **Générer l'Horaire**:
   - Cliquez sur "Générer l'horaire"
   - Attendez l'optimisation (jusqu'à 2 minutes)
   - Consultez les résultats dans les onglets

3. **Onglets Disponibles**:
   - 📅 **Sessions de cours**: Voir toutes les sessions créées
   - 👤 **Horaires individuels**: Horaire de chaque étudiant
   - 👨‍🏫 **Horaires enseignants**: Horaire de chaque enseignant
   - 📊 **Statistiques**: Analyse détaillée de l'optimisation
   - 🗂️ **Gestion des Données**: Modifier les CSV et programmes

4. **Export Excel**:
   - Cliquez sur "Exporter vers Excel"
   - Fichier créé: `horaire_YYYY-MM-DD_HH-MM-SS.xlsx`
   - 3 feuilles: Sessions, Horaires Individuels, Assignations Enseignants

### Gestion des Données

Dans l'onglet "🗂️ Gestion des Données":

1. **Ouvrir les fichiers CSV**:
   - Cliquez sur "Ouvrir le fichier CSV" pour éditer avec Excel
   - Modifiez les données (élèves, enseignants, classes)
   - Sauvegardez

2. **Modifier les programmes**:
   - Cliquez sur "Ouvrir le dossier des programmes"
   - Créez/modifiez les fichiers JSON
   - Voir `data/README.md` pour le format

3. **Régénérer les données d'exemple**:
   - Cliquez sur "Regénérer les données d'exemple"
   - Confirmer (écrase les fichiers existants)
   - 56 élèves, 13 enseignants, 8 classes recréés

4. **Appliquer les changements**:
   - Après modification des CSV
   - Retournez à la configuration
   - Cliquez sur "Générer l'horaire"

## Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `run_app.bat` | Lancer l'application (Windows) |
| `creer_donnees.bat` | Créer les données d'exemple (Windows) |
| `main.py` | Point d'entrée de l'application |
| `creer_donnees_exemple.py` | Générateur de données |
| `data/eleves/eleves.csv` | Données des élèves |
| `data/enseignants/enseignants.csv` | Données des enseignants |
| `data/classes/classes.csv` | Données des salles |
| `data/programmes/*.json` | Définitions des programmes |

## Documentation Complète

- [README.md](README.md) - Documentation principale
- [GUIDE_GESTION_DONNEES.md](GUIDE_GESTION_DONNEES.md) - Guide détaillé des données
- [ENCODAGE_UTF8.md](ENCODAGE_UTF8.md) - Support des caractères spéciaux
- [data/README.md](data/README.md) - Format des fichiers de données
- [CLAUDE.md](CLAUDE.md) - Documentation technique pour développeurs

## Problèmes Courants

### Caractères mal affichés (é, à, ç, etc.)

**Sur Windows:**
- Utilisez `run_app.bat` au lieu de `python main.py`
- Voir [ENCODAGE_UTF8.md](ENCODAGE_UTF8.md) pour plus de détails

### Fichiers de données introuvables

**Solution:**
```bash
python creer_donnees_exemple.py
```
OU
```bash
creer_donnees.bat
```

### Optimisation échoue

**Causes possibles:**
- Trop d'étudiants pour le nombre d'enseignants/salles
- Configuration impossible à satisfaire

**Solutions:**
- Réduire le nombre d'étudiants
- Augmenter le nombre d'enseignants
- Augmenter le nombre de salles

### Excel non installé

**Pour ouvrir les fichiers CSV:**
- LibreOffice Calc (gratuit)
- Google Sheets (en ligne)
- Bloc-notes / éditeur de texte

## Support

Pour toute question ou problème:
1. Consultez la documentation complète
2. Vérifiez les fichiers README dans le projet
3. Vérifiez que Python 3.8+ est installé
4. Vérifiez que les dépendances sont installées (`pip install -r requirements.txt`)

## Raccourcis Clavier

- `F5` : Actualiser l'interface (après modification des CSV)
- `Ctrl+E` : Exporter vers Excel
- `Ctrl+Q` : Quitter l'application
