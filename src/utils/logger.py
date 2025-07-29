"""
Module de logging pour le Component Data Processor.

Fournit une configuration de logging centralisée et des utilitaires
pour le suivi des opérations de traitement.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Gestionnaire de logging centralisé."""
    
    def __init__(self, name: str = "ComponentProcessor", log_level: str = "INFO"):
        """
        Initialise le logger.
        
        Args:
            name: Nom du logger
            log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configure et retourne le logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Éviter la duplication des handlers
        if logger.handlers:
            return logger
        
        # Format des messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour la console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler pour le fichier
        log_file = self._get_log_filename()
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _get_log_filename(self) -> str:
        """Génère le nom du fichier de log avec timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"component_processor_{timestamp}.log"
    
    def debug(self, message: str):
        """Log un message de debug."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log un message d'information."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log un message d'avertissement."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log un message d'erreur."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log un message critique."""
        self.logger.critical(message)
    
    def log_processing_start(self, file_path: str, total_rows: int):
        """Log le début du traitement d'un fichier."""
        self.info(f"Début du traitement: {file_path} ({total_rows} lignes)")
    
    def log_processing_end(self, success: bool, duration: float):
        """Log la fin du traitement."""
        status = "SUCCÈS" if success else "ÉCHEC"
        self.info(f"Traitement terminé: {status} (durée: {duration:.2f}s)")
    
    def log_data_cleaning(self, original_count: int, cleaned_count: int, excluded_count: int):
        """Log les résultats du nettoyage des données."""
        self.info(f"Nettoyage des données: {original_count} -> {cleaned_count} "
                 f"(exclus: {excluded_count})")
    
    def log_status_update(self, status: str, pn: str, project: str, action: str):
        """Log une mise à jour de statut."""
        self.info(f"Statut {status}: PN={pn}, Projet={project} -> {action}")
    
    def log_summary(self, summary: dict):
        """Log un résumé des opérations."""
        self.info("=== RÉSUMÉ DU TRAITEMENT ===")
        for key, value in summary.items():
            self.info(f"{key.replace('_', ' ').title()}: {value}")
        self.info("=" * 30)


class PerformanceLogger:
    """Logger spécialisé pour mesurer les performances."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Démarre un timer pour une opération."""
        self.start_times[operation] = datetime.now()
        self.logger.debug(f"Début de l'opération: {operation}")
    
    def end_timer(self, operation: str):
        """Termine un timer et log la durée."""
        if operation in self.start_times:
            duration = (datetime.now() - self.start_times[operation]).total_seconds()
            self.logger.debug(f"Fin de l'opération: {operation} (durée: {duration:.2f}s)")
            del self.start_times[operation]
            return duration
        return 0
    
    def log_memory_usage(self):
        """Log l'utilisation mémoire actuelle."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.logger.debug(f"Utilisation mémoire: {memory_mb:.2f} MB")
        except ImportError:
            self.logger.debug("psutil non disponible pour le monitoring mémoire")


def get_logger(name: str = "ComponentProcessor", log_level: str = "INFO") -> Logger:
    """
    Factory function pour créer un logger.
    
    Args:
        name: Nom du logger
        log_level: Niveau de logging
        
    Returns:
        Instance de Logger configurée
    """
    return Logger(name, log_level)
