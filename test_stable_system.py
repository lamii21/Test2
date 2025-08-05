#!/usr/bin/env python3
"""
Test complet du système stable
Validation de toutes les fonctionnalités
"""

import requests
import time
from pathlib import Path

def test_stable_system():
    """Test complet du système stable"""
    print("🧪 TEST COMPLET DU SYSTÈME STABLE")
    print("=" * 60)
    
    results = {
        "backend_health": False,
        "frontend_health": False,
        "project_columns": False,
        "suggestion": False,
        "best_column": False,
        "frontend_api": False
    }
    
    # 1. Test Backend Health
    print("1️⃣ Test Backend Health...")
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code == 200:
            data = health.json()
            print(f"   ✅ Backend: {data['status']}")
            print(f"   📊 Version: {data.get('version', 'unknown')}")
            print(f"   📁 Master BOM: {'✅' if data['master_bom_available'] else '❌'}")
            results["backend_health"] = True
        else:
            print(f"   ❌ Backend Health: {health.status_code}")
    except Exception as e:
        print(f"   ❌ Backend non disponible: {e}")
    
    # 2. Test Frontend Health
    print("\n2️⃣ Test Frontend Health...")
    try:
        frontend = requests.get("http://localhost:5000", timeout=5)
        if frontend.status_code == 200:
            print("   ✅ Frontend accessible")
            results["frontend_health"] = True
        else:
            print(f"   ❌ Frontend: {frontend.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend non disponible: {e}")
    
    # 3. Test API Project Columns
    print("\n3️⃣ Test API Colonnes de Projets...")
    try:
        columns = requests.get("http://localhost:8000/project-columns", timeout=10)
        if columns.status_code == 200:
            data = columns.json()
            if data.get('success'):
                cols = data.get('columns', [])
                project_cols = [col for col in cols if col.get('is_project_column')]
                print(f"   ✅ {len(cols)} colonnes totales détectées")
                print(f"   🎯 {len(project_cols)} colonnes de projets")
                
                # Afficher les top 3
                top_cols = sorted(cols, key=lambda x: x['fill_percentage'], reverse=True)[:3]
                for i, col in enumerate(top_cols, 1):
                    status = "🎯" if col['is_project_column'] else "📊"
                    print(f"   {i}. {status} {col['name']} ({col['fill_percentage']}%)")
                
                results["project_columns"] = True
            else:
                print(f"   ❌ API Error: {data.get('message')}")
        else:
            print(f"   ❌ API Columns: {columns.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur API Columns: {e}")
    
    # 4. Test Suggestion
    print("\n4️⃣ Test Suggestion Intelligente...")
    try:
        suggestion = requests.post(
            "http://localhost:8000/suggest-column",
            json={"input_name": "FORD_J74_V710_B2_PP_YOTK_00000"},
            timeout=10
        )
        if suggestion.status_code == 200:
            data = suggestion.json()
            if data.get('success'):
                confidence = round(data.get('confidence', 0) * 100)
                print(f"   ✅ Suggestion: {data.get('suggested_column')}")
                print(f"   📊 Confiance: {confidence}%")
                results["suggestion"] = True
            else:
                print(f"   ❌ Suggestion Error: {data.get('message')}")
        else:
            print(f"   ❌ Suggestion: {suggestion.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Suggestion: {e}")
    
    # 5. Test Best Column
    print("\n5️⃣ Test Meilleure Colonne...")
    try:
        best = requests.post(
            "http://localhost:8000/find-best-project-column",
            json={"project_hint": "FORD_J74_V710_B2_PP_YOTK"},
            timeout=10
        )
        if best.status_code == 200:
            data = best.json()
            if data.get('success'):
                confidence = round(data.get('confidence', 0) * 100)
                print(f"   ✅ Meilleure colonne: {data.get('best_column')}")
                print(f"   📊 Confiance: {confidence}%")
                print(f"   📈 Analyse: {data.get('analysis', {}).get('total_columns', 0)} colonnes")
                results["best_column"] = True
            else:
                print(f"   ❌ Best Column Error: {data.get('message')}")
        else:
            print(f"   ❌ Best Column: {best.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Best Column: {e}")
    
    # 6. Test Frontend API
    print("\n6️⃣ Test API Frontend...")
    try:
        frontend_api = requests.get("http://localhost:5000/api/project-columns", timeout=10)
        if frontend_api.status_code == 200:
            data = frontend_api.json()
            if data.get('success'):
                cols_count = len(data.get('columns', []))
                print(f"   ✅ Frontend API: {cols_count} colonnes via frontend")
                results["frontend_api"] = True
            else:
                print(f"   ❌ Frontend API Error: {data.get('message')}")
        else:
            print(f"   ❌ Frontend API: {frontend_api.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Frontend API: {e}")
    
    # 7. Test Status Frontend
    print("\n7️⃣ Test Status Frontend...")
    try:
        status = requests.get("http://localhost:5000/api/status", timeout=5)
        if status.status_code == 200:
            data = status.json()
            backend_available = data.get('backend_available', False)
            print(f"   ✅ Status API: Backend {'disponible' if backend_available else 'indisponible'}")
            print(f"   📊 Version frontend: {data.get('frontend_version', 'unknown')}")
        else:
            print(f"   ❌ Status API: {status.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Status API: {e}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS:")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ RÉUSSI" if passed else "❌ ÉCHOUÉ"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 Score: {passed_tests}/{total_tests} tests réussis ({round(passed_tests/total_tests*100)}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("💡 Le système stable est complètement opérationnel")
        print("\n🚀 Services disponibles:")
        print("   🌐 Interface web: http://localhost:5000")
        print("   🧠 Interface avancée: http://localhost:5000/enhanced")
        print("   📡 API Backend: http://localhost:8000")
        print("   📚 Documentation: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) échoué(s)")
        print("💡 Vérifiez que les services sont démarrés:")
        print("   - Backend: python backend_stable.py")
        print("   - Frontend: python frontend_stable.py")
        return 1

def test_interfaces():
    """Test des interfaces web"""
    print("\n🌐 TEST DES INTERFACES WEB")
    print("=" * 40)
    
    interfaces = [
        ("Page d'accueil", "http://localhost:5000"),
        ("Interface classique", "http://localhost:5000/upload"),
        ("Interface avancée", "http://localhost:5000/enhanced")
    ]
    
    for name, url in interfaces:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {name}: {status}")
        except Exception as e:
            print(f"   {name}: ❌ Erreur - {e}")

if __name__ == "__main__":
    print("🚀 COMPONENT DATA PROCESSOR v2.0 - TEST SYSTÈME STABLE")
    print("=" * 70)
    
    # Test principal
    exit_code = test_stable_system()
    
    # Test des interfaces
    test_interfaces()
    
    print("\n" + "=" * 70)
    
    if exit_code == 0:
        print("🎯 SYSTÈME STABLE VALIDÉ - PRÊT POUR LA PRODUCTION !")
    else:
        print("⚠️  SYSTÈME PARTIELLEMENT FONCTIONNEL")
    
    print("=" * 70)
    exit(exit_code)
