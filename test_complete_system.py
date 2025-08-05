#!/usr/bin/env python3
"""
Test complet du système Backend FastAPI + Frontend Flask
"""

import requests
import time
from pathlib import Path

def test_complete_system():
    """Test complet du système"""
    print("🧪 TEST COMPLET DU SYSTÈME")
    print("=" * 50)
    
    # 1. Test Backend Health
    print("1️⃣ Test Backend Health...")
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code == 200:
            data = health.json()
            print(f"   ✅ Backend: {data['status']}")
            print(f"   📊 Master BOM: {'✅' if data['master_bom_available'] else '❌'}")
        else:
            print(f"   ❌ Backend Health: {health.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend non disponible: {e}")
        return False
    
    # 2. Test Frontend Health
    print("\n2️⃣ Test Frontend Health...")
    try:
        frontend = requests.get("http://localhost:5000", timeout=5)
        if frontend.status_code == 200:
            print("   ✅ Frontend accessible")
        else:
            print(f"   ❌ Frontend: {frontend.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend non disponible: {e}")
        return False
    
    # 3. Test API Project Columns via Frontend
    print("\n3️⃣ Test API Colonnes de Projets...")
    try:
        columns = requests.get("http://localhost:5000/api/project-columns", timeout=10)
        if columns.status_code == 200:
            data = columns.json()
            if data.get('success'):
                cols = data.get('columns', [])
                print(f"   ✅ {len(cols)} colonnes détectées")
                
                # Trouver une colonne V710 pour le test
                v710_cols = [col for col in cols if 'V710' in col['name']]
                if v710_cols:
                    best_col = v710_cols[0]['name']
                    print(f"   🎯 Colonne de test: {best_col}")
                    return best_col
                else:
                    print("   ⚠️  Aucune colonne V710 trouvée")
                    return cols[0]['name'] if cols else None
            else:
                print(f"   ❌ API Error: {data.get('message')}")
                return False
        else:
            print(f"   ❌ API Columns: {columns.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur API Columns: {e}")
        return False

def test_backend_upload():
    """Test direct du backend pour upload et traitement"""
    print("\n4️⃣ Test Backend Upload Direct...")
    
    # Vérifier si le fichier de test existe
    test_file = Path("Sample_Input_Data.xlsx")
    if not test_file.exists():
        print("   ❌ Fichier de test non trouvé: Sample_Input_Data.xlsx")
        return False
    
    try:
        # Upload direct vers le backend
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            upload_response = requests.post("http://localhost:8000/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            if upload_data.get('success'):
                print(f"   ✅ Upload réussi: {upload_data['filename']}")
                
                # Test traitement avec colonne de projet
                process_response = requests.post(
                    "http://localhost:8000/process",
                    params={
                        'file_id': upload_data['file_id'],
                        'filename': upload_data['filename'],
                        'project_column': 'V710_AWD_PP_YOTK'  # Colonne de test
                    },
                    timeout=60
                )
                
                if process_response.status_code == 200:
                    process_data = process_response.json()
                    print(f"   ✅ Traitement: {'Réussi' if process_data.get('success') else 'Échoué'}")
                    if not process_data.get('success'):
                        print(f"   📝 Message: {process_data.get('message')}")
                        print(f"   📄 Stdout: {process_data.get('stdout', '')[:200]}...")
                    return process_data.get('success', False)
                else:
                    print(f"   ❌ Traitement: {process_response.status_code}")
                    return False
            else:
                print(f"   ❌ Upload échoué: {upload_data.get('message')}")
                return False
        else:
            print(f"   ❌ Upload: {upload_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test backend: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 COMPONENT DATA PROCESSOR v2.0 - TEST COMPLET")
    print("=" * 60)
    
    # Test du système
    project_column = test_complete_system()
    
    if not project_column:
        print("\n❌ Tests de base échoués")
        return 1
    
    # Test backend direct
    backend_success = test_backend_upload()
    
    # Résumé
    print("\n📋 RÉSUMÉ DES TESTS:")
    print(f"   Backend Health: ✅")
    print(f"   Frontend Health: ✅") 
    print(f"   API Columns: ✅ ({project_column})")
    print(f"   Backend Upload/Process: {'✅' if backend_success else '❌'}")
    
    if backend_success:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("💡 Le système est opérationnel et prêt à l'emploi")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("💡 Vérifiez les logs pour plus de détails")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
