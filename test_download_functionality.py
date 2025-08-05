#!/usr/bin/env python3
"""
Test des fonctionnalités de téléchargement
Validation complète du système de téléchargement
"""

import requests
import time
from pathlib import Path

def test_download_functionality():
    """Test complet des fonctionnalités de téléchargement"""
    print("🧪 TEST DES FONCTIONNALITÉS DE TÉLÉCHARGEMENT")
    print("=" * 60)
    
    # 1. Test Liste des fichiers de sortie (Backend)
    print("1️⃣ Test Liste des fichiers (Backend)...")
    try:
        response = requests.get("http://localhost:8000/list-outputs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                files_count = data.get('count', 0)
                files = data.get('files', [])
                print(f"✅ Backend: {files_count} fichiers disponibles")
                
                for i, file_info in enumerate(files[:3], 1):  # Afficher les 3 premiers
                    size_mb = round(file_info['size'] / 1024 / 1024, 2)
                    print(f"   {i}. {file_info['filename']} ({size_mb} MB)")
                
                if files_count > 3:
                    print(f"   ... et {files_count - 3} autres fichiers")
                
                return files
            else:
                print(f"❌ Backend API Error: {data.get('message')}")
                return []
        else:
            print(f"❌ Backend API: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur Backend API: {e}")
        return []

def test_frontend_download_api():
    """Test de l'API de téléchargement du frontend"""
    print("\n2️⃣ Test API Frontend...")
    try:
        response = requests.get("http://localhost:5000/api/list-outputs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                files_count = data.get('count', 0)
                print(f"✅ Frontend API: {files_count} fichiers via frontend")
                
                # Vérifier que les URLs de téléchargement frontend sont présentes
                files = data.get('files', [])
                if files:
                    first_file = files[0]
                    if 'frontend_download_url' in first_file:
                        print(f"✅ URLs de téléchargement frontend configurées")
                        return files
                    else:
                        print(f"⚠️  URLs de téléchargement frontend manquantes")
                        return files
                else:
                    print(f"⚠️  Aucun fichier disponible")
                    return []
            else:
                print(f"❌ Frontend API Error: {data.get('message')}")
                return []
        else:
            print(f"❌ Frontend API: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur Frontend API: {e}")
        return []

def test_download_endpoints(files):
    """Test des endpoints de téléchargement"""
    if not files:
        print("\n3️⃣ Test Téléchargement: Aucun fichier à tester")
        return
    
    print(f"\n3️⃣ Test Endpoints de Téléchargement...")
    
    # Tester le premier fichier
    test_file = files[0]
    filename = test_file['filename']
    
    # Test téléchargement direct backend
    print(f"   Test Backend: {filename}")
    try:
        backend_url = f"http://localhost:8000/download/{filename}"
        response = requests.head(backend_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend téléchargement: OK")
            
            # Vérifier les headers
            content_type = response.headers.get('content-type', '')
            if 'excel' in content_type or 'spreadsheet' in content_type:
                print(f"   ✅ Content-Type correct: {content_type}")
            else:
                print(f"   ⚠️  Content-Type: {content_type}")
        else:
            print(f"   ❌ Backend téléchargement: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Backend téléchargement: {e}")
    
    # Test redirection frontend
    print(f"   Test Frontend: {filename}")
    try:
        frontend_url = f"http://localhost:5000/download/{filename}"
        response = requests.head(frontend_url, timeout=5, allow_redirects=False)
        if response.status_code in [302, 301]:  # Redirection
            print(f"   ✅ Frontend redirection: OK")
            
            # Vérifier la redirection
            location = response.headers.get('location', '')
            if backend_url in location:
                print(f"   ✅ Redirection vers backend: OK")
            else:
                print(f"   ⚠️  Redirection: {location}")
        else:
            print(f"   ❌ Frontend redirection: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Frontend redirection: {e}")

def test_complete_workflow():
    """Test du workflow complet avec téléchargement"""
    print("\n4️⃣ Test Workflow Complet...")
    
    # Vérifier qu'un fichier de test existe
    test_file = Path("Sample_Input_Data.xlsx")
    if not test_file.exists():
        print("❌ Fichier de test non trouvé")
        return False
    
    try:
        # 1. Upload
        print("   Upload du fichier de test...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            upload_response = requests.post("http://localhost:8000/upload", files=files, timeout=30)
        
        if upload_response.status_code != 200:
            print(f"   ❌ Upload échoué: {upload_response.status_code}")
            return False
        
        upload_data = upload_response.json()
        if not upload_data.get('success'):
            print(f"   ❌ Upload error: {upload_data.get('message')}")
            return False
        
        file_id = upload_data['file_id']
        filename = upload_data['filename']
        print(f"   ✅ Upload réussi: {file_id}")
        
        # 2. Traitement
        print("   Traitement du fichier...")
        process_response = requests.post(
            "http://localhost:8000/process",
            params={
                'file_id': file_id,
                'filename': filename,
                'project_column': 'V710_AWD_PP_YOTK'
            },
            timeout=60
        )
        
        if process_response.status_code != 200:
            print(f"   ❌ Traitement échoué: {process_response.status_code}")
            return False
        
        process_data = process_response.json()
        if not process_data.get('success'):
            print(f"   ❌ Traitement error: {process_data.get('message')}")
            return False
        
        print(f"   ✅ Traitement réussi")
        
        # 3. Vérifier les fichiers de sortie
        output_files = process_data.get('output_files', [])
        if output_files:
            print(f"   ✅ {len(output_files)} fichier(s) de sortie généré(s)")
            for output_file in output_files:
                print(f"      - {output_file['filename']} ({round(output_file['size']/1024, 1)} KB)")
        else:
            print(f"   ⚠️  Aucun fichier de sortie dans la réponse")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur workflow: {e}")
        return False

def test_interfaces():
    """Test des interfaces web"""
    print("\n5️⃣ Test Interfaces Web...")
    
    interfaces = [
        ("Page d'accueil", "http://localhost:5000"),
        ("Page résultats", "http://localhost:5000/results"),
        ("Interface avancée", "http://localhost:5000/enhanced"),
        ("API Backend", "http://localhost:8000/health")
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
    print("🚀 COMPONENT DATA PROCESSOR v2.0 - TEST TÉLÉCHARGEMENT")
    print("=" * 70)
    
    # Test des APIs
    backend_files = test_download_functionality()
    frontend_files = test_frontend_download_api()
    
    # Test des endpoints
    test_download_endpoints(backend_files)
    
    # Test workflow complet
    workflow_success = test_complete_workflow()
    
    # Test des interfaces
    test_interfaces()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DES TESTS DE TÉLÉCHARGEMENT")
    print("=" * 70)
    
    backend_ok = len(backend_files) > 0
    frontend_ok = len(frontend_files) > 0
    
    print(f"✅ Backend API: {'OK' if backend_ok else 'ERREUR'} ({len(backend_files)} fichiers)")
    print(f"✅ Frontend API: {'OK' if frontend_ok else 'ERREUR'} ({len(frontend_files)} fichiers)")
    print(f"✅ Workflow complet: {'OK' if workflow_success else 'ERREUR'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 FONCTIONNALITÉS DE TÉLÉCHARGEMENT OPÉRATIONNELLES !")
        print("\n💡 Utilisation:")
        print("   🌐 Interface: http://localhost:5000")
        print("   📥 Résultats: http://localhost:5000/results")
        print("   📡 API: http://localhost:8000/list-outputs")
        
        if backend_files:
            print(f"\n📊 Fichiers disponibles:")
            for file_info in backend_files[:3]:
                size_mb = round(file_info['size'] / 1024 / 1024, 2)
                print(f"   📄 {file_info['filename']} ({size_mb} MB)")
                print(f"      🔗 {file_info['download_url']}")
        
        return 0
    else:
        print("\n⚠️  PROBLÈMES DÉTECTÉS")
        return 1

if __name__ == "__main__":
    exit(main())
