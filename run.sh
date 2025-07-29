#!/bin/bash
# Script de démarrage rapide pour Linux/macOS - Component Data Processor
# Usage: ./run.sh <commande> [arguments]

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${RESET}"
    exit 1
fi

# Si aucun argument, afficher l'aide
if [ $# -eq 0 ]; then
    echo -e "${BLUE}🚀 Component Data Processor - Runner${RESET}"
    echo
    echo -e "${YELLOW}Commandes disponibles:${RESET}"
    echo -e "  ${GREEN}setup${RESET}           - Configure l'environnement"
    echo -e "  ${GREEN}samples${RESET}         - Crée les fichiers d'exemple"
    echo -e "  ${GREEN}process <file>${RESET}  - Traite un fichier"
    echo -e "  ${GREEN}batch <pattern>${RESET} - Traite plusieurs fichiers"
    echo -e "  ${GREEN}validate <file>${RESET} - Valide un fichier"
    echo -e "  ${GREEN}test${RESET}            - Exécute les tests"
    echo -e "  ${GREEN}clean${RESET}           - Nettoie les fichiers temporaires"
    echo -e "  ${GREEN}status${RESET}          - Affiche le statut du projet"
    echo -e "  ${GREEN}info${RESET}            - Informations du projet"
    echo
    echo -e "${YELLOW}Exemples:${RESET}"
    echo "  ./run.sh setup"
    echo "  ./run.sh samples"
    echo "  ./run.sh process input.xlsx"
    echo "  ./run.sh test"
    exit 0
fi

# Exécuter la commande via le runner Python
python3 runner.py "$@"

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commande terminée avec succès${RESET}"
else
    echo -e "${RED}❌ Commande échouée${RESET}"
    exit 1
fi
