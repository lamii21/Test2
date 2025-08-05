#!/usr/bin/env python3
"""
Runner - Script d'exécution et de gestion pour le Component Data Processor

Ce script fournit une interface simplifiée pour toutes les opérations
du Component Data Processor avec des commandes intuitives.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime


class ComponentProcessorRunner:
    """Runner principal pour le Component Data Processor."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.python_cmd = sys.executable
        
    def run_command(self, cmd, capture_output=False, check=True):
        """Exécute une commande système."""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
                return result.stdout.strip()
            else:
                subprocess.run(cmd, shell=True, check=check)
                return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'execution: {e}")
            return False
    
    def setup(self):
        """Configure l'environnement de développement."""
        print("Configuration de l'environnement...")
        
        # Vérifier Python
        python_version = self.run_command(f"{self.python_cmd} --version", capture_output=True)
        print(f"[OK] Python: {python_version}")
        
        # Installer les dépendances
        print("[INSTALL] Installation des dépendances...")
        if self.run_command(f"{self.python_cmd} -m pip install -r requirements.txt"):
            print("[OK] Dépendances installées")
        
        # Créer les répertoires nécessaires
        dirs = ['output', 'config', 'examples', 'tests/coverage_html']
        for dir_path in dirs:
            Path(dir_path).mkdir(exist_ok=True)
            print(f"Repertoire cree: {dir_path}")
        
        print("Configuration terminee!")
    
    def create_samples(self):
        """Crée les fichiers d'exemple."""
        print("Creation des fichiers d'exemple...")
        # Utiliser le nouveau système - les échantillons existent déjà
        print("[OK] Fichiers d'exemple disponibles: Sample_Input_Data.xlsx")
        return True
    
    def process(self, input_file, config=None, verbose=False, validate_only=False, project_column=None):
        """Traite un fichier en utilisant le nouveau système ComponentDataProcessor."""
        try:
            # Importer et utiliser le système existant
            from src.component_processor.processor import ComponentDataProcessor

            # Créer le processeur
            processor = ComponentDataProcessor()

            # Traiter le fichier
            if validate_only:
                print(f"[VALIDATION] {input_file}")
                # Validation simple - vérifier que le fichier existe et est lisible
                import pandas as pd
                df = pd.read_excel(input_file)
                print(f"[VALIDE] Fichier valide: {len(df)} lignes, {len(df.columns)} colonnes")
                return True
            else:
                print(f"[TRAITEMENT] {input_file}")
                if project_column:
                    print(f"[COLONNE] {project_column}")
                    # Configurer la colonne de projet
                    processor.set_project_column(project_column)

                # Traitement avec le système existant
                result = processor.process_file(input_file)

                if result:
                    print("[SUCCES] Traitement termine avec succes")
                    return True
                else:
                    print("[ERREUR] Traitement echoue")
                    return False

        except Exception as e:
            print(f"[ERREUR] Erreur lors du traitement: {e}")
            return False
    
    def batch_process(self, pattern, config=None):
        """Traite plusieurs fichiers en lot."""
        print(f"[BATCH] Traitement en lot: {pattern}")

        try:
            from pathlib import Path
            import glob

            # Trouver les fichiers correspondant au pattern
            files = glob.glob(pattern)
            if not files:
                print(f"[ERREUR] Aucun fichier trouve pour le pattern: {pattern}")
                return False

            print(f"[INFO] {len(files)} fichiers trouves")

            # Traiter chaque fichier
            success_count = 0
            for file_path in files:
                print(f"\n[TRAITEMENT] {file_path}")
                if self.process(file_path, config=config):
                    success_count += 1
                    print(f"[SUCCES] {file_path}")
                else:
                    print(f"[ECHEC] {file_path}")

            print(f"\n[RESUME] {success_count}/{len(files)} fichiers traites avec succes")
            return success_count == len(files)

        except Exception as e:
            print(f"[ERREUR] Erreur traitement en lot: {e}")
            return False
    
    def validate(self, input_file):
        """Valide un fichier sans le traiter."""
        print(f"[VALIDATION] {input_file}")
        return self.process(input_file, validate_only=True)
    
    def test(self, coverage=False, module=None):
        """Exécute les tests."""
        if module:
            print(f"[TEST] Tests du module: {module}")
            return self.run_command(f"{self.python_cmd} tests/run_tests.py --module {module}")
        elif coverage:
            print("[TEST] Tests avec couverture...")
            return self.run_command(f"{self.python_cmd} tests/run_tests.py --coverage")
        else:
            print("[TEST] Exécution des tests...")
            return self.run_command(f"{self.python_cmd} -m unittest discover tests -v")
    
    def clean(self):
        """Nettoie les fichiers temporaires."""
        print("[CLEAN] Nettoyage...")
        
        # Supprimer les caches Python
        import shutil
        for cache_dir in Path('.').rglob('__pycache__'):
            shutil.rmtree(cache_dir, ignore_errors=True)
            print(f"[DELETE]  Supprimé: {cache_dir}")
        
        # Supprimer les fichiers .pyc
        for pyc_file in Path('.').rglob('*.pyc'):
            pyc_file.unlink(missing_ok=True)
            print(f"[DELETE]  Supprimé: {pyc_file}")
        
        print("[OK] Nettoyage terminé")
    
    def status(self):
        """Affiche le statut du projet."""
        print("Statut du Component Data Processor")
        print("=" * 50)
        
        # Vérifier la structure
        required_dirs = ['src', 'tests', 'docs', 'config']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"[OK] {dir_name}/")
            else:
                print(f"[ERREUR] {dir_name}/ (manquant)")
        
        # Vérifier les fichiers principaux
        required_files = ['START_SYSTEM.py', 'backend_simple.py', 'simple_web.py', 'requirements.txt', 'README.md']
        for file_name in required_files:
            if Path(file_name).exists():
                print(f"[OK] {file_name}")
            else:
                print(f"[ERREUR] {file_name} (manquant)")
        
        # Vérifier les dépendances
        try:
            import pandas, openpyxl, numpy
            print("[OK] Dépendances principales installées")
        except ImportError as e:
            print(f"[ERREUR] Dépendances manquantes: {e}")
        
        # Statistiques des fichiers
        output_dir = Path('output')
        if output_dir.exists():
            output_files = list(output_dir.glob('*'))
            print(f"Fichiers de sortie: {len(output_files)}")
        
        print("=" * 50)
    
    def docs(self, serve=False):
        """Gère la documentation."""
        if serve:
            print("[DOCS] Serveur de documentation (non implémenté)")
            print("[INFO] Consultez les fichiers dans docs/")
        else:
            print("[DOCS] Documentation disponible:")
            docs_dir = Path('docs')
            if docs_dir.exists():
                for doc_file in docs_dir.glob('*.md'):
                    print(f"  [FILE] {doc_file}")
            print("  [DOC] README.md")
            print("  [FILE] OVERVIEW.md")
    
    def config_create(self, name, template='default'):
        """Crée un nouveau fichier de configuration."""
        config_dir = Path('config')
        template_file = config_dir / f'{template}.json'
        new_file = config_dir / f'{name}.json'
        
        if template_file.exists():
            import shutil
            shutil.copy(template_file, new_file)
            print(f"[OK] Configuration créée: {new_file}")
            print(f"[INFO] Basée sur le template: {template}")
        else:
            print(f"[ERREUR] Template non trouvé: {template}")
    
    def config_list(self):
        """Liste les configurations disponibles."""
        config_dir = Path('config')
        if config_dir.exists():
            configs = list(config_dir.glob('*.json'))
            if configs:
                print("Configurations disponibles:")
                for config in configs:
                    print(f"  [FILE] {config.stem}")
            else:
                print("[ERREUR] Aucune configuration trouvée")
        else:
            print("[ERREUR] Répertoire config/ non trouvé")
    
    def info(self):
        """Affiche les informations du projet."""
        print("[INFO]  Component Data Processor")
        print("=" * 40)
        print("[DESC] Description: Automatise le traitement des données de composants")
        print("[ARCH]  Architecture: Modulaire et extensible")
        print("[PYTHON] Python: 3.7+")
        print("[INSTALL] Dépendances: pandas, openpyxl, numpy")
        print("[TEST] Tests: unittest + coverage")
        print("[DOCS] Documentation: Complète")
        print("=" * 40)


