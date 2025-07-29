#!/usr/bin/env python3
"""
Script de démarrage pour l'interface web du Component Data Processor
"""

import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 Component Data Processor - Interface Web")
    print("=" * 50)
    
    # Vérifier que les fichiers nécessaires existent
    required_files = [
        'simple_web.py',
        'frontend/templates/index.html',
        'frontend/templates/base.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Fichiers manquants:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n💡 Assurez-vous d'être dans le bon répertoire")
        return False
    
    print("✅ Tous les fichiers nécessaires sont présents")
    print("🌐 Démarrage du serveur web...")
    print("📱 L'interface sera disponible sur: http://localhost:5000")
    print("🔧 Utilisez Ctrl+C pour arrêter le serveur")
    print("\n" + "=" * 50)
    
    # Démarrer le serveur
    try:
        import subprocess
        
        # Lancer le serveur en arrière-plan
        process = subprocess.Popen(
            [sys.executable, 'simple_web.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Attendre un peu que le serveur démarre
        time.sleep(3)
        
        # Vérifier si le serveur est toujours en cours d'exécution
        if process.poll() is None:
            print("✅ Serveur démarré avec succès !")
            print("🌐 Ouverture du navigateur...")
            
            # Ouvrir le navigateur
            webbrowser.open('http://localhost:5000')
            
            print("\n📋 Interface web disponible avec les fonctionnalités :")
            print("   • Upload et traitement de fichiers Excel")
            print("   • Création de fichiers d'exemple")
            print("   • Validation des données")
            print("   • Téléchargement des résultats")
            print("   • Statut du système en temps réel")
            
            print("\n🎯 Pour arrêter le serveur :")
            print("   • Fermez cette fenêtre")
            print("   • Ou utilisez Ctrl+C")
            
            # Attendre que l'utilisateur arrête le serveur
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Arrêt du serveur...")
                process.terminate()
                process.wait()
                print("✅ Serveur arrêté")
        
        else:
            # Le serveur a échoué à démarrer
            stdout, stderr = process.communicate()
            print("❌ Erreur lors du démarrage du serveur")
            if stderr:
                print(f"Erreur: {stderr.decode()}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            print("\n💡 Vous pouvez aussi utiliser l'interface en ligne de commande :")
            print("   python runner.py --help")
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("\n💡 Utilisez l'interface en ligne de commande :")
        print("   python runner.py --help")
