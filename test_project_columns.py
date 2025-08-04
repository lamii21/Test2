#!/usr/bin/env python3
"""
Test des colonnes de projets du Master BOM
"""

import pandas as pd
import json

def test_project_columns():
    """Teste la récupération des colonnes de projets."""
    try:
        # Lire le Master BOM
        df = pd.read_excel('Master_BOM_Real.xlsx')
        print(f"Master BOM chargé: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Récupérer les colonnes 2 à 23 (index 1 à 22)
        project_columns = []
        start_col = 1  # Colonne 2 (index 1)
        end_col = min(23, len(df.columns))  # Colonne 23 ou dernière colonne disponible
        
        print(f"\nAnalyse des colonnes {start_col + 1} à {end_col}:")
        
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
                'index': i + 1,  # Position de la colonne (1-based)
                'unique_values': unique_values,
                'sample_values': sample_values,
                'non_null_count': non_null_count,
                'total_rows': len(df),
                'is_status_column': is_status_column,
                'fill_percentage': fill_percentage
            })
            
            print(f"  {i+1:2d}. {col}")
            print(f"      Valeurs uniques: {unique_values}")
            print(f"      Remplissage: {fill_percentage}%")
            print(f"      Statut: {'Oui' if is_status_column else 'Non'}")
            print(f"      Exemples: {sample_values}")
            print()
        
        # Sauvegarder le résultat
        result = {
            'success': True,
            'columns': project_columns,
            'message': f'{len(project_columns)} colonnes de projet trouvées (colonnes 2 à {end_col})'
        }
        
        with open('project_columns_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Résultat sauvegardé dans project_columns_result.json")
        print(f"Total: {len(project_columns)} colonnes de projets disponibles")
        
        return result
        
    except Exception as e:
        print(f"Erreur: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    test_project_columns()
