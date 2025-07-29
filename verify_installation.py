#!/usr/bin/env python3
"""
Script de vérification d'installation - Component Data Processor

Ce script vérifie que l'installation est complète et fonctionnelle.
Il teste tous les composants principaux et génère un rapport de validation.
"""

import sys
import os
import subprocess
from pathlib import Path
import json
import importlib.util


class InstallationVerifier:
    """Vérificateur d'installation du Component Data Processor."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, description, condition, error_msg="", warning_msg=""):
        """Effectue une vérification et enregistre le résultat."""
        self.total_checks += 1
        
        if condition:
            print(f"[OK] {description}")
            self.success_count += 1
            return True
        else:
            if error_msg:
                print(f"[ERROR] {description}: {error_msg}")
                self.errors.append(f"{description}: {error_msg}")
            elif warning_msg:
                print(f"[WARN] {description}: {warning_msg}")
                self.warnings.append(f"{description}: {warning_msg}")
            else:
                print(f"[ERROR] {description}")
                self.errors.append(description)
            return False
    
    def verify_python_version(self):
        """Vérifie la version de Python."""
        print("\n[PYTHON] Vérification de Python...")

        version = sys.version_info
        self.check(
            f"Python {version.major}.{version.minor}.{version.micro}",
            version >= (3, 7),
            "Python 3.7+ requis"
        )
    
    def verify_file_structure(self):
        """Vérifie la structure des fichiers."""
        print("\n[FILES] Vérification de la structure des fichiers...")

        required_files = [
            "main.py",
            "runner.py",
            "requirements.txt",
            "README.md",
            "QUICKSTART.md"
        ]

        required_dirs = [
            "src",
            "src/component_processor",
            "src/data_handlers",
            "src/utils",
            "tests",
            "docs",
            "config"
        ]
        
        for file_path in required_files:
            self.check(
                f"Fichier {file_path}",
                Path(file_path).exists(),
                "Fichier manquant"
            )
        
        for dir_path in required_dirs:
            self.check(
                f"Répertoire {dir_path}/",
                Path(dir_path).exists(),
                "Répertoire manquant"
            )
    
    def verify_dependencies(self):
        """Vérifie les dépendances Python."""
        print("\n[DEPS] Vérification des dépendances...")

        required_packages = [
            "pandas",
            "numpy",
            "openpyxl"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.check(f"Package {package}", True)
            except ImportError:
                self.check(f"Package {package}", False, "Non installé")
    
    def verify_modules(self):
        """Vérifie que les modules s'importent correctement."""
        print("\n🔧 Vérification des modules...")
        
        modules_to_test = [
            ("src.component_processor.processor", "ComponentDataProcessor"),
            ("src.data_handlers.data_cleaner", "DataCleaner"),
            ("src.data_handlers.lookup_processor", "LookupProcessor"),
            ("src.data_handlers.excel_handler", "ExcelHandler"),
            ("src.utils.logger", "Logger"),
            ("src.utils.file_manager", "FileManager"),
            ("src.utils.validators", "DataValidator")
        ]
        
        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                getattr(module, class_name)
                self.check(f"Module {module_name}", True)
            except Exception as e:
                self.check(f"Module {module_name}", False, str(e))
    
    def verify_configuration(self):
        """Vérifie les fichiers de configuration."""
        print("\n⚙️ Vérification de la configuration...")
        
        config_files = [
            "config/default.json"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        json.load(f)
                    self.check(f"Configuration {config_file}", True)
                except json.JSONDecodeError as e:
                    self.check(f"Configuration {config_file}", False, f"JSON invalide: {e}")
            else:
                self.check(f"Configuration {config_file}", False, "Fichier manquant")
    
    def verify_scripts(self):
        """Vérifie les scripts de démarrage."""
        print("\n🚀 Vérification des scripts...")
        
        # Vérifier que les scripts principaux s'exécutent
        scripts_to_test = [
            ("python runner.py info", "Runner principal"),
            ("python main.py --help", "Application principale")
        ]
        
        for cmd, description in scripts_to_test:
            try:
                result = subprocess.run(
                    cmd.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                self.check(description, result.returncode == 0)
            except Exception as e:
                self.check(description, False, str(e))
    
    def verify_sample_creation(self):
        """Vérifie la création des fichiers d'exemple."""
        print("\n📋 Vérification de la création d'exemples...")
        
        try:
            # Nettoyer les anciens exemples
            for file in ["Master_BOM.xlsx", "Sample_Input_Data.xlsx"]:
                if Path(file).exists():
                    Path(file).unlink()
            
            # Créer les exemples
            result = subprocess.run(
                ["python", "runner.py", "samples"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Vérifier que les fichiers ont été créés
                expected_files = ["Master_BOM.xlsx", "Sample_Input_Data.xlsx"]
                for file in expected_files:
                    self.check(
                        f"Fichier d'exemple {file}",
                        Path(file).exists(),
                        "Non créé"
                    )
            else:
                self.check("Création d'exemples", False, result.stderr)
                
        except Exception as e:
            self.check("Création d'exemples", False, str(e))
    
    def verify_basic_processing(self):
        """Vérifie le traitement de base."""
        print("\n🔄 Vérification du traitement de base...")
        
        if not Path("Sample_Input_Data.xlsx").exists():
            self.check("Traitement de base", False, "Fichier d'exemple manquant")
            return
        
        try:
            # Test de validation
            result = subprocess.run(
                ["python", "main.py", "Sample_Input_Data.xlsx", "--validate-only"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.check("Validation fichier", result.returncode == 0)
            
            # Test de traitement (si validation OK)
            if result.returncode == 0:
                result = subprocess.run(
                    ["python", "runner.py", "process", "Sample_Input_Data.xlsx"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                self.check("Traitement fichier", result.returncode == 0)
                
                # Vérifier les sorties
                output_dir = Path("output")
                if output_dir.exists():
                    output_files = list(output_dir.glob("Update_*.xlsx"))
                    self.check("Fichier de sortie généré", len(output_files) > 0)
                
        except Exception as e:
            self.check("Traitement de base", False, str(e))
    
    def generate_report(self):
        """Génère un rapport de vérification."""
        print("\n" + "="*60)
        print("RAPPORT DE VERIFICATION")
        print("="*60)

        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0

        print(f"[SUCCESS] Verifications reussies: {self.success_count}/{self.total_checks} ({success_rate:.1f}%)")

        if self.errors:
            print(f"\n[ERRORS] Erreurs ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n[WARNINGS] Avertissements ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "="*60)

        if not self.errors:
            print("INSTALLATION VALIDEE - Pret a l'emploi !")
            print("\nProchaines etapes:")
            print("  1. Consultez QUICKSTART.md pour commencer")
            print("  2. Lisez README.md pour le guide complet")
            print("  3. Utilisez 'python runner.py --help' pour l'aide")
            return True
        else:
            print("INSTALLATION INCOMPLETE")
            print("\nActions recommandees:")
            print("  1. Installez les dependances: pip install -r requirements.txt")
            print("  2. Verifiez la structure des fichiers")
            print("  3. Relancez cette verification")
            return False
    
    def run_full_verification(self):
        """Exécute la vérification complète."""
        print("Component Data Processor - Verification d'installation")
        print("="*60)
        
        self.verify_python_version()
        self.verify_file_structure()
        self.verify_dependencies()
        self.verify_modules()
        self.verify_configuration()
        self.verify_scripts()
        self.verify_sample_creation()
        self.verify_basic_processing()
        
        return self.generate_report()


def main():
    """Fonction principale."""
    verifier = InstallationVerifier()
    success = verifier.run_full_verification()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
