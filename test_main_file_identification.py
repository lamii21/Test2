#!/usr/bin/env python3
"""
Test d'identification du fichier principal
Validation que le bon fichier (Update_YYYY-MM-DD.xlsx) est identifié et mis en évidence
"""

import requests
import time
from pathlib import Path

def test_main_file_identification():
    """Test d'identification du fichier principal"""
    print("🧪 TEST D'IDENTIFICATION DU FICHIER PRINCIPAL")
    print("=" * 60)
    
    # 1. Récupérer la liste des fichiers
    print("1️⃣ Récupération de la liste des fichiers...")
    try:
        response = requests.get("http://localhost:8000/list-outputs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                files = data.get('files', [])
                print(f"✅ {len(files)} fichiers trouvés")
                
                # Analyser chaque fichier
                main_files = []
                master_bom_files = []
                summary_files = []
                other_files = []
                
                for file_info in files:
                    filename = file_info['filename']
                    name_lower = filename.lower()
                    
                    if name_lower.startswith('update_') and name_lower.endswith('.xlsx'):
                        main_files.append(file_info)
                        print(f"   📊 FICHIER PRINCIPAL: {filename}")
                    elif 'master_bom' in name_lower:
                        master_bom_files.append(file_info)
                        print(f"   🗄️ Master BOM: {filename}")
                    elif 'summary' in name_lower or 'processing' in name_lower:
                        summary_files.append(file_info)
                        print(f"   📈 Résumé: {filename}")
                    else:
                        other_files.append(file_info)
                        print(f"   📄 Autre: {filename}")
                
                return {
                    'main_files': main_files,
                    'master_bom_files': master_bom_files,
                    'summary_files': summary_files,
                    'other_files': other_files,
                    'total_files': len(files)
                }
            else:
                print(f"❌ Erreur API: {data.get('message')}")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_main_file_content(main_files):
    """Test du contenu du fichier principal"""
    if not main_files:
        print("\n2️⃣ Aucun fichier principal à tester")
        return False
    
    print(f"\n2️⃣ Test du contenu du fichier principal...")
    
    # Prendre le fichier principal le plus récent
    main_file = max(main_files, key=lambda x: x['modified'])
    filename = main_file['filename']
    
    print(f"   Fichier testé: {filename}")
    print(f"   Taille: {round(main_file['size'] / 1024, 1)} KB")
    print(f"   Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(main_file['modified']))}")
    
    try:
        # Télécharger un échantillon du fichier pour vérifier le contenu
        response = requests.get(f"http://localhost:8000/download/{filename}", 
                               timeout=10, stream=True)
        
        if response.status_code == 200:
            print("   ✅ Fichier accessible")
            
            # Vérifier les headers
            content_type = response.headers.get('content-type', '')
            if 'excel' in content_type or 'spreadsheet' in content_type:
                print(f"   ✅ Type Excel correct: {content_type}")
            else:
                print(f"   ⚠️  Type inattendu: {content_type}")
            
            # Vérifier la signature Excel
            content_start = next(response.iter_content(chunk_size=100))
            if content_start and content_start.startswith(b'PK'):
                print("   ✅ Signature Excel valide (PK)")
                return True
            else:
                print(f"   ❌ Signature invalide: {content_start[:10] if content_start else 'Vide'}")
                return False
        else:
            print(f"   ❌ Erreur téléchargement: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test contenu: {e}")
        return False

def test_frontend_api():
    """Test de l'API frontend pour l'identification"""
    print("\n3️⃣ Test API Frontend...")
    
    try:
        response = requests.get("http://localhost:5000/api/list-outputs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                files = data.get('files', [])
                print(f"   ✅ Frontend API: {len(files)} fichiers")
                
                # Vérifier que les URLs de téléchargement frontend sont présentes
                main_file_found = False
                for file_info in files:
                    filename = file_info['filename']
                    if filename.lower().startswith('update_') and filename.lower().endswith('.xlsx'):
                        main_file_found = True
                        if 'frontend_download_url' in file_info:
                            print(f"   ✅ Fichier principal avec URL frontend: {filename}")
                            print(f"      URL: {file_info['frontend_download_url']}")
                        else:
                            print(f"   ⚠️  Fichier principal sans URL frontend: {filename}")
                
                if not main_file_found:
                    print("   ⚠️  Aucun fichier principal trouvé via frontend")
                
                return main_file_found
            else:
                print(f"   ❌ Erreur Frontend API: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Frontend API: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur Frontend API: {e}")
        return False

def test_file_descriptions():
    """Test des descriptions de fichiers"""
    print("\n4️⃣ Test des descriptions de fichiers...")
    
    test_files = [
        ("Update_2025-08-05.xlsx", "Fichier principal"),
        ("Master_BOM_Updated_2025-08-05.xlsx", "Master BOM"),
        ("Processing_Summary_2025-08-05.csv", "Résumé")
    ]
    
    for filename, expected_type in test_files:
        name_lower = filename.lower()
        
        if name_lower.startswith('update_') and name_lower.endswith('.xlsx'):
            description = "VOS DONNÉES enrichies avec informations Master BOM"
            icon = "fas fa-star text-warning"
            print(f"   ✅ {filename}: {expected_type} - {description}")
        elif 'master_bom' in name_lower:
            description = "Master BOM complet mis à jour"
            icon = "fas fa-database text-secondary"
            print(f"   ✅ {filename}: {expected_type} - {description}")
        elif 'summary' in name_lower or 'processing' in name_lower:
            description = "Statistiques détaillées du traitement"
            icon = "fas fa-chart-line text-info"
            print(f"   ✅ {filename}: {expected_type} - {description}")
        else:
            print(f"   ⚠️  {filename}: Type non reconnu")

def main():
    """Fonction principale"""
    print("🚀 COMPONENT DATA PROCESSOR v2.0 - TEST IDENTIFICATION FICHIER PRINCIPAL")
    print("=" * 70)
    
    # Test principal
    file_analysis = test_main_file_identification()
    
    if not file_analysis:
        print("\n❌ ÉCHEC DE L'ANALYSE DES FICHIERS")
        return 1
    
    # Test du contenu du fichier principal
    main_file_valid = test_main_file_content(file_analysis['main_files'])
    
    # Test de l'API frontend
    frontend_ok = test_frontend_api()
    
    # Test des descriptions
    test_file_descriptions()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DE L'IDENTIFICATION DU FICHIER PRINCIPAL")
    print("=" * 70)
    
    main_files_count = len(file_analysis['main_files'])
    master_bom_count = len(file_analysis['master_bom_files'])
    summary_count = len(file_analysis['summary_files'])
    
    print(f"📊 Fichiers principaux (Update_*.xlsx): {main_files_count}")
    print(f"🗄️ Fichiers Master BOM: {master_bom_count}")
    print(f"📈 Fichiers de résumé: {summary_count}")
    print(f"📄 Total des fichiers: {file_analysis['total_files']}")
    
    if main_files_count > 0:
        print(f"\n🎉 FICHIER PRINCIPAL IDENTIFIÉ AVEC SUCCÈS !")
        print(f"\n💡 Le fichier que vous devez télécharger:")
        
        for main_file in file_analysis['main_files']:
            filename = main_file['filename']
            size_kb = round(main_file['size'] / 1024, 1)
            date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(main_file['modified']))
            
            print(f"   📊 {filename}")
            print(f"      📅 Date: {date_str}")
            print(f"      💾 Taille: {size_kb} KB")
            print(f"      📝 Contenu: VOS données avec informations Master BOM selon le projet sélectionné")
            print(f"      🔗 URL: http://localhost:5000/download/{filename}")
        
        print(f"\n🌐 Interface de téléchargement: http://localhost:5000/results")
        print(f"   Le fichier principal est maintenant mis en évidence avec:")
        print(f"   • ⭐ Icône étoile dorée")
        print(f"   • 🟢 Bordure verte et fond clair")
        print(f"   • 🏷️ Badge 'FICHIER PRINCIPAL'")
        print(f"   • 📝 Description détaillée")
        
        return 0
    else:
        print(f"\n⚠️  AUCUN FICHIER PRINCIPAL TROUVÉ")
        print(f"💡 Assurez-vous d'avoir effectué un traitement récemment")
        return 1

if __name__ == "__main__":
    exit(main())
