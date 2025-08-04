#!/usr/bin/env python3
"""
Script de debug pour tester le lookup directement
"""

import pandas as pd
from src.data_handlers.lookup_processor import LookupProcessor
from src.utils.logger import Logger

def main():
    # Initialiser le logger
    logger = Logger("debug_lookup")
    
    # Charger les fichiers
    print("=== CHARGEMENT DES FICHIERS ===")
    
    # Fichier d'entrée
    df_input = pd.read_excel('frontend/uploads/20250803_143216_PP_B2_GPDB_BOM.xlsx')
    df_input_renamed = df_input.rename(columns={'YAZAKI PN': 'PN', 'BOM ASL FILTER': 'Project'})
    print(f"Fichier d'entrée: {len(df_input_renamed)} lignes")
    print(f"Colonnes: {df_input_renamed.columns.tolist()}")
    print(f"Premier PN: {df_input_renamed['PN'].iloc[0]}")
    print(f"Premier Project: {repr(df_input_renamed['Project'].iloc[0])}")
    
    # Master BOM
    df_master = pd.read_excel('Master_BOM_Real.xlsx')
    print(f"\nMaster BOM: {len(df_master)} lignes")
    print(f"Colonnes: {df_master.columns.tolist()}")
    print(f"Premier PN: {df_master['PN'].iloc[0]}")
    print(f"Premier Project: {repr(df_master['Project'].iloc[0])}")
    
    # Créer les clés de lookup manuellement
    print("\n=== CRÉATION DES CLÉS DE LOOKUP ===")
    
    # Clés d'entrée
    input_keys = (df_input_renamed['PN'].astype(str) + '|' + 
                  df_input_renamed['Project'].astype(str))
    print(f"Première clé d'entrée: {repr(input_keys.iloc[0])}")
    
    # Clés master
    master_keys = (df_master['PN'].astype(str) + '|' + 
                   df_master['Project'].astype(str))
    print(f"Première clé master: {repr(master_keys.iloc[0])}")
    
    # Vérifier correspondances
    input_keys_set = set(input_keys.tolist())
    master_keys_set = set(master_keys.tolist())
    matches = input_keys_set.intersection(master_keys_set)
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Clés d'entrée uniques: {len(input_keys_set)}")
    print(f"Clés master uniques: {len(master_keys_set)}")
    print(f"Correspondances: {len(matches)}")
    
    if matches:
        print(f"Exemples de correspondances: {list(matches)[:5]}")
        
        # Créer le dictionnaire de lookup
        lookup_dict = pd.Series(df_master['Status'].values, index=master_keys).to_dict()
        
        # Effectuer le mapping
        status_mapping = input_keys.map(lookup_dict)
        
        print(f"\nStatuts mappés:")
        print(status_mapping.value_counts(dropna=False))
        
        # Créer le résultat
        result_df = df_input_renamed.copy()
        result_df['Status'] = status_mapping
        result_df['lookup_key'] = input_keys
        
        # Sauvegarder pour vérification
        result_df.to_excel('debug_output.xlsx', index=False)
        print(f"\nRésultat sauvegardé dans debug_output.xlsx")
        
    else:
        print("Aucune correspondance trouvée!")
        print(f"Exemples de clés d'entrée: {list(input_keys_set)[:3]}")
        print(f"Exemples de clés master: {list(master_keys_set)[:3]}")

if __name__ == "__main__":
    main()
