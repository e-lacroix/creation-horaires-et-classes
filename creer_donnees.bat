@echo off
REM Script pour créer les données d'exemple avec support UTF-8 sur Windows
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python creer_donnees_exemple.py
pause
