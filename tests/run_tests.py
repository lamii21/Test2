#!/usr/bin/env python3
"""
Script pour exécuter tous les tests unitaires du Component Data Processor.
"""

import unittest
import sys
from pathlib import Path
import coverage

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests_with_coverage():
    """Exécute les tests avec mesure de couverture de code."""
    print("Démarrage des tests avec mesure de couverture...")
    
    # Initialiser la mesure de couverture
    cov = coverage.Coverage(source=['src'])
    cov.start()
    
    try:
        # Découvrir et exécuter tous les tests
        loader = unittest.TestLoader()
        start_dir = Path(__file__).parent
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Exécuter les tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Arrêter la mesure de couverture
        cov.stop()
        cov.save()
        
        # Afficher le rapport de couverture
        print("\n" + "="*60)
        print("RAPPORT DE COUVERTURE DE CODE")
        print("="*60)
        cov.report()
        
        # Générer un rapport HTML si possible
        try:
            cov.html_report(directory='tests/coverage_html')
            print(f"\nRapport HTML généré dans: tests/coverage_html/index.html")
        except Exception as e:
            print(f"Impossible de générer le rapport HTML: {e}")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution des tests: {e}")
        return False


def run_tests_simple():
    """Exécute les tests sans mesure de couverture."""
    print("Démarrage des tests...")
    
    # Découvrir et exécuter tous les tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_module):
    """Exécute un module de test spécifique."""
    print(f"Exécution du module de test: {test_module}")
    
    try:
        # Importer et exécuter le module spécifique
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_module)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution du test {test_module}: {e}")
        return False


def print_test_summary():
    """Affiche un résumé des tests disponibles."""
    print("Tests disponibles:")
    print("- test_data_cleaner: Tests pour le nettoyage des données")
    print("- test_lookup_processor: Tests pour le processus de lookup")
    print("- test_validators: Tests pour la validation des données")
    print("\nUtilisation:")
    print("  python run_tests.py                    # Tous les tests")
    print("  python run_tests.py --coverage        # Avec couverture")
    print("  python run_tests.py --module <name>   # Test spécifique")
    print("  python run_tests.py --list            # Liste des tests")


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Exécuteur de tests pour Component Data Processor')
    parser.add_argument('--coverage', action='store_true', help='Mesurer la couverture de code')
    parser.add_argument('--module', help='Exécuter un module de test spécifique')
    parser.add_argument('--list', action='store_true', help='Lister les tests disponibles')
    
    args = parser.parse_args()
    
    if args.list:
        print_test_summary()
        return
    
    if args.module:
        success = run_specific_test(args.module)
    elif args.coverage:
        try:
            success = run_tests_with_coverage()
        except ImportError:
            print("Module 'coverage' non installé. Installation avec: pip install coverage")
            print("Exécution des tests sans mesure de couverture...")
            success = run_tests_simple()
    else:
        success = run_tests_simple()
    
    if success:
        print("\n✅ Tous les tests ont réussi!")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)


if __name__ == '__main__':
    main()
