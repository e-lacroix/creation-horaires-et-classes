# Support des Caractères Spéciaux (UTF-8)

## Problème

Sur Windows, Python utilise par défaut l'encodage `cp1252` au lieu d'UTF-8, ce qui cause des erreurs avec les caractères accentués et les symboles spéciaux (é, à, ç, etc.).

## Solution Implémentée

Le projet inclut maintenant un support complet UTF-8 pour tous les scripts Python.

### Module `setup_encoding.py`

Un module a été créé pour configurer automatiquement l'encodage UTF-8. Il est importé au début de chaque script principal.

**Fonctionnalités:**
- Configure `PYTHONIOENCODING=utf-8`
- Change la page de code Windows en UTF-8 (65001)
- Reconfigure `stdout` et `stderr` pour UTF-8
- Compatible avec toutes les versions de Python 3.6+

### Scripts Modifiés

Les scripts suivants importent automatiquement `setup_encoding`:
- `main.py` - Point d'entrée de l'application
- `creer_donnees_exemple.py` - Générateur de données
- `data_generator.py` - Module de génération

## Utilisation

### Méthode 1: Lancer avec Python (recommandé)

Sur Windows, utilisez les scripts batch fournis:

```bash
# Lancer l'application
run_app.bat

# Créer les données d'exemple
creer_donnees.bat
```

Ces scripts configurent automatiquement:
- La page de code UTF-8 (`chcp 65001`)
- La variable d'environnement `PYTHONIOENCODING=utf-8`

### Méthode 2: Ligne de commande Python

Vous pouvez aussi lancer directement avec Python (l'encodage est géré automatiquement):

```bash
python main.py
python creer_donnees_exemple.py
```

### Méthode 3: Configuration globale Windows (optionnel)

Pour configurer UTF-8 globalement sur votre système Windows:

1. **Via les Paramètres Régionaux:**
   - Ouvrir "Paramètres" > "Heure et langue" > "Langue et région"
   - Cliquer sur "Paramètres administratifs de langue"
   - Onglet "Options administratives" > "Modifier les paramètres régionaux système"
   - Cocher "Bêta: Utiliser Unicode UTF-8 pour la prise en charge linguistique internationale"
   - Redémarrer l'ordinateur

2. **Via une Variable d'Environnement:**
   - Ouvrir "Paramètres système avancés"
   - Variables d'environnement
   - Ajouter une nouvelle variable système:
     - Nom: `PYTHONIOENCODING`
     - Valeur: `utf-8`

## Vérification

Pour vérifier que l'encodage UTF-8 fonctionne:

```bash
python -c "import sys; print(sys.stdout.encoding)"
```

Devrait afficher: `utf-8`

## Dépannage

### Erreur: UnicodeEncodeError

Si vous voyez encore cette erreur:
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solutions:**
1. Utilisez les scripts batch (`.bat`) pour lancer l'application
2. Vérifiez que `setup_encoding.py` est bien dans le même dossier
3. Essayez de configurer UTF-8 globalement (voir Méthode 3)

### Problème avec la console Python IDLE

IDLE peut avoir des limitations avec UTF-8. Utilisez plutôt:
- Windows Terminal
- PowerShell
- Command Prompt (cmd)
- VS Code Terminal

### Caractères Affichés Incorrectement

Si les caractères s'affichent mal dans la console:
```bash
chcp 65001
```
Puis relancez votre script.

## Fichiers Créés

### `setup_encoding.py`
Module de configuration UTF-8 automatique. Importé par tous les scripts principaux.

### `run_app.bat`
Script batch pour lancer l'application avec UTF-8 sur Windows.

### `creer_donnees.bat`
Script batch pour créer les données d'exemple avec UTF-8 sur Windows.

## Notes pour les Développeurs

Si vous créez de nouveaux scripts Python dans ce projet:

```python
# Toujours importer en premier
import setup_encoding

# Puis vos autres imports
from models import Student
...
```

Cela garantit que tous les caractères spéciaux seront correctement gérés.

## Compatibilité

- **Windows**: ✅ Support complet UTF-8
- **macOS**: ✅ UTF-8 par défaut (pas de configuration nécessaire)
- **Linux**: ✅ UTF-8 par défaut (pas de configuration nécessaire)
- **Python**: 3.6+ (testé avec 3.11)

## Références

- [PEP 540 - UTF-8 Mode](https://www.python.org/dev/peps/pep-0540/)
- [PEP 528 - Windows Console Encoding](https://www.python.org/dev/peps/pep-0528/)
- [Documentation Python - sys.stdout](https://docs.python.org/3/library/sys.html#sys.stdout)
