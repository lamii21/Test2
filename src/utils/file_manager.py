"""
Gestionnaire de fichiers pour le Component Data Processor.

Fournit des utilitaires pour la gestion des fichiers, la création de répertoires,
et la génération de noms de fichiers avec timestamps.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union


class FileManager:
    """Gestionnaire centralisé pour les opérations sur les fichiers."""
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialise le gestionnaire de fichiers.
        
        Args:
            base_output_dir: Répertoire de base pour les sorties
        """
        self.base_output_dir = Path(base_output_dir)
        self.ensure_directory_exists(self.base_output_dir)
    
    def ensure_directory_exists(self, directory: Union[str, Path]) -> Path:
        """
        S'assure qu'un répertoire existe, le crée si nécessaire.
        
        Args:
            directory: Chemin du répertoire
            
        Returns:
            Path object du répertoire
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def generate_timestamped_filename(self, base_name: str, extension: str = ".xlsx") -> str:
        """
        Génère un nom de fichier avec timestamp.
        
        Args:
            base_name: Nom de base du fichier
            extension: Extension du fichier
            
        Returns:
            Nom de fichier avec timestamp
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"{base_name}_{timestamp}{extension}"
    
    def generate_detailed_timestamped_filename(self, base_name: str, extension: str = ".xlsx") -> str:
        """
        Génère un nom de fichier avec timestamp détaillé (incluant l'heure).
        
        Args:
            base_name: Nom de base du fichier
            extension: Extension du fichier
            
        Returns:
            Nom de fichier avec timestamp détaillé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}{extension}"
    
    def get_output_path(self, filename: str) -> Path:
        """
        Retourne le chemin complet pour un fichier de sortie.
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Chemin complet du fichier
        """
        return self.base_output_dir / filename
    
    def backup_file(self, file_path: Union[str, Path], backup_suffix: str = "_backup") -> Optional[Path]:
        """
        Crée une sauvegarde d'un fichier.
        
        Args:
            file_path: Chemin du fichier à sauvegarder
            backup_suffix: Suffixe pour le fichier de sauvegarde
            
        Returns:
            Chemin du fichier de sauvegarde ou None si échec
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            backup_name = f"{source_path.stem}{backup_suffix}{source_path.suffix}"
            backup_path = source_path.parent / backup_name
            
            shutil.copy2(source_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def clean_old_files(self, directory: Union[str, Path], pattern: str = "*", days_old: int = 30) -> int:
        """
        Nettoie les anciens fichiers d'un répertoire.
        
        Args:
            directory: Répertoire à nettoyer
            pattern: Pattern des fichiers à considérer
            days_old: Âge minimum en jours pour supprimer
            
        Returns:
            Nombre de fichiers supprimés
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            deleted_count = 0
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            return deleted_count
        except Exception:
            return 0
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """
        Retourne la taille d'un fichier en octets.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Taille en octets
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Formate une taille de fichier en unités lisibles.
        
        Args:
            size_bytes: Taille en octets
            
        Returns:
            Taille formatée (ex: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def list_files_by_pattern(self, directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """
        Liste les fichiers correspondant à un pattern.
        
        Args:
            directory: Répertoire à scanner
            pattern: Pattern de recherche
            
        Returns:
            Liste des fichiers trouvés
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return []
            
            return list(dir_path.glob(pattern))
        except Exception:
            return []
    
    def create_archive(self, source_dir: Union[str, Path], archive_name: str) -> Optional[Path]:
        """
        Crée une archive ZIP d'un répertoire.
        
        Args:
            source_dir: Répertoire source
            archive_name: Nom de l'archive (sans extension)
            
        Returns:
            Chemin de l'archive créée ou None si échec
        """
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                return None
            
            archive_path = self.get_output_path(f"{archive_name}.zip")
            shutil.make_archive(str(archive_path.with_suffix('')), 'zip', source_path)
            
            return archive_path
        except Exception:
            return None
    
    def validate_file_access(self, file_path: Union[str, Path], mode: str = 'r') -> bool:
        """
        Valide qu'un fichier est accessible en lecture/écriture.
        
        Args:
            file_path: Chemin du fichier
            mode: Mode d'accès ('r' pour lecture, 'w' pour écriture)
            
        Returns:
            True si accessible, False sinon
        """
        try:
            path = Path(file_path)
            
            if mode == 'r':
                return path.exists() and path.is_file() and os.access(path, os.R_OK)
            elif mode == 'w':
                if path.exists():
                    return os.access(path, os.W_OK)
                else:
                    # Vérifier si on peut écrire dans le répertoire parent
                    return os.access(path.parent, os.W_OK)
            
            return False
        except Exception:
            return False
