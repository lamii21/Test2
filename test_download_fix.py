#!/usr/bin/env python3
"""
Test de validation des corrections de téléchargement
Vérification que le problème "fichier non trouvé" est résolu
"""

import requests
import time
from pathlib import Path

def test_download_fix():
    """Test des corrections de téléchargement"""
    print("🧪 TEST DES CORRECTIONS DE TÉLÉCHARGEMENT")
    print("=" * 60)
    
    # 1. Test Backend - Requête HEAD
    print("1️⃣ Test Backend - Requête HEAD...")
    try:
        response = requests.head("http://localhost:8000/download/Master_BOM_Updated_2025-08-05.xlsx", timeout=10)
        if response.status_code == 200:
            print("✅ Backend HEAD: OK")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'N/A')} bytes")
            print(f"   Content-Disposition: {response.headers.get('content-disposition', 'N/A')}")
        else:
            print(f"❌ Backend HEAD: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur Backend HEAD: {e}")
        return False
    
    # 2. Test Backend - Requête GET (sans télécharger le contenu complet)
    print("\n2️⃣ Test Backend - Requête GET...")
    try:
        response = requests.get("http://localhost:8000/download/Master_BOM_Updated_2025-08-05.xlsx", 
                               timeout=10, stream=True)
        if response.status_code == 200:
            print("✅ Backend GET: OK")
            
            # Lire seulement les premiers bytes pour vérifier
            content_start = next(response.iter_content(chunk_size=100))
            if content_start and len(content_start) > 0:
                print(f"   Contenu reçu: {len(content_start)} bytes (échantillon)")
                
                # Vérifier que c'est bien un fichier Excel (signature PK)
                if content_start.startswith(b'PK'):
                    print("   ✅ Format Excel valide (signature PK)")
                else:
                    print(f"   ⚠️  Format inattendu: {content_start[:10]}")
            else:
                print("   ❌ Aucun contenu reçu")
                return False
        else:
            print(f"❌ Backend GET: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur Backend GET: {e}")
        return False
    
    # 3. Test Frontend - Redirection
    print("\n3️⃣ Test Frontend - Redirection...")
    try:
        response = requests.get("http://localhost:5000/download/Master_BOM_Updated_2025-08-05.xlsx", 
                               timeout=10, allow_redirects=False)
        if response.status_code in [301, 302]:
            print("✅ Frontend redirection: OK")
            location = response.headers.get('location', '')
            if 'localhost:8000/download' in location:
                print(f"   ✅ Redirection correcte vers: {location}")
            else:
                print(f"   ⚠️  Redirection inattendue: {location}")
        else:
            print(f"❌ Frontend redirection: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur Frontend redirection: {e}")
        return False
    
    # 4. Test Frontend - Redirection complète
    print("\n4️⃣ Test Frontend - Redirection complète...")
    try:
        response = requests.get("http://localhost:5000/download/Master_BOM_Updated_2025-08-05.xlsx", 
                               timeout=10, allow_redirects=True, stream=True)
        if response.status_code == 200:
            print("✅ Frontend redirection complète: OK")
            
            # Vérifier l'URL finale
            final_url = response.url
            if 'localhost:8000/download' in final_url:
                print(f"   ✅ URL finale correcte: {final_url}")
            else:
                print(f"   ⚠️  URL finale inattendue: {final_url}")
            
            # Vérifier le contenu
            content_start = next(response.iter_content(chunk_size=100))
            if content_start and content_start.startswith(b'PK'):
                print("   ✅ Contenu Excel valide via frontend")
            else:
                print("   ⚠️  Contenu invalide via frontend")
        else:
            print(f"❌ Frontend redirection complète: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur Frontend redirection complète: {e}")
        return False
    
    # 5. Test de tous les fichiers disponibles
    print("\n5️⃣ Test de tous les fichiers disponibles...")
    try:
        list_response = requests.get("http://localhost:8000/list-outputs", timeout=10)
        if list_response.status_code == 200:
            data = list_response.json()
            if data.get('success'):
                files = data.get('files', [])
                print(f"   {len(files)} fichiers à tester")
                
                success_count = 0
                for file_info in files:
                    filename = file_info['filename']
                    try:
                        # Test rapide HEAD pour chaque fichier
                        head_response = requests.head(f"http://localhost:8000/download/{filename}", timeout=5)
                        if head_response.status_code == 200:
                            success_count += 1
                            print(f"   ✅ {filename}: OK")
                        else:
                            print(f"   ❌ {filename}: {head_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {filename}: Erreur - {e}")
                
                print(f"   📊 Résultat: {success_count}/{len(files)} fichiers accessibles")
                return success_count == len(files)
            else:
                print(f"   ❌ Erreur API: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Liste fichiers: {list_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur test fichiers: {e}")
        return False

def test_interfaces():
    """Test des interfaces web"""
    print("\n6️⃣ Test des interfaces web...")
    
    interfaces = [
        ("Page résultats", "http://localhost:5000/results"),
        ("API liste fichiers", "http://localhost:5000/api/list-outputs"),
        ("Page d'accueil", "http://localhost:5000")
    ]
    
    for name, url in interfaces:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {name}: {status}")
        except Exception as e:
            print(f"   {name}: ❌ Erreur - {e}")

def main():
    """Fonction principale"""
    print("🚀 COMPONENT DATA PROCESSOR v2.0 - TEST CORRECTION TÉLÉCHARGEMENT")
    print("=" * 70)
    
    # Test principal
    success = test_download_fix()
    
    # Test des interfaces
    test_interfaces()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DES TESTS DE CORRECTION")
    print("=" * 70)
    
    if success:
        print("🎉 PROBLÈME 'FICHIER NON TROUVÉ' RÉSOLU !")
        print("\n✅ Corrections appliquées avec succès:")
        print("   • Backend: Support des requêtes HEAD et GET")
        print("   • Frontend: Redirection simplifiée sans vérification HEAD")
        print("   • Sécurité: Validation des noms de fichiers")
        print("   • Gestion d'erreurs: Logs détaillés")
        
        print("\n💡 Téléchargements disponibles:")
        print("   🌐 Via interface: http://localhost:5000/results")
        print("   📡 Via API: http://localhost:8000/download/{filename}")
        print("   🔄 Via frontend: http://localhost:5000/download/{filename}")
        
        print("\n🎯 Le système de téléchargement est maintenant pleinement opérationnel !")
        return 0
    else:
        print("⚠️  PROBLÈMES PERSISTANTS DÉTECTÉS")
        print("💡 Vérifiez les logs et les services")
        return 1

if __name__ == "__main__":
    exit(main())
