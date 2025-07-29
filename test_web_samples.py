#!/usr/bin/env python3
"""
Test de l'interface web pour la création d'exemples
"""

import requests
import time

def test_web_samples():
    """Teste la création d'exemples via l'interface web."""
    
    print("Test de l'interface web - Creation d'exemples")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test 1: Vérifier que le serveur répond
        print("1. Test de connexion au serveur...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur accessible")
        else:
            print(f"❌ Serveur inaccessible: {response.status_code}")
            return False
        
        # Test 2: Accéder à la page samples
        print("2. Test de la page samples...")
        response = requests.get(f"{base_url}/samples", timeout=5)
        if response.status_code == 200:
            print("✅ Page samples accessible")
        else:
            print(f"❌ Page samples inaccessible: {response.status_code}")
            return False
        
        # Test 3: Tester la création d'exemples via POST
        print("3. Test de création d'exemples...")
        response = requests.post(f"{base_url}/samples", timeout=60)
        
        if response.status_code == 200:
            print("✅ Requête POST réussie")
            
            # Vérifier le contenu de la réponse
            if "succès" in response.text or "success" in response.text:
                print("✅ Création d'exemples réussie")
                return True
            elif "erreur" in response.text.lower() or "error" in response.text.lower():
                print("❌ Erreur dans la création")
                print("Contenu de la réponse:")
                print(response.text[:500])
                return False
            else:
                print("⚠️ Réponse ambiguë")
                return False
        else:
            print(f"❌ Requête POST échouée: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur web est démarré:")
        print("   python simple_web.py")
        return False
    
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de la requête")
        return False
    
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == '__main__':
    try:
        import requests
    except ImportError:
        print("❌ Module 'requests' non installé")
        print("💡 Installez-le avec: pip install requests")
        exit(1)
    
    success = test_web_samples()
    
    if success:
        print("\n🎉 SUCCÈS: L'interface web fonctionne correctement!")
    else:
        print("\n❌ ÉCHEC: Problème avec l'interface web")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que le serveur web est démarré")
        print("   2. Testez la CLI: python runner.py samples")
        print("   3. Vérifiez les logs du serveur web")
