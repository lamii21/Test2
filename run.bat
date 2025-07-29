@echo off
REM Script de démarrage rapide pour Windows - Component Data Processor
REM Usage: run.bat <commande> [arguments]

setlocal enabledelayedexpansion

REM Couleurs pour l'affichage
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python n'est pas installé ou pas dans le PATH%RESET%
    exit /b 1
)

REM Si aucun argument, afficher l'aide
if "%1"=="" (
    echo %BLUE%🚀 Component Data Processor - Runner%RESET%
    echo.
    echo %YELLOW%Commandes disponibles:%RESET%
    echo   %GREEN%setup%RESET%           - Configure l'environnement
    echo   %GREEN%samples%RESET%         - Crée les fichiers d'exemple
    echo   %GREEN%process ^<file^>%RESET%  - Traite un fichier
    echo   %GREEN%batch ^<pattern^>%RESET% - Traite plusieurs fichiers
    echo   %GREEN%validate ^<file^>%RESET% - Valide un fichier
    echo   %GREEN%test%RESET%            - Exécute les tests
    echo   %GREEN%clean%RESET%           - Nettoie les fichiers temporaires
    echo   %GREEN%status%RESET%          - Affiche le statut du projet
    echo   %GREEN%info%RESET%            - Informations du projet
    echo.
    echo %YELLOW%Exemples:%RESET%
    echo   run setup
    echo   run samples
    echo   run process input.xlsx
    echo   run test
    exit /b 0
)

REM Exécuter la commande via le runner Python
python runner.py %*

REM Vérifier le code de retour
if errorlevel 1 (
    echo %RED%❌ Commande échouée%RESET%
    exit /b 1
) else (
    echo %GREEN%✅ Commande terminée avec succès%RESET%
)
