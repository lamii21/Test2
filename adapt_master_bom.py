#!/usr/bin/env python3
"""
Adapte votre Master BOM réel au format attendu par le système
"""

import pandas as pd
from datetime import datetime

def adapt_master_bom():
    """Adapte votre Master BOM au format requis."""
    
    print("🔧 ADAPTATION DE VOTRE MASTER BOM")
    print("=" * 50)
    
    # Lire votre Master BOM original
    original_df = pd.read_excel('Master_BOM.xlsx')
    print(f"📊 Master BOM original: {len(original_df)} lignes, {len(original_df.columns)} colonnes")
    
    # Identifier les colonnes de projets disponibles
    project_columns = [col for col in original_df.columns if 'V710_B2' in col or 'FORD' in col]
    print(f"📋 Colonnes de projets trouvées: {project_columns}")
    
    # Choisir la colonne de projet principale (celle qui correspond à votre fichier)
    main_project_col = None
    for col in project_columns:
        if 'V710_B2_J74' in col and 'YMOK' in col:  # Correspond à votre projet
            main_project_col = col
            break
    
    if not main_project_col and project_columns:
        main_project_col = project_columns[0]  # Prendre la première disponible
    
    print(f"🎯 Colonne de projet sélectionnée: {main_project_col}")
    
    # Créer le DataFrame adapté
    adapted_data = {
        'PN': original_df['Yazaki PN'],  # Renommer Yazaki PN -> PN
        'Project': 'FORD_J74_V710_B2_PP_YOTK_00000',  # Projet fixe pour correspondre à votre fichier
        'Description': original_df.get('Item Description', ''),
        'Supplier': original_df.get('Supplier Name', ''),
        'Status': 'A',  # Status par défaut (vous pouvez modifier selon YPN Status)
        'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
        'Category': 'Component',
        'Price': 0.0,
        'Lead_Time_Days': 14,
        'Min_Order_Qty': 1
    }
    
    # Adapter le Status selon YPN Status si disponible
    if 'YPN Status' in original_df.columns:
        print("🔍 Adaptation des statuts depuis YPN Status...")
        
        # Mapping des statuts
        status_mapping = {
            'Active': 'A',
            'Deprecated': 'D', 
            'Obsolete': 'X',
            'Duplicate': '0',
            'Under Review': 'D',
            'Pending': 'D'
        }
        
        # Appliquer le mapping
        mapped_status = original_df['YPN Status'].map(status_mapping)
        adapted_data['Status'] = mapped_status.fillna('A')  # Par défaut A si non mappé
        
        # Statistiques des statuts
        status_counts = adapted_data['Status'].value_counts() if hasattr(adapted_data['Status'], 'value_counts') else pd.Series(adapted_data['Status']).value_counts()
        print("📊 Répartition des statuts adaptés:")
        for status, count in status_counts.items():
            print(f"   • Status '{status}': {count} composants")
    
    # Créer le DataFrame adapté
    adapted_df = pd.DataFrame(adapted_data)
    
    # Supprimer les lignes avec PN vide
    adapted_df = adapted_df.dropna(subset=['PN'])
    adapted_df = adapted_df[adapted_df['PN'] != '']
    
    print(f"📊 Master BOM adapté: {len(adapted_df)} lignes")
    
    # Sauvegarder une copie de l'original
    original_df.to_excel('Master_BOM_Original.xlsx', index=False)
    print("💾 Original sauvegardé: Master_BOM_Original.xlsx")
    
    # Sauvegarder le Master BOM adapté
    adapted_df.to_excel('Master_BOM.xlsx', index=False)
    print("✅ Master BOM adapté sauvegardé: Master_BOM.xlsx")
    
    print(f"\n🎯 Résumé de l'adaptation:")
    print(f"   • Yazaki PN → PN")
    print(f"   • YPN Status → Status (avec mapping)")
    print(f"   • Item Description → Description")
    print(f"   • Supplier Name → Supplier")
    print(f"   • Projet fixe: FORD_J74_V710_B2_PP_YOTK_00000")
    
    return adapted_df

def test_adapted_master_bom():
    """Teste le Master BOM adapté."""
    
    print(f"\n🧪 TEST DU MASTER BOM ADAPTÉ")
    print("=" * 50)
    
    try:
        df = pd.read_excel('Master_BOM.xlsx')
        
        required_columns = ['PN', 'Project', 'Status']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            print(f"❌ Colonnes manquantes: {missing}")
            return False
        
        print("✅ Toutes les colonnes requises présentes")
        print(f"📊 {len(df)} composants dans le Master BOM")
        
        # Aperçu
        print(f"\n📋 Aperçu:")
        print(df[['PN', 'Status', 'Description']].head(5))
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    adapted_df = adapt_master_bom()
    
    if test_adapted_master_bom():
        print(f"\n🎉 ADAPTATION RÉUSSIE !")
        print(f"💡 Vous pouvez maintenant traiter vos fichiers avec:")
        print(f"   python runner.py process votre_fichier.xlsx")
    else:
        print(f"\n❌ ADAPTATION ÉCHOUÉE")
        print(f"💡 Vérifiez les erreurs ci-dessus")
