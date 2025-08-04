#!/usr/bin/env python3
"""
Script de nettoyage pour le Component Data Processor
Supprime les fichiers temporaires, logs anciens, et cache Python
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

def clean_pycache():
    """Supprime tous les dossiers __pycache__."""
    print("🧹 Nettoyage des fichiers cache Python...")
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"   ✅ Supprimé: {pycache_path}")
            except Exception as e:
                print(f"   ❌ Erreur: {pycache_path} - {e}")

def clean_old_logs():
    """Supprime les logs de plus de 7 jours."""
    print("🧹 Nettoyage des anciens logs...")
    
    cutoff_date = datetime.now() - timedelta(days=7)
    log_pattern = "component_processor_*.log"
    
    for log_file in glob.glob(log_pattern):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                print(f"   ✅ Supprimé: {log_file}")
        except Exception as e:
            print(f"   ❌ Erreur: {log_file} - {e}")

def clean_old_uploads():
    """Supprime les anciens fichiers uploadés (garde les 5 plus récents)."""
    print("🧹 Nettoyage des anciens uploads...")
    
    uploads_dir = Path("frontend/uploads")
    if not uploads_dir.exists():
        return
    
    # Lister tous les fichiers Excel
    excel_files = list(uploads_dir.glob("*.xlsx"))
    
    if len(excel_files) <= 5:
        print("   ℹ️ Moins de 5 fichiers, rien à supprimer")
        return
    
    # Trier par date de modification (plus récent en premier)
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Supprimer les fichiers au-delà des 5 plus récents
    for old_file in excel_files[5:]:
        try:
            old_file.unlink()
            print(f"   ✅ Supprimé: {old_file}")
        except Exception as e:
            print(f"   ❌ Erreur: {old_file} - {e}")

def clean_old_outputs():
    """Supprime les anciens fichiers de sortie (garde les 3 plus récents de chaque type)."""
    print("🧹 Nettoyage des anciens outputs...")
    
    output_dir = Path("output")
    if not output_dir.exists():
        return
    
    # Types de fichiers à nettoyer
    file_patterns = [
        "Update_*.xlsx",
        "Master_BOM_Updated_*.xlsx", 
        "Processing_Summary_*.csv",
        "Clean_Excluded_*.xlsx"
    ]
    
    for pattern in file_patterns:
        files = list(output_dir.glob(pattern))
        
        if len(files) <= 3:
            continue
        
        # Trier par date de modification (plus récent en premier)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Supprimer les fichiers au-delà des 3 plus récents
        for old_file in files[3:]:
            try:
                old_file.unlink()
                print(f"   ✅ Supprimé: {old_file}")
            except Exception as e:
                print(f"   ❌ Erreur: {old_file} - {e}")

def clean_temp_files():
    """Supprime les fichiers temporaires."""
    print("🧹 Nettoyage des fichiers temporaires...")
    
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "~$*.xlsx",  # Fichiers Excel temporaires
        ".~lock.*"   # Fichiers de verrouillage LibreOffice
    ]
    
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern):
            try:
                os.remove(temp_file)
                print(f"   ✅ Supprimé: {temp_file}")
            except Exception as e:
                print(f"   ❌ Erreur: {temp_file} - {e}")

def main():
    """Fonction principale de nettoyage."""
    print("🧹 NETTOYAGE DU COMPONENT DATA PROCESSOR")
    print("=" * 50)
    
    clean_pycache()
    clean_old_logs()
    clean_old_uploads()
    clean_old_outputs()
    clean_temp_files()
    
    print("\n✅ Nettoyage terminé!")
    print("💡 Conseil: Exécutez ce script régulièrement pour maintenir le projet propre")

if __name__ == '__main__':
    main()
