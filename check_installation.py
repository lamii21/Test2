#!/usr/bin/env python3
"""
Script de verification simple - Component Data Processor
Verifie que l'installation est complete et fonctionnelle.
"""

import sys
import os
import subprocess
from pathlib import Path
import json


def check_python():
    """Verifie la version de Python."""
    print("\n[PYTHON] Verification de Python...")
    version = sys.version_info
    if version >= (3, 7):
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERROR] Python {version.major}.{version.minor}.{version.micro} - Version 3.7+ requise")
        return False


def check_files():
    """Verifie la structure des fichiers."""
    print("\n[FILES] Verification de la structure...")
    
    required_files = [
        "main.py", "runner.py", "requirements.txt", "README.md"
    ]
    
    required_dirs = [
        "src", "src/component_processor", "src/data_handlers", 
        "src/utils", "tests", "docs", "config"
    ]
    
    success = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} manquant")
            success = False
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"[OK] {dir_path}/")
        else:
            print(f"[ERROR] {dir_path}/ manquant")
            success = False
    
    return success


def check_dependencies():
    """Verifie les dependances Python."""
    print("\n[DEPS] Verification des dependances...")
    
    required_packages = ["pandas", "numpy", "openpyxl"]
    success = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERROR] {package} non installe")
            success = False
    
    return success


def check_modules():
    """Verifie que les modules s'importent."""
    print("\n[MODULES] Verification des modules...")
    
    modules = [
        "src.component_processor.processor",
        "src.data_handlers.data_cleaner",
        "src.utils.logger"
    ]
    
    success = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[ERROR] {module}: {e}")
            success = False
    
    return success


def check_config():
    """Verifie la configuration."""
    print("\n[CONFIG] Verification de la configuration...")
    
    config_file = "config/default.json"
    if Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                json.load(f)
            print(f"[OK] {config_file}")
            return True
        except json.JSONDecodeError:
            print(f"[ERROR] {config_file} - JSON invalide")
            return False
    else:
        print(f"[ERROR] {config_file} manquant")
        return False


def check_runner():
    """Verifie le runner."""
    print("\n[RUNNER] Verification du runner...")
    
    try:
        result = subprocess.run(
            ["python", "runner.py", "info"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("[OK] Runner fonctionne")
            return True
        else:
            print("[ERROR] Runner echoue")
            return False
    except Exception as e:
        print(f"[ERROR] Runner: {e}")
        return False


def check_samples():
    """Verifie la creation d'exemples."""
    print("\n[SAMPLES] Test creation d'exemples...")
    
    try:
        result = subprocess.run(
            ["python", "runner.py", "samples"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            if Path("Master_BOM.xlsx").exists() and Path("Sample_Input_Data.xlsx").exists():
                print("[OK] Exemples crees")
                return True
            else:
                print("[ERROR] Fichiers d'exemple non crees")
                return False
        else:
            print("[ERROR] Creation d'exemples echouee")
            return False
    except Exception as e:
        print(f"[ERROR] Samples: {e}")
        return False


def main():
    """Fonction principale."""
    print("Component Data Processor - Verification d'installation")
    print("=" * 60)
    
    checks = [
        check_python(),
        check_files(),
        check_dependencies(),
        check_modules(),
        check_config(),
        check_runner(),
        check_samples()
    ]
    
    success_count = sum(checks)
    total_count = len(checks)
    
    print("\n" + "=" * 60)
    print(f"RESULTAT: {success_count}/{total_count} verifications reussies")
    
    if all(checks):
        print("INSTALLATION VALIDEE - Pret a l'emploi !")
        print("\nProchaines etapes:")
        print("  1. Consultez QUICKSTART.md")
        print("  2. Utilisez 'python runner.py --help'")
        print("  3. Traitez vos fichiers avec 'python runner.py process file.xlsx'")
        return True
    else:
        print("INSTALLATION INCOMPLETE")
        print("\nActions recommandees:")
        print("  1. pip install -r requirements.txt")
        print("  2. Verifiez la structure des fichiers")
        print("  3. Relancez cette verification")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
