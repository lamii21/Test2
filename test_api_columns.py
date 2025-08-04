#!/usr/bin/env python3
"""
Test de l'API des colonnes de projets
"""

import pandas as pd
import json
from pathlib import Path

def test_api_columns():
    """Simule l'API des colonnes de projets."""
    try:
        # Lire le Master BOM
        master_bom_path = Path('Master_BOM_Real.xlsx')
        if not master_bom_path.exists():
            print(f"❌ Master BOM non trouvé: {master_bom_path.absolute()}")
            return

        df = pd.read_excel(master_bom_path)
        print(f"✅ Master BOM chargé: {len(df)} lignes, {len(df.columns)} colonnes")

        # Récupérer les colonnes 2 à 23 (index 1 à 22)
        project_columns = []
        start_col = 1  # Colonne 2 (index 1)
        end_col = min(23, len(df.columns))  # Colonne 23 ou dernière colonne disponible
        
        print(f"\n📊 Analyse des colonnes {start_col + 1} à {end_col}:")
        
        for i in range(start_col, end_col):
            col = df.columns[i]
            unique_values = df[col].nunique()
            sample_values = df[col].dropna().head(3).tolist()
            
            # Compter les valeurs non-nulles
            non_null_count = df[col].notna().sum()
            
            # Vérifier si c'est une colonne de statut (contient A, D, X, 0)
            status_values = set(['A', 'D', 'X', '0'])
            col_values = set(df[col].dropna().astype(str).unique())
            is_status_column = bool(status_values.intersection(col_values))
            
            fill_percentage = round((non_null_count / len(df)) * 100, 1)
            
            project_columns.append({
                'name': col,
                'index': int(i + 1),  # Position de la colonne (1-based)
                'unique_values': int(unique_values),
                'sample_values': sample_values,
                'non_null_count': int(non_null_count),
                'total_rows': int(len(df)),
                'is_status_column': is_status_column,
                'fill_percentage': fill_percentage
            })
            
            print(f"  {i+1:2d}. {col}")
            print(f"      📈 Remplissage: {fill_percentage}% ({non_null_count}/{len(df)})")
            print(f"      🔢 Valeurs uniques: {unique_values}")
            print(f"      📋 Statut: {'✅' if is_status_column else '❌'}")
            print(f"      📝 Exemples: {sample_values}")
            print()

        # Créer la réponse API
        result = {
            'success': True,
            'columns': project_columns,
            'message': f'{len(project_columns)} colonnes de projet trouvées (colonnes 2 à {end_col})'
        }
        
        print(f"🎯 Résultat API:")
        print(f"   Succès: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   Colonnes: {len(result['columns'])}")
        
        # Sauvegarder pour test
        with open('api_columns_test.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultat sauvegardé dans api_columns_test.json")
        
        # Afficher les 5 premières colonnes recommandées
        print(f"\n🏆 Top 5 colonnes recommandées:")
        for i, col in enumerate(project_columns[:5], 1):
            status_icon = "✅" if col['is_status_column'] else "❌"
            print(f"   {i}. {col['name']} {status_icon} ({col['fill_percentage']}% rempli)")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    test_api_columns()
