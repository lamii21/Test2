"""
Processeur principal pour le Component Data Processor.

Orchestre l'ensemble du processus de traitement des données
en utilisant les modules spécialisés.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .config_manager import ConfigManager
from ..data_handlers.excel_handler import ExcelHandler
from ..data_handlers.data_cleaner import DataCleaner
from ..data_handlers.lookup_processor import LookupProcessor
from ..utils.logger import Logger, PerformanceLogger
from ..utils.file_manager import FileManager
from ..utils.validators import DataValidator


class ComponentDataProcessor:
    """Processeur principal pour les données de composants."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialise le processeur.
        
        Args:
            config_file: Chemin vers le fichier de configuration (optionnel)
        """
        # Initialiser la configuration
        self.config_manager = ConfigManager(config_file)
        
        # Initialiser le logger
        logging_config = self.config_manager.get_logging_config()
        self.logger = Logger("ComponentDataProcessor", logging_config.level)
        self.perf_logger = PerformanceLogger(self.logger)
        
        # Initialiser les gestionnaires
        self.file_manager = FileManager(self.config_manager.get('files', 'output_dir'))
        self.excel_handler = ExcelHandler(self.logger)
        
        # Initialiser les processeurs de données
        processing_config = self.config_manager.get('processing')
        validation_config = self.config_manager.get('validation')

        # Créer une configuration combinée pour le validator
        combined_config = {**validation_config, **processing_config}

        self.data_cleaner = DataCleaner(processing_config, self.logger)
        self.lookup_processor = LookupProcessor(self.logger)
        self.validator = DataValidator(combined_config)
        
        # Statistiques globales
        self.global_stats = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'files_processed': 0,
            'total_rows_processed': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        self.logger.info("ComponentDataProcessor initialisé")
        self.logger.info(f"Configuration: {self.config_manager.get_summary()}")
    
    def process_file(self, input_file_path: str) -> bool:
        """
        Traite un fichier d'entrée complet.
        
        Args:
            input_file_path: Chemin du fichier d'entrée
            
        Returns:
            True si le traitement a réussi, False sinon
        """
        try:
            self.global_stats['start_time'] = datetime.now()
            self.logger.log_processing_start(input_file_path, 0)
            self.perf_logger.start_timer('total_processing')
            
            # Étape 1: Validation du fichier d'entrée
            if not self._validate_input_file(input_file_path):
                return False
            
            # Étape 2: Chargement des données
            input_df, master_bom = self._load_data(input_file_path)
            if input_df is None or master_bom is None:
                return False
            
            self.global_stats['total_rows_processed'] = len(input_df)
            
            # Étape 3: Nettoyage des données
            cleaned_df = self._clean_data(input_df)
            
            # Étape 4: Traitement du lookup
            processed_df, updated_master_bom = self._process_lookup(cleaned_df, master_bom)
            
            # Étape 5: Génération des sorties
            success = self._generate_outputs(processed_df, updated_master_bom)
            
            # Finalisation
            self._finalize_processing(success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {e}")
            self.global_stats['error_count'] += 1
            return False
    
    def _validate_input_file(self, file_path: str) -> bool:
        """Valide le fichier d'entrée."""
        self.perf_logger.start_timer('file_validation')
        
        # Validation du format
        format_valid, format_error = self.validator.validate_file_format(file_path)
        if not format_valid:
            self.logger.error(f"Validation du format échouée: {format_error}")
            return False
        
        # Validation du contenu (informative, non bloquante)
        content_valid, content_errors = self.validator.validate_excel_content(file_path)
        if not content_valid:
            self.logger.warning(f"Problèmes détectés dans le fichier: {'; '.join(content_errors)}")
            self.logger.info("Le traitement continuera malgré ces problèmes")
        
        self.perf_logger.end_timer('file_validation')
        self.logger.info("Validation du fichier d'entrée réussie")
        return True
    
    def _load_data(self, input_file_path: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Charge les données d'entrée et le Master BOM."""
        self.perf_logger.start_timer('data_loading')
        
        try:
            # Charger le fichier d'entrée
            self.logger.info(f"Chargement du fichier d'entrée: {input_file_path}")
            input_df = self.excel_handler.read_excel_file(input_file_path)

            # Appliquer le mapping intelligent des colonnes
            from src.utils.column_mapper import ColumnMapper
            mapper = ColumnMapper()

            # Obtenir les colonnes disponibles
            available_columns = input_df.columns.tolist()
            self.logger.info(f"Colonnes disponibles: {available_columns}")

            # Valider et mapper les colonnes
            is_valid, missing_columns = mapper.validate_required_columns(available_columns)

            if not is_valid:
                # Afficher les informations de mapping pour le debug
                mapping_info = mapper.get_mapping_info(available_columns)
                self.logger.error(f"Colonnes manquantes: {missing_columns}")
                self.logger.error(f"Colonnes disponibles: {available_columns}")
                if mapping_info['mapped_columns']:
                    self.logger.info(f"Colonnes détectées: {mapping_info['mapped_columns']}")

                raise ValueError(f"Colonnes obligatoires manquantes: {missing_columns}")

            # Appliquer le mapping des colonnes
            column_mapping = mapper.get_required_columns_mapping(available_columns)
            self.logger.info(f"Mapping des colonnes obligatoires: {column_mapping}")

            # Renommer les colonnes selon le mapping
            rename_dict = {v: k for k, v in column_mapping.items() if v is not None}
            if rename_dict:
                input_df = input_df.rename(columns=rename_dict)
                self.logger.info(f"Colonnes renommées: {rename_dict}")

            # Mapper aussi les colonnes optionnelles
            all_mapping = mapper.map_columns(available_columns)
            optional_rename = {}
            for standard_col, actual_col in all_mapping.items():
                if actual_col and standard_col not in ['PN', 'Project'] and actual_col not in rename_dict:
                    optional_rename[actual_col] = standard_col

            if optional_rename:
                input_df = input_df.rename(columns=optional_rename)
                self.logger.info(f"Colonnes optionnelles renommées: {optional_rename}")

            self.logger.info(f"Colonnes finales après mapping: {input_df.columns.tolist()}")
            
            # Charger le Master BOM
            master_bom_path = self.config_manager.get('files', 'master_bom_path')
            self.logger.info(f"Chargement du Master BOM: {master_bom_path}")
            master_bom = self.excel_handler.read_excel_file(master_bom_path)
            
            # Valider le Master BOM
            bom_valid, bom_errors = self.lookup_processor.validate_master_bom(master_bom)
            if not bom_valid:
                self.logger.error(f"Master BOM invalide: {'; '.join(bom_errors)}")
                return None, None
            
            self.perf_logger.end_timer('data_loading')
            return input_df, master_bom
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {e}")
            return None, None
    
    def _clean_data(self, input_df):
        """Nettoie les données d'entrée."""
        self.perf_logger.start_timer('data_cleaning')
        
        self.logger.info("Début du nettoyage des données")
        cleaned_df = self.data_cleaner.clean_dataframe(input_df)
        
        # Log des statistiques de nettoyage
        cleaning_stats = self.data_cleaner.get_cleaning_statistics()
        self.logger.log_data_cleaning(
            cleaning_stats['original_rows'],
            cleaning_stats['cleaned_rows'],
            cleaning_stats['excluded_rows']
        )
        
        self.perf_logger.end_timer('data_cleaning')
        return cleaned_df
    
    def _process_lookup(self, cleaned_df, master_bom):
        """Traite le lookup et applique la logique métier."""
        self.perf_logger.start_timer('lookup_processing')
        
        # Effectuer le lookup
        self.logger.info("Début du processus de lookup")
        lookup_df = self.lookup_processor.perform_lookup(cleaned_df, master_bom)
        
        # Traiter les résultats selon la logique métier
        self.logger.info("Application de la logique métier")
        processed_df, updated_master_bom = self.lookup_processor.process_lookup_results(
            lookup_df, master_bom
        )
        
        self.perf_logger.end_timer('lookup_processing')
        return processed_df, updated_master_bom
    
    def _generate_outputs(self, processed_df, updated_master_bom) -> bool:
        """Génère tous les fichiers de sortie."""
        self.perf_logger.start_timer('output_generation')
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            
            # Fichier principal de sortie
            main_output_file = self.file_manager.get_output_path(f"Update_{timestamp}.xlsx")
            success = self.excel_handler.write_formatted_excel(
                processed_df, str(main_output_file)
            )
            
            if not success:
                return False
            
            # Master BOM mis à jour
            if self.config_manager.get('files', 'backup_enabled', True):
                master_bom_output = self.file_manager.get_output_path(
                    f"Master_BOM_Updated_{timestamp}.xlsx"
                )
                self.excel_handler.write_excel_file(
                    updated_master_bom, str(master_bom_output)
                )
            
            # Lignes exclues
            excluded_df = self.data_cleaner.get_excluded_rows_dataframe()
            if not excluded_df.empty:
                excluded_file = self.file_manager.get_output_path(
                    f"Clean_Excluded_{timestamp}.xlsx"
                )
                self.excel_handler.write_excel_file(excluded_df, str(excluded_file))
            
            # Rapport de résumé
            self._generate_summary_report(timestamp)
            
            self.perf_logger.end_timer('output_generation')
            self.logger.info("Génération des sorties terminée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des sorties: {e}")
            return False
    
    def _generate_summary_report(self, timestamp: str):
        """Génère un rapport de résumé."""
        try:
            # Collecter toutes les statistiques
            summary_data = {
                'timestamp': timestamp,
                'processing_duration': self.global_stats.get('total_duration', 0),
                **self.data_cleaner.get_cleaning_statistics(),
                **self.lookup_processor.get_processing_statistics()
            }
            
            # Sauvegarder en CSV
            import pandas as pd
            summary_df = pd.DataFrame([summary_data])
            summary_file = self.file_manager.get_output_path(
                f"Processing_Summary_{timestamp}.csv"
            )
            summary_df.to_csv(summary_file, index=False)
            
            self.logger.info(f"Rapport de résumé généré: {summary_file}")
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la génération du rapport: {e}")
    
    def _finalize_processing(self, success: bool):
        """Finalise le traitement et log les résultats."""
        self.global_stats['end_time'] = datetime.now()
        self.global_stats['total_duration'] = self.perf_logger.end_timer('total_processing')
        self.global_stats['files_processed'] += 1
        
        if success:
            self.global_stats['success_count'] += 1
            print("Update completed successfully")
            self.logger.info("Traitement terminé avec succès")
        else:
            self.global_stats['error_count'] += 1
            print("Processing failed")
            self.logger.error("Traitement échoué")
        
        # Afficher le résumé
        self._print_final_summary()
        
        # Log des performances
        self.logger.log_processing_end(success, self.global_stats['total_duration'])
    
    def _print_final_summary(self):
        """Affiche un résumé final du traitement."""
        print("\n" + "="*60)
        print("RÉSUMÉ FINAL DU TRAITEMENT")
        print("="*60)
        
        # Statistiques de nettoyage
        cleaning_stats = self.data_cleaner.get_cleaning_statistics()
        print(f"Lignes originales: {cleaning_stats.get('original_rows', 0)}")
        print(f"Lignes nettoyées: {cleaning_stats.get('cleaned_rows', 0)}")
        print(f"Lignes exclues: {cleaning_stats.get('excluded_rows', 0)}")
        
        # Statistiques de traitement
        processing_stats = self.lookup_processor.get_processing_statistics()
        print(f"Mises a jour D->X: {processing_stats.get('status_d_updates', 0)}")
        print(f"Doublons ajoutés: {processing_stats.get('status_0_duplicates', 0)}")
        print(f"Inconnus ajoutés: {processing_stats.get('status_nan_unknowns', 0)}")
        print(f"Ignorés (status X): {processing_stats.get('status_x_skipped', 0)}")
        
        # Performances
        print(f"Durée totale: {self.global_stats['total_duration']:.2f}s")
        print("="*60)
    
    def process_multiple_files(self, file_paths: list) -> Dict[str, bool]:
        """
        Traite plusieurs fichiers en lot.
        
        Args:
            file_paths: Liste des chemins de fichiers
            
        Returns:
            Dictionnaire {fichier: succès}
        """
        results = {}
        
        self.logger.info(f"Traitement en lot de {len(file_paths)} fichiers")
        
        for file_path in file_paths:
            self.logger.info(f"Traitement du fichier: {file_path}")
            success = self.process_file(file_path)
            results[file_path] = success
            
            if not success:
                self.logger.error(f"Échec du traitement: {file_path}")
        
        # Résumé du lot
        successful = sum(1 for success in results.values() if success)
        total = len(file_paths)
        
        self.logger.info(f"Traitement en lot terminé: {successful}/{total} réussis")
        
        return results
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales."""
        return self.global_stats.copy()
