# Guide de Gestion des Données

## Vue d'ensemble

Le système de création d'horaires utilise maintenant des fichiers CSV et JSON pour stocker et gérer les données des élèves, enseignants, classes et programmes. Cela permet une personnalisation complète sans avoir à modifier le code source.

## Structure des Dossiers

```
data/
├── programmes/           # Fichiers JSON définissant les programmes d'études
│   ├── Secondaire 4 Régulier.json
│   └── Secondaire 4 Sciences.json
├── eleves/              # Fichiers CSV des élèves
│   └── eleves.csv
├── enseignants/         # Fichiers CSV des enseignants
│   └── enseignants.csv
└── classes/             # Fichiers CSV des salles de classe
    └── classes.csv
```

## Démarrage Rapide

### 1. Créer les Données d'Exemple

Si c'est votre première utilisation, générez les données d'exemple:

```bash
python creer_donnees_exemple.py
```

Cela créera:
- 56 élèves répartis dans deux programmes
- 13 enseignants avec différentes spécialisations
- 8 salles de classe
- 2 programmes d'études

### 2. Lancer l'Application

```bash
python main.py
```

### 3. Gérer les Données

Dans l'application, allez dans l'onglet **"🗂️ Gestion des Données"** pour:
- Ouvrir et modifier les fichiers CSV avec Excel/LibreOffice
- Accéder aux dossiers de données
- Régénérer les données d'exemple si nécessaire

## Formats des Fichiers

### Élèves (eleves.csv)

Colonnes:
- **Nom**: Nom complet de l'élève
- **Identifiant**: Code unique (ex: E0001)
- **Programme**: Nom du programme (doit exister dans data/programmes/)
- **Restrictions**: Plages horaires non disponibles (ex: "lundi_matin,jeudi_apres_midi")
- **Talents**: Compétences par matière (ex: "Science:0.85|Math SN:0.92|Français:0.78")

Exemple:
```csv
Nom,Identifiant,Programme,Restrictions,Talents
Alice Tremblay,E0001,Secondaire 4 Régulier,lundi_matin,Science:0.85|Math SN:0.92|Français:0.78
Bob Gagnon,E0002,Secondaire 4 Sciences,,Science:0.95|Math SN:0.88|Français:0.82
```

### Enseignants (enseignants.csv)

Colonnes:
- **Nom**: Nom complet
- **Identifiant**: Code unique (ex: T001)
- **Matières**: Matières enseignées, séparées par `|` (ex: "Science|STE|ASC")
- **Restrictions**: Plages horaires non disponibles
- **Classe Préférée**: Identifiant de la salle préférée (ex: C001)

Exemple:
```csv
Nom,Identifiant,Matières,Restrictions,Classe Préférée
Marie Dubois,T001,Science|STE|ASC,,C001
Jean Martin,T002,Français,mercredi_matin,C003
```

### Classes (classes.csv)

Colonnes:
- **Identifiant**: Code unique (ex: C001)
- **Nom**: Nom descriptif de la salle
- **Capacité**: Nombre maximum d'élèves
- **Matières Autorisées**: Matières autorisées, séparées par `|`

Exemple:
```csv
Identifiant,Nom,Capacité,Matières Autorisées
C001,Laboratoire Science 1,28,Science|STE|ASC
C002,Salle régulière 1,30,Français|Math SN|Anglais|Histoire|CCQ|Espagnol
```

### Programmes (fichiers JSON)

Structure:
```json
{
  "nom": "Secondaire 4 Régulier",
  "cours": {
    "Science": 4,
    "STE": 2,
    "ASC": 2,
    "Français": 6,
    "Math SN": 6,
    "Anglais": 4,
    "Histoire": 4,
    "CCQ": 2,
    "Espagnol": 2,
    "Éducation physique": 2,
    "Option": 2
  },
  "description": "Programme régulier pour les élèves de Secondaire 4 au Québec"
}
```

Le nom du fichier doit correspondre au champ "nom" (ex: "Secondaire 4 Régulier.json").

## Matières Disponibles

Les matières suivantes sont reconnues par le système:
- Science, STE, ASC
- Français, Math SN
- Anglais, Histoire
- CCQ, Espagnol
- Éducation physique, Option

## Workflow de Modification

### Modifier les Données

