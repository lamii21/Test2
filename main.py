#!/usr/bin/env python3
"""
Point d'entrée principal pour le Component Data Processor.

Ce script fournit une interface en ligne de commande pour traiter
les fichiers de données de composants avec différentes options.
"""

import argparse
import sys
import glob
from pathlib import Path
from typing import List

from src.component_processor.processor import ComponentDataProcessor
from src.utils.logger import get_logger


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description='Component Data Processor - Automatise le traitement des données de composants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s input.xlsx                    # Traiter un fichier
  %(prog)s input.xlsx --config my.json   # Avec configuration personnalisée
  %(prog)s --batch "*.xlsx"              # Traiter tous les fichiers Excel
  %(prog)s --validate input.xlsx         # Valider seulement
  %(prog)s --create-samples              # Créer des fichiers d'exemple
        """
    )
    
    # Arguments principaux
    parser.add_argument(
        'input_files',
        nargs='*',
        help='Fichier(s) d\'entrée à traiter'
    )
    
    # Options de configuration
    parser.add_argument(
        '--config', '-c',
        help='Fichier de configuration personnalisé'
    )
    
    # Options de traitement
    parser.add_argument(
        '--batch', '-b',
        help='Pattern pour traitement en lot (ex: "*.xlsx")'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Répertoire de sortie personnalisé'
    )

    parser.add_argument(
        '--project-column', '-p',
        help='Colonne de projet à utiliser dans le Master BOM (ex: "Project", "Ford_Project")'
    )
    
    # Options de validation
    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='Valider les fichiers sans les traiter'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulation sans écriture de fichiers'
    )
    
    # Options utilitaires
    parser.add_argument(
        '--create-samples',
        action='store_true',
        help='Créer des fichiers d\'exemple'
    )
    
    parser.add_argument(
        '--verbose', '-V',
        action='store_true',
        help='Mode verbeux (niveau DEBUG)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Mode silencieux (erreurs seulement)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Component Data Processor v1.0.0'
    )
    
    return parser.parse_args()


def setup_logging(args):
    """Configure le logging selon les arguments."""
    if args.verbose:
        log_level = 'DEBUG'
    elif args.quiet:
        log_level = 'ERROR'
    else:
        log_level = 'INFO'
    
    return get_logger("Main", log_level)


def get_input_files(args) -> List[str]:
    """Détermine la liste des fichiers à traiter."""
    files = []
    
    # Fichiers spécifiés directement
    if args.input_files:
        files.extend(args.input_files)
    
    # Pattern de lot
    if args.batch:
        batch_files = glob.glob(args.batch)
        files.extend(batch_files)
    
    # Valider que les fichiers existent
    valid_files = []
    for file_path in files:
        if Path(file_path).exists():
            valid_files.append(file_path)
        else:
            print(f"Attention: Fichier introuvable: {file_path}")
    
    return valid_files


def validate_files_only(files: List[str], logger):
    """Valide les fichiers sans les traiter."""
    from src.utils.validators import DataValidator
    
    validator = DataValidator()
    all_valid = True
    
    logger.info(f"Validation de {len(files)} fichier(s)")
    
    for file_path in files:
        logger.info(f"Validation: {file_path}")
        
        # Validation du format
        format_valid, format_error = validator.validate_file_format(file_path)
        if not format_valid:
            logger.error(f"  Format invalide: {format_error}")
            all_valid = False
            continue
        
        # Validation du contenu
        content_valid, content_errors = validator.validate_excel_content(file_path)
        if not content_valid:
            logger.error(f"  Contenu invalide:")
            for error in content_errors:
                logger.error(f"    - {error}")
            all_valid = False
        else:
            logger.info(f"  Fichier valide")
    
    return all_valid


def create_sample_files(logger):
    """Crée des fichiers d'exemple."""
    try:
        logger.info("Création des fichiers d'exemple...")
        
        # Importer et exécuter les scripts de création
        from create_sample_master_bom import create_sample_master_bom
        from create_sample_input import create_sample_input, create_additional_test_files
        
        # Créer Master BOM
        logger.info("Création du Master BOM d'exemple...")
        create_sample_master_bom()
        
        # Créer fichiers d'entrée
        logger.info("Création des fichiers d'entrée d'exemple...")
        create_sample_input()
        create_additional_test_files()
        
        logger.info("Fichiers d'exemple créés avec succès!")
        print("\nFichiers d'exemple créés:")
        print("- Master_BOM.xlsx (Master BOM de référence)")
        print("- Sample_Input_Data.xlsx (données d'entrée d'exemple)")
        print("- Sample_Invalid_Data.xlsx (données invalides pour test)")
        print("- Sample_New_Components.xlsx (nouveaux composants)")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des fichiers d'exemple: {e}")
        return False


def process_files(files: List[str], args, logger):
    """Traite les fichiers avec le processeur."""
    try:
        # Initialiser le processeur
        processor = ComponentDataProcessor(args.config)

        # Configurer la colonne de projet si spécifiée
        if hasattr(args, 'project_column') and args.project_column:
            processor.set_project_column(args.project_column)
        
        if len(files) == 1:
            # Traitement d'un seul fichier
            file_path = files[0]
            logger.info(f"Traitement du fichier: {file_path}")
            
            success = processor.process_file(file_path)
            
            if success:
                print(f"\nTraitement reussi: {file_path}")
                return True
            else:
                print(f"\n✗ Traitement échoué: {file_path}")
                return False
        
        else:
            # Traitement en lot
            logger.info(f"Traitement en lot de {len(files)} fichiers")
            
            results = processor.process_multiple_files(files)
            
            # Afficher les résultats
            successful = sum(1 for success in results.values() if success)
            total = len(files)
            
            print(f"\n=== RÉSULTATS DU TRAITEMENT EN LOT ===")
            print(f"Fichiers traités: {total}")
            print(f"Succès: {successful}")
            print(f"Échecs: {total - successful}")
            
            if successful < total:
                print("\nFichiers échoués:")
                for file_path, success in results.items():
                    if not success:
                        print(f"  ✗ {file_path}")
            
            return successful == total
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        return False


def main():
    """Fonction principale."""
    args = parse_arguments()
    logger = setup_logging(args)
    
    try:
        # Créer des fichiers d'exemple si demandé
        if args.create_samples:
            success = create_sample_files(logger)
            sys.exit(0 if success else 1)
        
        # Obtenir la liste des fichiers à traiter
        files = get_input_files(args)
        
        if not files:
            print("Erreur: Aucun fichier à traiter spécifié.")
            print("Utilisez --help pour voir les options disponibles.")
            sys.exit(1)
        
        # Mode validation seulement
        if args.validate_only:
            success = validate_files_only(files, logger)
            if success:
                print("\nTous les fichiers sont valides")
            else:
                print("\n✗ Certains fichiers sont invalides")
            sys.exit(0 if success else 1)
        
        # Mode dry-run
        if args.dry_run:
            print("Mode simulation activé - aucun fichier ne sera modifié")
            logger.info("Mode dry-run activé")
        
        # Traitement normal
        success = process_files(files, args, logger)
        
        if success:
            print("\nTraitement termine avec succes!")
            sys.exit(0)
        else:
            print("\nTraitement termine avec des erreurs.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nTraitement interrompu par l'utilisateur.")
        logger.info("Traitement interrompu par l'utilisateur")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        print(f"\nErreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
