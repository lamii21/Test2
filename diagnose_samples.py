#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes avec la création d'exemples
"""

import sys
import subprocess
from pathlib import Path
import traceback

def test_samples_creation():
    """Test la création d'exemples et diagnostique les problèmes."""
    
    print("🔍 DIAGNOSTIC - Création d'exemples")
    print("=" * 50)
    
    # Test 1: Vérifier l'environnement
    print("\n📋 Test 1: Environnement")
    print(f"Python: {sys.version}")
    print(f"Répertoire: {Path.cwd()}")
    
    # Test 2: Vérifier les fichiers nécessaires
    print("\n📋 Test 2: Fichiers nécessaires")
    required_files = [
        'runner.py',
        'examples/create_sample_master_bom.py',
        'examples/create_sample_input.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
    
    # Test 3: Vérifier les dépendances
    print("\n📋 Test 3: Dépendances")
    try:
        import pandas
        print(f"✅ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"❌ pandas: {e}")
    
    try:
        import openpyxl
        print(f"✅ openpyxl {openpyxl.__version__}")
    except ImportError as e:
        print(f"❌ openpyxl: {e}")
    
    # Test 4: Tester la création via CLI
    print("\n📋 Test 4: Création via CLI")
    try:
        result = subprocess.run(
            ['python', 'runner.py', 'samples'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(f"Code de retour: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ CLI fonctionne")
            print("Sortie:")
            print(result.stdout)
        else:
            print("❌ CLI échoue")
            print("Erreur:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de l'exécution")
    except Exception as e:
        print(f"❌ Exception: {e}")
        traceback.print_exc()
    
    # Test 5: Vérifier les fichiers créés
    print("\n📋 Test 5: Fichiers créés")
    expected_files = [
        'Master_BOM.xlsx',
        'Sample_Input_Data.xlsx',
        'Sample_Invalid_Data.xlsx',
        'Sample_New_Components.xlsx'
    ]
    
    for file_path in expected_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - NON CRÉÉ")
    
    # Test 6: Tester l'import des modules
    print("\n📋 Test 6: Import des modules")
    try:
        from examples.create_sample_master_bom import create_sample_master_bom
        print("✅ create_sample_master_bom importé")
        
        from examples.create_sample_input import create_sample_input
        print("✅ create_sample_input importé")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        traceback.print_exc()
    
    # Test 7: Tester la création directe
    print("\n📋 Test 7: Création directe")
    try:
        from examples.create_sample_master_bom import create_sample_master_bom
        from examples.create_sample_input import create_sample_input
        
        print("Création du Master BOM...")
        create_sample_master_bom()
        print("✅ Master BOM créé")
        
        print("Création des données d'entrée...")
        create_sample_input()
        print("✅ Données d'entrée créées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création directe: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC TERMINÉ")
    
    # Résumé
    if all(Path(f).exists() for f in expected_files):
        print("✅ RÉSULTAT: Tous les fichiers ont été créés avec succès")
        print("💡 Le problème pourrait être dans l'interface web")
    else:
        print("❌ RÉSULTAT: Problème avec la création des fichiers")
        print("💡 Vérifiez les erreurs ci-dessus")

if __name__ == '__main__':
    test_samples_creation()
