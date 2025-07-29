#!/usr/bin/env python3
"""
Démonstration complète du Component Data Processor

Ce script montre toutes les fonctionnalités principales
du Component Data Processor de manière interactive.
"""

import os
import sys
import time
from pathlib import Path


def print_header(title):
    """Affiche un en-tête formaté."""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)


def print_step(step, description):
    """Affiche une étape de la démonstration."""
    print(f"\n📋 Étape {step}: {description}")
    print("-" * 40)


def wait_for_user():
    """Attend que l'utilisateur appuie sur Entrée."""
    input("\n⏸️  Appuyez sur Entrée pour continuer...")


def run_command(cmd, description=""):
    """Exécute une commande et affiche le résultat."""
    if description:
        print(f"🚀 {description}")
    print(f"💻 Commande: {cmd}")
    
    result = os.system(cmd)
    if result == 0:
        print("✅ Succès")
    else:
        print("❌ Erreur")
    
    return result == 0


def demo_runner():
    """Démonstration du runner."""
    print_header("DÉMONSTRATION DU COMPONENT DATA PROCESSOR")
    
    print("""
🎉 Bienvenue dans la démonstration du Component Data Processor !

Cette démonstration vous montrera :
1. 📊 Les informations du projet
2. 🔧 La configuration de l'environnement
3. 📋 La création de fichiers d'exemple
4. 🚀 Le traitement des données
5. ✅ La validation des fichiers
6. 🧪 L'exécution des tests
    """)
    
    wait_for_user()
    
    # Étape 1: Informations du projet
    print_step(1, "Informations du projet")
    run_command("python runner.py info", "Affichage des informations")
    wait_for_user()
    
    # Étape 2: Statut du projet
    print_step(2, "Statut du projet")
    run_command("python runner.py status", "Vérification du statut")
    wait_for_user()
    
    # Étape 3: Création des fichiers d'exemple
    print_step(3, "Création des fichiers d'exemple")
    run_command("python runner.py samples", "Génération des exemples")
    
    print("\n📁 Fichiers créés:")
    for file in ["Master_BOM.xlsx", "Sample_Input_Data.xlsx", "Sample_Invalid_Data.xlsx"]:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (manquant)")
    
    wait_for_user()
    
    # Étape 4: Validation d'un fichier
    print_step(4, "Validation d'un fichier")
    run_command("python runner.py validate Sample_Input_Data.xlsx", 
                "Validation du fichier d'exemple")
    wait_for_user()
    
    # Étape 5: Traitement des données
    print_step(5, "Traitement des données")
    run_command("python runner.py process Sample_Input_Data.xlsx", 
                "Traitement du fichier d'exemple")
    
    print("\n📁 Fichiers de sortie générés:")
    output_dir = Path("output")
    if output_dir.exists():
        for file in output_dir.glob("*"):
            print(f"  📄 {file.name}")
    
    wait_for_user()
    
    # Étape 6: Configuration
    print_step(6, "Gestion de la configuration")
    run_command("python runner.py config list", "Liste des configurations")
    run_command("python runner.py config create demo", "Création d'une config demo")
    wait_for_user()
    
    # Étape 7: Tests (optionnel)
    print_step(7, "Tests unitaires (optionnel)")
    print("🧪 Voulez-vous exécuter les tests unitaires ?")
    response = input("(o/N): ").lower().strip()
    
    if response in ['o', 'oui', 'y', 'yes']:
        run_command("python runner.py test", "Exécution des tests")
    else:
        print("⏭️  Tests ignorés")
    
    # Conclusion
    print_header("DÉMONSTRATION TERMINÉE")
    print("""
🎉 Félicitations ! Vous avez terminé la démonstration.

📚 Prochaines étapes recommandées :

1. 📖 Lire la documentation complète :
   - README.md (guide utilisateur)
   - QUICKSTART.md (démarrage rapide)
   - docs/ARCHITECTURE.md (architecture technique)

2. 🔧 Personnaliser la configuration :
   - Éditer config/default.json
   - Créer vos propres configurations

3. 🚀 Utiliser avec vos données :
   - Remplacer Master_BOM.xlsx par votre fichier
   - Traiter vos fichiers d'entrée

4. 🧪 Intégrer dans vos workflows :
   - Utiliser l'API programmatique
   - Automatiser avec des scripts

📞 Besoin d'aide ?
   - Consultez la documentation dans docs/
   - Utilisez 'python runner.py --help'
   - Vérifiez le statut avec 'python runner.py status'

Merci d'avoir testé le Component Data Processor ! 🚀
    """)


def demo_api():
    """Démonstration de l'API programmatique."""
    print_header("DÉMONSTRATION API PROGRAMMATIQUE")
    
    print("""
🔧 Cette démonstration montre comment utiliser le Component Data Processor
   directement dans votre code Python.
    """)
    
    # Code d'exemple
    example_code = '''
from src.component_processor.processor import ComponentDataProcessor

# Initialiser le processeur
processor = ComponentDataProcessor()

# Traiter un fichier
success = processor.process_file("Sample_Input_Data.xlsx")

if success:
    print("✅ Traitement réussi")
    
    # Obtenir les statistiques
    stats = processor.get_global_statistics()
    print(f"Lignes traitées: {stats['total_rows_processed']}")
    print(f"Durée: {stats['total_duration']:.2f}s")
else:
    print("❌ Traitement échoué")
'''
    
    print("💻 Exemple de code:")
    print(example_code)
    
    print("\n🚀 Voulez-vous exécuter cet exemple ?")
    response = input("(o/N): ").lower().strip()
    
    if response in ['o', 'oui', 'y', 'yes']:
        try:
            # S'assurer que les exemples existent
            if not Path("Sample_Input_Data.xlsx").exists():
                print("📋 Création des fichiers d'exemple...")
                os.system("python runner.py samples")
            
            # Exécuter l'exemple
            print("\n🔄 Exécution de l'exemple...")
            
            from src.component_processor.processor import ComponentDataProcessor
            
            processor = ComponentDataProcessor()
            success = processor.process_file("Sample_Input_Data.xlsx")
            
            if success:
                print("✅ Traitement réussi")
                stats = processor.get_global_statistics()
                print(f"Lignes traitées: {stats['total_rows_processed']}")
                print(f"Durée: {stats['total_duration']:.2f}s")
            else:
                print("❌ Traitement échoué")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print("\n📚 Pour plus d'exemples, consultez docs/API_REFERENCE.md")


def main():
    """Fonction principale de la démonstration."""
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        demo_api()
    else:
        demo_runner()


if __name__ == "__main__":
    main()