1. **Via l'Application** (recommandé):
   - Ouvrir l'application (`python main.py`)
   - Aller dans l'onglet "🗂️ Gestion des Données"
   - Cliquer sur "Ouvrir le fichier CSV" pour modifier avec Excel

2. **Manuellement**:
   - Ouvrir les fichiers CSV dans `data/` avec Excel, LibreOffice ou un éditeur de texte
   - Respecter le format exact des colonnes
   - Sauvegarder en UTF-8

### Créer un Nouveau Programme

1. Créer un nouveau fichier JSON dans `data/programmes/`
2. Suivre la structure décrite ci-dessus
3. Le nom du fichier doit correspondre au champ "nom"
4. Référencer ce programme dans le CSV des élèves

### Ajouter des Élèves/Enseignants/Classes

Ajouter simplement une nouvelle ligne dans le fichier CSV correspondant en respectant le format.

### Appliquer les Changements

Après modification des fichiers:
1. Sauvegarder les fichiers
2. Dans l'application, cliquer sur "Générer l'horaire"
3. Les nouvelles données seront automatiquement chargées

## Module Python: data_manager.py

Le système utilise le module `data_manager.py` qui fournit:

### Classes de Données

- `Programme`: Définit un programme d'études
- `EleveData`: Données d'un élève
- `EnseignantData`: Données d'un enseignant
- `ClasseData`: Données d'une salle de classe

### DataManager

Gestionnaire principal pour charger/sauvegarder les données:

```python
from data_manager import DataManager

# Créer une instance
dm = DataManager()

# Lister les programmes
programmes = dm.lister_programmes()

# Charger un programme
programme = dm.charger_programme("Secondaire 4 Régulier")

# Charger les données CSV
eleves = dm.charger_eleves()
enseignants = dm.charger_enseignants()
classes = dm.charger_classes()

# Sauvegarder
dm.sauvegarder_eleves(eleves)
dm.sauvegarder_programme(programme)
```

## Intégration avec data_generator.py

Le module `data_generator.py` a été modifié pour:
1. Charger automatiquement les données depuis les CSV s'ils existent
2. Sinon, générer des données par défaut en mémoire

La fonction `generate_sample_data()` accepte maintenant un paramètre `use_csv_data`:

```python
# Charger depuis CSV (défaut)
data = generate_sample_data(num_students=56, use_csv_data=True)

# Générer des données temporaires
data = generate_sample_data(num_students=56, use_csv_data=False)
```

## Dépannage

### Erreur: Fichier introuvable

Exécutez `python creer_donnees_exemple.py` pour créer les fichiers initiaux.

### Erreur: Programme introuvable

Vérifiez que:
1. Le fichier JSON existe dans `data/programmes/`
2. Le nom dans le CSV correspond exactement au nom du fichier (sans .json)
3. Le format JSON est valide

### Erreur: Matière non reconnue

Vérifiez l'orthographe exacte des matières dans les fichiers CSV. Utilisez les noms listés dans la section "Matières Disponibles".

### Encodage incorrect

Assurez-vous que tous les fichiers CSV sont enregistrés en UTF-8 (option dans Excel: "CSV UTF-8").

## Exemples d'Utilisation

### Créer un Programme Personnalisé

Créez `data/programmes/Mon Programme.json`:

```json
{
  "nom": "Mon Programme",
  "cours": {
    "Science": 8,
    "Français": 8,
    "Math SN": 8,
    "Anglais": 6,
    "Histoire": 6
  },
  "description": "Programme personnalisé avec plus de sciences"
}
```

### Ajouter des Restrictions pour un Élève

Dans `eleves.csv`, colonne "Restrictions":
```csv
...,lundi_matin,mercredi_apres_midi,...
```

Signifie que l'élève n'est pas disponible le lundi matin et le mercredi après-midi.

### Créer un Enseignant Polyvalent

Dans `enseignants.csv`:
```csv
Prof Polyvalent,T099,Science|Français|Math SN|Anglais,,C001
```

Cet enseignant peut enseigner 4 matières différentes.

## Notes Importantes

- Les identifiants doivent être uniques dans chaque catégorie
- Les références entre fichiers doivent être exactes (programmes, classes)
- Les modifications prennent effet au prochain "Générer l'horaire"
- Les données d'exemple peuvent être régénérées à tout moment depuis l'application
- Faites des sauvegardes avant de régénérer les données d'exemple

## Support

Pour plus d'informations détaillées sur le format des fichiers, consultez `data/README.md`.
