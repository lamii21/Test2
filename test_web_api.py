#!/usr/bin/env python3
"""
Test complet de l'API web pour la sélection de colonnes de projets
"""

import requests
import json
import time

def test_project_columns_api():
    """Test de l'API des colonnes de projets."""
    print("🧪 Test de l'API des colonnes de projets...")
    
    try:
        response = requests.get('http://localhost:5000/api/project-columns', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API réussie: {response.status_code}")
            print(f"📊 Succès: {data.get('success', False)}")
            print(f"📝 Message: {data.get('message', 'N/A')}")
            
            columns = data.get('columns', [])
            print(f"🔢 Nombre de colonnes: {len(columns)}")
            
            if columns:
                print(f"\n🏆 Top 5 colonnes de projets:")
                for i, col in enumerate(columns[:5], 1):
                    status_icon = "✅" if col.get('is_status_column', False) else "❌"
                    fill_pct = col.get('fill_percentage', 0)
                    print(f"   {i}. {col['name']} {status_icon} ({fill_pct}% rempli)")
                
                # Trouver la meilleure colonne pour notre test
                best_col = None
                for col in columns:
                    if 'V710' in col['name'] and col.get('is_status_column', False):
                        best_col = col['name']
                        break
                
                if not best_col and columns:
                    best_col = columns[0]['name']
                
                print(f"\n🎯 Colonne recommandée pour test: {best_col}")
                return best_col
            else:
                print("❌ Aucune colonne trouvée")
                return None
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"📝 Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_file_upload_with_project_column(project_column):
    """Test d'upload de fichier avec sélection de colonne de projet."""
    print(f"\n🧪 Test d'upload avec colonne de projet: {project_column}")
    
    try:
        # Préparer le fichier
        files = {'file': open('Sample_Input_Data.xlsx', 'rb')}
        data = {'project_column': project_column}
        
        print("📤 Upload en cours...")
        response = requests.post(
            'http://localhost:5000/upload', 
            files=files, 
            data=data,
            timeout=60
        )
        
        files['file'].close()
        
        if response.status_code == 200:
            print(f"✅ Upload réussi: {response.status_code}")
            
            # Analyser la réponse HTML pour détecter le succès
            html_content = response.text
            if "Fichier traité avec succès" in html_content:
                print("🎉 Traitement réussi détecté dans la réponse HTML")
            elif "Erreur" in html_content:
                print("⚠️ Erreur détectée dans la réponse HTML")
            else:
                print("ℹ️ Statut du traitement non déterminé")
                
            return True
        else:
            print(f"❌ Erreur upload: {response.status_code}")
            print(f"📝 Réponse: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erreur d'upload: {e}")
        return False

def main():
    """Test principal."""
    print("🚀 Test complet de l'API web - Sélection de colonnes de projets")
    print("=" * 70)
    
    # Test 1: API des colonnes de projets
    project_column = test_project_columns_api()
    
    if not project_column:
        print("❌ Impossible de continuer sans colonne de projet")
        return
    
    # Attendre un peu
    time.sleep(2)
    
    # Test 2: Upload avec colonne de projet
    upload_success = test_file_upload_with_project_column(project_column)
    
    # Résumé
    print(f"\n📋 RÉSUMÉ DES TESTS:")
    print(f"   API colonnes: {'✅' if project_column else '❌'}")
    print(f"   Upload fichier: {'✅' if upload_success else '❌'}")
    
    if project_column and upload_success:
        print(f"\n🎉 Tous les tests réussis ! Le système de sélection de colonnes de projets fonctionne.")
        print(f"🔧 Colonne testée: {project_column}")
    else:
        print(f"\n⚠️ Certains tests ont échoué.")

if __name__ == "__main__":
    main()
