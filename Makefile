# Makefile pour Component Data Processor
# Fournit des raccourcis pour les tâches courantes

.PHONY: help setup samples process test clean status docs install dev-install

# Variables
PYTHON := python
PIP := pip
VENV := venv

# Couleurs pour l'affichage
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
RESET := \033[0m

# Aide par défaut
help:
	@echo "$(BLUE)🚀 Component Data Processor - Makefile$(RESET)"
	@echo
	@echo "$(YELLOW)Commandes disponibles:$(RESET)"
	@echo "  $(GREEN)make setup$(RESET)          - Configure l'environnement complet"
	@echo "  $(GREEN)make install$(RESET)        - Installe les dépendances"
	@echo "  $(GREEN)make dev-install$(RESET)    - Installe les dépendances de développement"
	@echo "  $(GREEN)make samples$(RESET)        - Crée les fichiers d'exemple"
	@echo "  $(GREEN)make test$(RESET)           - Exécute tous les tests"
	@echo "  $(GREEN)make test-coverage$(RESET)  - Tests avec couverture de code"
	@echo "  $(GREEN)make clean$(RESET)          - Nettoie les fichiers temporaires"
	@echo "  $(GREEN)make status$(RESET)         - Affiche le statut du projet"
	@echo "  $(GREEN)make docs$(RESET)           - Affiche la documentation"
	@echo "  $(GREEN)make lint$(RESET)           - Vérifie le style de code"
	@echo "  $(GREEN)make format$(RESET)         - Formate le code"
	@echo
	@echo "$(YELLOW)Exemples d'utilisation:$(RESET)"
	@echo "  make setup && make samples"
	@echo "  make test"
	@echo "  $(PYTHON) main.py input.xlsx"

# Configuration complète de l'environnement
setup: install
	@echo "$(BLUE)🔧 Configuration de l'environnement...$(RESET)"
	@mkdir -p output config examples tests/coverage_html
	@echo "$(GREEN)✅ Environnement configuré$(RESET)"

# Installation des dépendances
install:
	@echo "$(BLUE)📦 Installation des dépendances...$(RESET)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dépendances installées$(RESET)"

# Installation des dépendances de développement
dev-install: install
	@echo "$(BLUE)🛠️ Installation des dépendances de développement...$(RESET)"
	@$(PIP) install coverage pytest black flake8 mypy
	@echo "$(GREEN)✅ Dépendances de développement installées$(RESET)"

# Création des fichiers d'exemple
samples:
	@echo "$(BLUE)📋 Création des fichiers d'exemple...$(RESET)"
	@$(PYTHON) main.py --create-samples
	@echo "$(GREEN)✅ Fichiers d'exemple créés$(RESET)"

# Exécution des tests
test:
	@echo "$(BLUE)🧪 Exécution des tests...$(RESET)"
	@$(PYTHON) -m unittest discover tests -v

# Tests avec couverture
test-coverage:
	@echo "$(BLUE)🧪 Tests avec couverture de code...$(RESET)"
	@$(PYTHON) tests/run_tests.py --coverage || echo "$(YELLOW)⚠️ Coverage non disponible, installation avec: pip install coverage$(RESET)"

# Nettoyage
clean:
	@echo "$(BLUE)🧹 Nettoyage...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@rm -rf .coverage 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(RESET)"

# Statut du projet
status:
	@echo "$(BLUE)📊 Statut du Component Data Processor$(RESET)"
	@$(PYTHON) runner.py status

# Documentation
docs:
	@echo "$(BLUE)📚 Documentation disponible:$(RESET)"
	@echo "  📖 README.md - Guide utilisateur principal"
	@echo "  📄 OVERVIEW.md - Vue d'ensemble du projet"
	@echo "  🏗️ docs/ARCHITECTURE.md - Architecture technique"
	@echo "  🔧 docs/API_REFERENCE.md - Référence API"
	@echo "  🚀 docs/DEPLOYMENT.md - Guide de déploiement"

# Vérification du style de code
lint:
	@echo "$(BLUE)🔍 Vérification du style de code...$(RESET)"
	@flake8 src/ tests/ main.py runner.py || echo "$(YELLOW)⚠️ flake8 non disponible$(RESET)"

# Formatage du code
format:
	@echo "$(BLUE)✨ Formatage du code...$(RESET)"
	@black src/ tests/ main.py runner.py || echo "$(YELLOW)⚠️ black non disponible$(RESET)"

# Traitement d'un fichier (exemple)
process-sample: samples
	@echo "$(BLUE)🚀 Traitement du fichier d'exemple...$(RESET)"
	@$(PYTHON) main.py Sample_Input_Data.xlsx --config config/default.json

# Validation d'un fichier (exemple)
validate-sample: samples
	@echo "$(BLUE)✅ Validation du fichier d'exemple...$(RESET)"
	@$(PYTHON) main.py Sample_Input_Data.xlsx --validate-only

# Traitement en lot (exemple)
batch-sample: samples
	@echo "$(BLUE)📦 Traitement en lot des exemples...$(RESET)"
	@$(PYTHON) main.py --batch "Sample_*.xlsx"

# Installation complète pour développement
dev-setup: dev-install setup samples
	@echo "$(GREEN)🎉 Environnement de développement prêt!$(RESET)"

# Vérification complète (tests + lint)
check: test lint
	@echo "$(GREEN)✅ Vérifications terminées$(RESET)"

# Construction d'un package (si nécessaire)
build: clean
	@echo "$(BLUE)📦 Construction du package...$(RESET)"
	@$(PYTHON) setup.py sdist bdist_wheel || echo "$(YELLOW)⚠️ setup.py non disponible$(RESET)"

# Informations sur le projet
info:
	@$(PYTHON) runner.py info