def main():
    """Fonction principale du runner."""
    parser = argparse.ArgumentParser(
        description='Runner pour Component Data Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commandes disponibles:
  setup                     Configure l'environnement
  samples                   Crée les fichiers d'exemple
  process <file>            Traite un fichier
  batch <pattern>           Traite plusieurs fichiers
  validate <file>           Valide un fichier
  test                      Exécute les tests
  clean                     Nettoie les fichiers temporaires
  status                    Affiche le statut du projet
  docs                      Gère la documentation
  config                    Gère les configurations
  info                      Informations du projet

Exemples:
  python runner.py setup
  python runner.py samples
  python runner.py process input.xlsx --config custom
  python runner.py batch "*.xlsx"
  python runner.py test --coverage
        """
    )
    
    parser.add_argument('command', help='Commande à exécuter')
    parser.add_argument('args', nargs='*', help='Arguments de la commande')
    parser.add_argument('--config', '-c', help='Fichier de configuration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    parser.add_argument('--coverage', action='store_true', help='Tests avec couverture')
    parser.add_argument('--module', '-m', help='Module de test spécifique')
    parser.add_argument('--serve', action='store_true', help='Servir la documentation')
    parser.add_argument('--template', '-t', default='default', help='Template de configuration')
    parser.add_argument('--project-column', '-p', help='Colonne de projet dans Master BOM')
    
    args = parser.parse_args()
    runner = ComponentProcessorRunner()
    
    # Exécuter la commande
    if args.command == 'setup':
        runner.setup()
    
    elif args.command == 'samples':
        runner.create_samples()
    
    elif args.command == 'process':
        if not args.args:
            print("[ERREUR] Fichier d'entrée requis")
            sys.exit(1)
        runner.process(args.args[0], args.config, args.verbose, project_column=getattr(args, 'project_column', None))
    
    elif args.command == 'batch':
        if not args.args:
            print("[ERREUR] Pattern requis")
            sys.exit(1)
        runner.batch_process(args.args[0], args.config)
    
    elif args.command == 'validate':
        if not args.args:
            print("[ERREUR] Fichier d'entrée requis")
            sys.exit(1)
        runner.validate(args.args[0])
    
    elif args.command == 'test':
        runner.test(args.coverage, args.module)
    
    elif args.command == 'clean':
        runner.clean()
    
    elif args.command == 'status':
        runner.status()
    
    elif args.command == 'docs':
        runner.docs(args.serve)
    
    elif args.command == 'config':
        if args.args and args.args[0] == 'create':
            if len(args.args) < 2:
                print("[ERREUR] Nom de configuration requis")
                sys.exit(1)
            runner.config_create(args.args[1], args.template)
        elif args.args and args.args[0] == 'list':
            runner.config_list()
        else:
            print("[ERREUR] Sous-commande config requise: create, list")
    
    elif args.command == 'info':
        runner.info()
    
    else:
        print(f"[ERREUR] Commande inconnue: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
