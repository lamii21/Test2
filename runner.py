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
        print(f"✅ Python: {python_version}")
        
        # Installer les dépendances
        print("📦 Installation des dépendances...")
        if self.run_command(f"{self.python_cmd} -m pip install -r requirements.txt"):
            print("✅ Dépendances installées")
        
        # Créer les répertoires nécessaires
        dirs = ['output', 'config', 'examples', 'tests/coverage_html']
        for dir_path in dirs:
            Path(dir_path).mkdir(exist_ok=True)
            print(f"Repertoire cree: {dir_path}")
        
        print("Configuration terminee!")
    
    def create_samples(self):
        """Crée les fichiers d'exemple."""
        print("Creation des fichiers d'exemple...")
        return self.run_command(f"{self.python_cmd} main.py --create-samples")
    
    def process(self, input_file, config=None, verbose=False, validate_only=False):
        """Traite un fichier."""
        cmd = f"{self.python_cmd} main.py {input_file}"
        
        if config:
            cmd += f" --config {config}"
        if verbose:
            cmd += " --verbose"
        if validate_only:
            cmd += " --validate-only"
        
        print(f"Traitement: {input_file}")
        return self.run_command(cmd)
    
    def batch_process(self, pattern, config=None):
        """Traite plusieurs fichiers en lot."""
        cmd = f"{self.python_cmd} main.py --batch \"{pattern}\""
        
        if config:
            cmd += f" --config {config}"
        
        print(f"📦 Traitement en lot: {pattern}")
        return self.run_command(cmd)
    
    def validate(self, input_file):
        """Valide un fichier sans le traiter."""
        print(f"✅ Validation: {input_file}")
        return self.run_command(f"{self.python_cmd} main.py {input_file} --validate-only")
    
    def test(self, coverage=False, module=None):
        """Exécute les tests."""
        if module:
            print(f"🧪 Tests du module: {module}")
            return self.run_command(f"{self.python_cmd} tests/run_tests.py --module {module}")
        elif coverage:
            print("🧪 Tests avec couverture...")
            return self.run_command(f"{self.python_cmd} tests/run_tests.py --coverage")
        else:
            print("🧪 Exécution des tests...")
            return self.run_command(f"{self.python_cmd} -m unittest discover tests -v")
    
    def clean(self):
        """Nettoie les fichiers temporaires."""
        print("🧹 Nettoyage...")
        
        # Supprimer les caches Python
        import shutil
        for cache_dir in Path('.').rglob('__pycache__'):
            shutil.rmtree(cache_dir, ignore_errors=True)
            print(f"🗑️  Supprimé: {cache_dir}")
        
        # Supprimer les fichiers .pyc
        for pyc_file in Path('.').rglob('*.pyc'):
            pyc_file.unlink(missing_ok=True)
            print(f"🗑️  Supprimé: {pyc_file}")
        
        print("✅ Nettoyage terminé")
    
    def status(self):
        """Affiche le statut du projet."""
        print("Statut du Component Data Processor")
        print("=" * 50)
        
        # Vérifier la structure
        required_dirs = ['src', 'tests', 'docs', 'config']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"✅ {dir_name}/")
            else:
                print(f"❌ {dir_name}/ (manquant)")
        
        # Vérifier les fichiers principaux
        required_files = ['main.py', 'requirements.txt', 'README.md']
        for file_name in required_files:
            if Path(file_name).exists():
                print(f"✅ {file_name}")
            else:
                print(f"❌ {file_name} (manquant)")
        
        # Vérifier les dépendances
        try:
            import pandas, openpyxl, numpy
            print("✅ Dépendances principales installées")
        except ImportError as e:
            print(f"❌ Dépendances manquantes: {e}")
        
        # Statistiques des fichiers
        output_dir = Path('output')
        if output_dir.exists():
            output_files = list(output_dir.glob('*'))
            print(f"Fichiers de sortie: {len(output_files)}")
        
        print("=" * 50)
    
    def docs(self, serve=False):
        """Gère la documentation."""
        if serve:
            print("📚 Serveur de documentation (non implémenté)")
            print("💡 Consultez les fichiers dans docs/")
        else:
            print("📚 Documentation disponible:")
            docs_dir = Path('docs')
            if docs_dir.exists():
                for doc_file in docs_dir.glob('*.md'):
                    print(f"  📄 {doc_file}")
            print("  📖 README.md")
            print("  📄 OVERVIEW.md")
    
    def config_create(self, name, template='default'):
        """Crée un nouveau fichier de configuration."""
        config_dir = Path('config')
        template_file = config_dir / f'{template}.json'
        new_file = config_dir / f'{name}.json'
        
        if template_file.exists():
            import shutil
            shutil.copy(template_file, new_file)
            print(f"✅ Configuration créée: {new_file}")
            print(f"💡 Basée sur le template: {template}")
        else:
            print(f"❌ Template non trouvé: {template}")
    
    def config_list(self):
        """Liste les configurations disponibles."""
        config_dir = Path('config')
        if config_dir.exists():
            configs = list(config_dir.glob('*.json'))
            if configs:
                print("Configurations disponibles:")
                for config in configs:
                    print(f"  📄 {config.stem}")
            else:
                print("❌ Aucune configuration trouvée")
        else:
            print("❌ Répertoire config/ non trouvé")
    
    def info(self):
        """Affiche les informations du projet."""
        print("ℹ️  Component Data Processor")
        print("=" * 40)
        print("📝 Description: Automatise le traitement des données de composants")
        print("🏗️  Architecture: Modulaire et extensible")
        print("🐍 Python: 3.7+")
        print("📦 Dépendances: pandas, openpyxl, numpy")
        print("🧪 Tests: unittest + coverage")
        print("📚 Documentation: Complète")
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
    
    args = parser.parse_args()
    runner = ComponentProcessorRunner()
    
    # Exécuter la commande
    if args.command == 'setup':
        runner.setup()
    
    elif args.command == 'samples':
        runner.create_samples()
    
    elif args.command == 'process':
        if not args.args:
            print("❌ Fichier d'entrée requis")
            sys.exit(1)
        runner.process(args.args[0], args.config, args.verbose)
    
    elif args.command == 'batch':
        if not args.args:
            print("❌ Pattern requis")
            sys.exit(1)
        runner.batch_process(args.args[0], args.config)
    
    elif args.command == 'validate':
        if not args.args:
            print("❌ Fichier d'entrée requis")
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
                print("❌ Nom de configuration requis")
                sys.exit(1)
            runner.config_create(args.args[1], args.template)
        elif args.args and args.args[0] == 'list':
            runner.config_list()
        else:
            print("❌ Sous-commande config requise: create, list")
    
    elif args.command == 'info':
        runner.info()
    
    else:
        print(f"❌ Commande inconnue: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
