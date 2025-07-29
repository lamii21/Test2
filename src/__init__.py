"""
Component Data Processor Package

Un package Python pour automatiser le traitement et la mise à jour 
des données de composants basées sur des fichiers Excel.
"""

__version__ = "1.0.0"
__author__ = "Component Data Processor Team"
__email__ = "support@component-processor.com"

from .component_processor import ComponentDataProcessor
from .data_handlers import ExcelHandler, DataCleaner
from .utils import Logger, FileManager

__all__ = [
    'ComponentDataProcessor',
    'ExcelHandler', 
    'DataCleaner',
    'Logger',
    'FileManager'
]
