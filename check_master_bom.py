#!/usr/bin/env python3
"""
Script pour diagnostiquer les problèmes avec le Master BOM
"""

import pandas as pd
import os
from pathlib import Path

def check_master_bom():
    """Vérifie le Master BOM et diagnostique les problèmes."""
    
    print("🔍 DIAGNOSTIC DU MASTER BOM")
    print("=" * 50)
    
    master_bom_path = "Master_BOM.xlsx"
    
    # Vérifier si le fichier existe
    if not os.path.exists(master_bom_path):
        print(f"❌ ERREUR: Fichier {master_bom_path} non trouvé")
        return False
    
    print(f"✅ Fichier {master_bom_path} trouvé")
    
    try:
        # Lire le fichier
        df = pd.read_excel(master_bom_path)
        print(f"✅ Fichier lu avec succès")
        print(f"📊 Nombre de lignes: {len(df)}")
        print(f"📊 Nombre de colonnes: {len(df.columns)}")
        
        # Vérifier les colonnes requises
        required_columns = ['PN', 'Project', 'Status']
        missing_columns = []
        
        print(f"\n📋 Colonnes présentes: {df.columns.tolist()}")
        
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ ERREUR: Colonnes manquantes: {missing_columns}")
            print("💡 Le Master BOM doit contenir au minimum: PN, Project, Status")
            return False
        else:
            print("✅ Toutes les colonnes requises sont présentes")
        
        # Vérifier les données
        print(f"\n📊 Aperçu des données:")
        print(df[['PN', 'Project', 'Status']].head(5))
        
        # Vérifier les valeurs nulles
        null_counts = df[required_columns].isnull().sum()
        print(f"\n📊 Valeurs nulles:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"⚠️  {col}: {count} valeurs nulles")
            else:
                print(f"✅ {col}: Aucune valeur nulle")
        
        # Vérifier les statuts
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts(dropna=False)
            print(f"\n📊 Répartition des statuts:")
            for status, count in status_counts.items():
                print(f"   • Status '{status}': {count} composants")
        
        # Vérifier les doublons de PN
        duplicate_pns = df['PN'].duplicated().sum()
        if duplicate_pns > 0:
            print(f"⚠️  {duplicate_pns} PN dupliqués trouvés")
            print("💡 Le système utilisera le premier trouvé (comportement VLOOKUP)")
        else:
            print("✅ Aucun PN dupliqué")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la lecture: {e}")
        print(f"💡 Vérifiez que le fichier n'est pas ouvert dans Excel")
        print(f"💡 Vérifiez que le fichier est un Excel valide (.xlsx)")
        return False

def test_processing():
    """Teste le traitement avec le Master BOM actuel."""
    
    print(f"\n🧪 TEST DE TRAITEMENT")
    print("=" * 50)
    
    try:
        # Importer le processeur
        from src.component_processor.processor import ComponentDataProcessor
        
        # Créer une instance
        processor = ComponentDataProcessor()
        
        # Tester le chargement du Master BOM
        master_bom = processor.data_loader.load_master_bom("Master_BOM.xlsx")
        print(f"✅ Master BOM chargé avec succès: {len(master_bom)} lignes")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors du test de traitement: {e}")
        print(f"💡 Détails de l'erreur:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_master_bom()
    
    if success:
        test_processing()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 DIAGNOSTIC TERMINÉ: Master BOM OK")
    else:
        print("❌ DIAGNOSTIC TERMINÉ: Problèmes détectés")
        print("\n💡 SOLUTIONS POSSIBLES:")
        print("   1. Vérifiez que le fichier Master_BOM.xlsx existe")
        print("   2. Vérifiez que les colonnes PN, Project, Status sont présentes")
        print("   3. Fermez le fichier s'il est ouvert dans Excel")
        print("   4. Vérifiez que le fichier n'est pas corrompu")
