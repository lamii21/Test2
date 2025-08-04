#!/usr/bin/env python3
"""
Script de vérification de sécurité pour Component Data Processor
"""

import os
import stat
from pathlib import Path

def check_file_permissions():
    """Vérifie les permissions des fichiers sensibles."""
    print("🔒 VÉRIFICATION DES PERMISSIONS")
    print("=" * 50)
    
    sensitive_files = [
        'Master_BOM.xlsx',
        'config/default.json',
        '.env'
    ]
    
    issues = []
    
    for file_path in sensitive_files:
        path = Path(file_path)
        if path.exists():
            file_stat = path.stat()
            permissions = stat.filemode(file_stat.st_mode)
            
            # Vérifier si le fichier est lisible par tous
            if file_stat.st_mode & stat.S_IROTH:
                issues.append(f"⚠️  {file_path}: Lisible par tous ({permissions})")
            else:
                print(f"✅ {file_path}: Permissions OK ({permissions})")
        else:
            print(f"ℹ️  {file_path}: Fichier non trouvé")
    
    return issues

def check_environment():
    """Vérifie la configuration d'environnement."""
    print(f"\n🌍 VÉRIFICATION DE L'ENVIRONNEMENT")
    print("=" * 50)
    
    issues = []
    
    # Vérifier la clé secrète
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        issues.append("⚠️  SECRET_KEY non définie")
    elif secret_key == 'component_processor_key':
        issues.append("🚨 SECRET_KEY utilise la valeur par défaut (CRITIQUE)")
    elif len(secret_key) < 32:
        issues.append("⚠️  SECRET_KEY trop courte (< 32 caractères)")
    else:
        print("✅ SECRET_KEY: Configuration OK")
    
    # Vérifier le mode debug
    debug = os.environ.get('DEBUG', 'false').lower()
    if debug == 'true':
        issues.append("🚨 DEBUG activé en production (CRITIQUE)")
    else:
        print("✅ DEBUG: Désactivé")
    
    return issues

def check_directory_security():
    """Vérifie la sécurité des répertoires."""
    print(f"\n📁 VÉRIFICATION DES RÉPERTOIRES")
    print("=" * 50)
    
    issues = []
    directories = ['output', 'frontend/uploads', 'config']
    
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            dir_stat = path.stat()
            permissions = stat.filemode(dir_stat.st_mode)
            
            # Vérifier si le répertoire est accessible en écriture par tous
            if dir_stat.st_mode & stat.S_IWOTH:
                issues.append(f"⚠️  {dir_path}: Écriture autorisée pour tous ({permissions})")
            else:
                print(f"✅ {dir_path}: Permissions OK ({permissions})")
        else:
            print(f"ℹ️  {dir_path}: Répertoire non trouvé")
    
    return issues

def main():
    """Fonction principale de vérification."""
    print("🛡️  AUDIT DE SÉCURITÉ - COMPONENT DATA PROCESSOR")
    print("=" * 60)
    
    all_issues = []
    
    # Vérifications
    all_issues.extend(check_file_permissions())
    all_issues.extend(check_environment())
    all_issues.extend(check_directory_security())
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DE L'AUDIT")
    print("=" * 50)
    
    if all_issues:
        print(f"🚨 {len(all_issues)} problème(s) de sécurité détecté(s):")
        for issue in all_issues:
            print(f"   {issue}")
        
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   • Définissez SECRET_KEY dans .env")
        print(f"   • Vérifiez les permissions des fichiers")
        print(f"   • Désactivez DEBUG en production")
        print(f"   • Limitez l'accès aux répertoires sensibles")
        
        return False
    else:
        print("✅ Aucun problème de sécurité détecté")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
