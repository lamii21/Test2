#!/usr/bin/env python3
"""
Script pour lister les colonnes de projet disponibles dans le Master BOM
"""

import pandas as pd

def list_project_columns():
    """Liste les colonnes de projet disponibles dans le Master BOM."""
    
    print("🔍 COLONNES DE PROJET DISPONIBLES DANS MASTER BOM")
    print("=" * 60)
    
    try:
        # Lire le Master BOM
        df = pd.read_excel('Master_BOM.xlsx')
        print(f"📊 Master BOM: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Chercher les colonnes qui pourraient être des projets
        project_columns = []
        
        # Critères de recherche pour les colonnes de projet
        project_keywords = [
            'project', 'proj', 'ford', 'v710', 'b2', 'j74', 
            'yotk', 'ymok', 'program', 'programme', 'customer'
        ]
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in project_keywords):
                project_columns.append(col)
        
        print(f"\n📋 Colonnes de projet potentielles trouvées: {len(project_columns)}")
        
        if project_columns:
            for i, col in enumerate(project_columns, 1):
                # Compter les valeurs uniques
                unique_values = df[col].nunique()
                sample_values = df[col].dropna().head(3).tolist()
                
                print(f"\n{i}. {col}")
                print(f"   • Valeurs uniques: {unique_values}")
                print(f"   • Exemples: {sample_values}")
                
                # Vérifier si c'est compatible avec votre fichier
                if 'FORD_J74_V710_B2_PP_YOTK_00000' in df[col].values:
                    print(f"   ✅ Compatible avec votre fichier")
                elif any('V710_B2' in str(val) for val in sample_values):
                    print(f"   ⚠️  Potentiellement compatible")
                else:
                    print(f"   ❌ Pas compatible avec votre fichier")
        
        else:
            print("❌ Aucune colonne de projet trouvée")
            print("\n📋 Toutes les colonnes disponibles:")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i}. {col}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   • Utilisez --project-column avec une des colonnes ci-dessus")
        print(f"   • Exemple: python runner.py process fichier.xlsx --project-column \"nom_colonne\"")
        
        if project_columns:
            best_match = None
            for col in project_columns:
                if 'FORD_J74_V710_B2_PP_YOTK_00000' in df[col].values:
                    best_match = col
                    break
            
            if best_match:
                print(f"   • Recommandé: --project-column \"{best_match}\"")
            else:
                print(f"   • Essayez: --project-column \"{project_columns[0]}\"")
        
        return project_columns
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

if __name__ == '__main__':
    list_project_columns()
