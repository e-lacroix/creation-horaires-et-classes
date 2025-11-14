# Guide des Données

Ce dossier contient toutes les données nécessaires pour générer des horaires scolaires.

## Structure des Dossiers

```
data/
├── programmes/       # Programmes d'études (fichiers JSON)
├── eleves/          # Données des élèves (fichiers CSV)
├── enseignants/     # Données des enseignants (fichiers CSV)
└── classes/         # Données des salles de classe (fichiers CSV)
```

## 1. Programmes (JSON)

Les programmes définissent les cours requis pour chaque type d'étudiant.

**Emplacement**: `data/programmes/`

**Format**: JSON

**Structure**:
```json
{
  "nom": "Nom du Programme",
  "cours": {
    "Science": 4,
    "STE": 2,
    "Math SN": 6,
    ...
  },
  "description": "Description du programme"
}
```

**Matières disponibles**:
- Science, STE, ASC
- Français, Math SN
- Anglais, Histoire
- CCQ, Espagnol
- Éducation physique, Option

## 2. Élèves (CSV)

**Emplacement**: `data/eleves/eleves.csv`

**Colonnes**:
- **Nom**: Nom complet de l'élève
- **Identifiant**: Code unique (ex: E0001)
- **Programme**: Nom du programme (doit correspondre à un fichier dans `programmes/`)
- **Restrictions**: Plages horaires non disponibles, séparées par des virgules
  - Format: `jour_periode` (ex: `lundi_matin,jeudi_apres_midi`)
  - Jours: lundi, mardi, mercredi, jeudi, vendredi
  - Périodes: matin, apres_midi
  - Laisser vide si aucune restriction
- **Talents**: Niveau de compétence par matière (0.0 à 1.0)
  - Format: `Matiere:valeur|Matiere:valeur|...`
  - Exemple: `Science:0.95|Math SN:0.82|Français:0.76`

**Exemple**:
```csv
Nom,Identifiant,Programme,Restrictions,Talents
Alice Tremblay,E0001,Secondaire 4 Régulier,lundi_matin,Science:0.85|Math SN:0.92|Français:0.78
Bob Gagnon,E0002,Secondaire 4 Sciences,,Science:0.95|Math SN:0.88|Français:0.82
```

## 3. Enseignants (CSV)

**Emplacement**: `data/enseignants/enseignants.csv`

**Colonnes**:
- **Nom**: Nom complet de l'enseignant
- **Identifiant**: Code unique (ex: T001)
- **Matières**: Matières que l'enseignant peut enseigner, séparées par des pipes (`|`)
  - Exemple: `Science|STE|ASC`
- **Restrictions**: Plages horaires non disponibles (même format que pour les élèves)
- **Classe Préférée**: Identifiant de la salle préférée (ex: C001)

**Exemple**:
```csv
Nom,Identifiant,Matières,Restrictions,Classe Préférée
Marie Dubois,T001,Science|STE|ASC,,C001
Jean Martin,T002,Français,mercredi_matin,C003
```

## 4. Classes (CSV)

**Emplacement**: `data/classes/classes.csv`

**Colonnes**:
- **Identifiant**: Code unique (ex: C001)
- **Nom**: Nom descriptif de la salle
- **Capacité**: Nombre maximum d'élèves
- **Matières Autorisées**: Matières qui peuvent être enseignées dans cette salle, séparées par des pipes (`|`)

**Exemple**:
```csv
Identifiant,Nom,Capacité,Matières Autorisées
C001,Laboratoire Science 1,28,Science|STE|ASC
C002,Salle régulière 1,30,Français|Math SN|Anglais|Histoire|CCQ|Espagnol
C003,Gymnase,35,Éducation physique
```

## Utilisation

### Créer des données d'exemple

Pour générer des fichiers CSV d'exemple avec des données aléatoires:

```bash
python creer_donnees_exemple.py
```

Cela créera:
- 56 élèves répartis dans deux programmes
- 13 enseignants avec différentes spécialisations
- 8 salles de classe de différents types
- 2 programmes par défaut

### Modifier les données

1. **Ajouter un nouveau programme**:
   - Créez un nouveau fichier JSON dans `data/programmes/`
   - Suivez la structure décrite ci-dessus
   - Le nom du fichier doit correspondre au champ "nom" dans le JSON

2. **Modifier les élèves**:
   - Éditez `data/eleves/eleves.csv` avec Excel, LibreOffice ou un éditeur de texte
   - Assurez-vous que les programmes référencés existent dans `data/programmes/`

3. **Modifier les enseignants**:
   - Éditez `data/enseignants/enseignants.csv`
   - Les matières doivent correspondre exactement aux noms utilisés dans les programmes

4. **Modifier les classes**:
   - Éditez `data/classes/classes.csv`
   - Ajustez les capacités selon vos besoins

### Importer les données dans l'application

L'application chargera automatiquement les données depuis ces fichiers CSV au démarrage.

## Notes Importantes

- **Encodage**: Tous les fichiers CSV doivent être encodés en UTF-8
- **Séparateurs**: Utilisez des virgules (`,`) pour séparer les colonnes
- **Pipes**: Utilisez des pipes (`|`) pour séparer les éléments de liste (matières, talents)
- **Identifiants**: Les identifiants doivent être uniques pour chaque catégorie
- **Références**: Assurez-vous que tous les programmes et classes référencés existent

## Dépannage

- **Erreur de chargement**: Vérifiez que l'encodage est UTF-8
- **Programme introuvable**: Assurez-vous qu'un fichier JSON existe pour chaque programme référencé
- **Matières non reconnues**: Vérifiez l'orthographe exacte des matières
