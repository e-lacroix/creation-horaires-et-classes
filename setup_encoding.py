"""
Module pour configurer l'encodage UTF-8 sur toutes les plateformes.
Importez ce module au début de vos scripts pour garantir le support des caractères spéciaux.
"""
import sys
import io
import os


def setup_utf8_encoding():
    """
    Configure l'encodage UTF-8 pour stdout, stderr et l'environnement.
    Cette fonction doit être appelée au début du script.
    """
    # Configurer les variables d'environnement
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Sur Windows, changer la page de code de la console
    if sys.platform == 'win32':
        try:
            # Changer la page de code en UTF-8 (65001)
            os.system('chcp 65001 > nul 2>&1')
        except:
            pass

    # Reconfigurer stdout et stderr pour UTF-8
    try:
        # Pour Python 3.7+, utiliser reconfigure si disponible
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            # Pour Python 3.6 et antérieur
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception as e:
        print(f"Avertissement: Impossible de configurer UTF-8: {e}")

    # Configurer l'encodage par défaut pour open()
    import locale
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass


# Exécuter automatiquement lors de l'import
setup_utf8_encoding()
