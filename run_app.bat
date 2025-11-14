@echo off
REM Script pour lancer l'application avec support UTF-8 sur Windows
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python main.py
pause
