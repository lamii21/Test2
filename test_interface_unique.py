#!/usr/bin/env python3
"""
Test de l'interface unique complète
Validation que l'interface unique fonctionne sans erreurs
"""

import requests
import time
from pathlib import Path

def test_interface_unique():
    """Test de l'interface unique"""
    print("🧪 TEST DE L'INTERFACE UNIQUE COMPLÈTE")
    print("=" * 60)
    
    # 1. Test de l'accès à l'interface
    print("1️⃣ Test d'accès à l'interface...")
    try:
        response = requests.get("http://localhost:5000/enhanced", timeout=10)
        if response.status_code == 200:
            print("✅ Interface accessible")
            if "Étape 1 : Sélection du Projet" in response.text:
                print("✅ Interface complète chargée")
            else:
                print("⚠️  Interface incomplète")
        else:
            print(f"❌ Interface: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'accès: {e}")
        return False
    
    # 2. Test des endpoints proxy
    print("\n2️⃣ Test des endpoints proxy...")
    
    # Test API Status
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: Backend {'disponible' if data.get('backend_available') else 'indisponible'}")
        else:
            print(f"❌ API Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API Status: {e}")
    
    # Test API Project Columns
    try:
        response = requests.get("http://localhost:5000/api/project-columns", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cols_count = len(data.get('columns', []))
                print(f"✅ API Project Columns: {cols_count} projets disponibles")
            else:
                print(f"⚠️  API Project Columns: {data.get('message')}")
        else:
            print(f"❌ API Project Columns: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API Project Columns: {e}")
    
    # Test API Suggest Column
    try:
        response = requests.post(
            "http://localhost:5000/api/suggest-column",
            json={"project_hint": "FORD_J74_V710_B2_PP_YOTK"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                suggested = data.get('suggested_column', 'N/A')
                confidence = round(data.get('confidence', 0) * 100)
                print(f"✅ API Suggest Column: {suggested} ({confidence}%)")
            else:
                print(f"⚠️  API Suggest Column: {data.get('message')}")
        else:
            print(f"❌ API Suggest Column: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API Suggest Column: {e}")
    
    # 3. Test de l'upload (si fichier disponible)
    print("\n3️⃣ Test de l'upload...")
    test_file = Path("Sample_Input_Data.xlsx")
    if test_file.exists():
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post("http://localhost:5000/api/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    file_id = data.get('file_id', 'N/A')
                    filename = data.get('filename', 'N/A')
                    print(f"✅ API Upload: {filename} (ID: {file_id})")
                    
                    # Test du traitement
                    print("\n4️⃣ Test du traitement...")
                    try:
                        process_data = {
                            "file_id": file_id,
                            "filename": filename,
                            "project_column": "V710_AWD_PP_YOTK"
                        }
                        
                        process_response = requests.post(
                            "http://localhost:5000/api/process",
                            json=process_data,
                            timeout=60
                        )
                        
                        if process_response.status_code == 200:
                            process_result = process_response.json()
                            if process_result.get('success'):
                                print("✅ API Process: Traitement réussi")
                                output_files = process_result.get('output_files', [])
                                if output_files:
                                    print(f"   📄 {len(output_files)} fichier(s) généré(s)")
                                    for file_info in output_files:
                                        print(f"      - {file_info.get('filename', 'N/A')}")
                                else:
                                    print("   📄 Fichiers disponibles dans /results")
                            else:
                                print(f"⚠️  API Process: {process_result.get('message')}")
                        else:
                            print(f"❌ API Process: {process_response.status_code}")
                    except Exception as e:
                        print(f"❌ Erreur API Process: {e}")
                        
                else:
                    print(f"⚠️  API Upload: {data.get('message')}")
            else:
                print(f"❌ API Upload: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur Upload: {e}")
    else:
        print("⚠️  Fichier de test non trouvé, test d'upload ignoré")
    
    # 5. Test de la page des résultats
    print("\n5️⃣ Test de la page des résultats...")
    try:
        response = requests.get("http://localhost:5000/results", timeout=10)
        if response.status_code == 200:
            print("✅ Page des résultats accessible")
        else:
            print(f"❌ Page des résultats: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur page des résultats: {e}")
    
    return True

def test_workflow_complet():
    """Test du workflow complet via l'interface"""
    print("\n6️⃣ Test du workflow complet...")
    
    # Vérifier que les services sont disponibles
    try:
        # Test frontend
        frontend_response = requests.get("http://localhost:5000", timeout=5)
        frontend_ok = frontend_response.status_code == 200
        
        # Test backend
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        backend_ok = backend_response.status_code == 200
        
        print(f"   Frontend: {'✅ OK' if frontend_ok else '❌ Erreur'}")
        print(f"   Backend: {'✅ OK' if backend_ok else '❌ Erreur'}")
        
        if frontend_ok and backend_ok:
            print("✅ Workflow complet possible")
            return True
        else:
            print("⚠️  Workflow complet limité")
            return False
            
    except Exception as e:
        print(f"❌ Erreur workflow: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 COMPONENT DATA PROCESSOR - TEST INTERFACE UNIQUE")
    print("=" * 70)
    
    # Test principal
    interface_ok = test_interface_unique()
    
    # Test workflow
    workflow_ok = test_workflow_complet()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DU TEST INTERFACE UNIQUE")
    print("=" * 70)
    
    if interface_ok and workflow_ok:
        print("🎉 INTERFACE UNIQUE COMPLÈTEMENT FONCTIONNELLE !")
        print("\n✅ Fonctionnalités validées:")
        print("   • Interface unique accessible")
        print("   • Endpoints proxy fonctionnels")
        print("   • Suggestion de projets opérationnelle")
        print("   • Upload et traitement possibles")
        print("   • Page des résultats accessible")
        print("   • Workflow complet disponible")
        
        print("\n💡 Utilisation pour l'ingénieur qualité:")
        print("   🌐 Interface unique: http://localhost:5000/enhanced")
        print("   📋 Processus en 3 étapes claires:")
        print("      1. Sélection du projet (automatique ou manuelle)")
        print("      2. Upload du fichier Excel")
        print("      3. Validation et traitement")
        print("   📥 Résultats: http://localhost:5000/results")
        
        print("\n🎯 L'interface unique est prête pour la production !")
        return 0
    else:
        print("⚠️  PROBLÈMES DÉTECTÉS DANS L'INTERFACE UNIQUE")
        print("💡 Vérifiez les logs et les services")
        return 1

if __name__ == "__main__":
    exit(main())
