"""
Client API pour communiquer avec le backend FastAPI
Inspiré du projet ETL-Automated-Tool
"""

import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Client pour communiquer avec le backend FastAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API {method} {endpoint}: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du backend"""
        response = self._make_request('GET', '/health')
        return response.json()
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload un fichier vers le backend
        
        Args:
            file_path: Chemin vers le fichier à uploader
            
        Returns:
            Dict contenant la réponse du serveur
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # Préparer le fichier pour l'upload
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            # Supprimer le header Content-Type pour l'upload de fichier
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def get_project_columns(self) -> Dict[str, Any]:
        """Récupère les colonnes de projets disponibles"""
        response = self._make_request('GET', '/project-columns')
        return response.json()
    
    def preview_data(self, file_id: str, sheet_name: Optional[str] = None, max_rows: int = 10) -> Dict[str, Any]:
        """
        Prévisualise les données d'un fichier
        
        Args:
            file_id: ID du fichier
            sheet_name: Nom du sheet (optionnel)
            max_rows: Nombre maximum de lignes
            
        Returns:
            Dict contenant l'aperçu des données
        """
        data = {
            'file_id': file_id,
            'max_rows': max_rows
        }
        
        if sheet_name:
            data['sheet_name'] = sheet_name
        
        response = self._make_request('POST', '/preview', json=data)
        return response.json()
    
    def validate_file(self, file_id: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Valide un fichier
        
        Args:
            file_id: ID du fichier
            sheet_name: Nom du sheet (optionnel)
            
        Returns:
            Dict contenant les résultats de validation
        """
        data = {
            'file_id': file_id
        }
        
        if sheet_name:
            data['sheet_name'] = sheet_name
        
        response = self._make_request('POST', '/validate', json=data)
        return response.json()
    
    def process_file(self, file_id: str, filename: str, project_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Lance le traitement d'un fichier

        Args:
            file_id: ID du fichier
            filename: Nom du fichier
            project_column: Nom de la colonne de projet (optionnel)

        Returns:
            Dict contenant les résultats du traitement
        """
        params = {
            'file_id': file_id,
            'filename': filename
        }

        if project_column:
            params['project_column'] = project_column

        response = requests.post(
            f"{self.base_url}/process",
            params=params,
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    
    def is_backend_available(self) -> bool:
        """Vérifie si le backend est disponible"""
        try:
            health = self.health_check()
            return health.get('status') == 'healthy'
        except Exception:
            return False


# Instance globale du client API
api_client = APIClient()


def test_api_connection():
    """Test de connexion à l'API"""
    print("🧪 Test de connexion au backend FastAPI...")
    
    try:
        # Test de santé
        health = api_client.health_check()
        print(f"✅ Backend disponible: {health['status']}")
        print(f"📊 Version: {health['version']}")
        print(f"⏱️  Uptime: {health['uptime']:.1f}s")
        print(f"📁 Master BOM: {'✅' if health['master_bom_available'] else '❌'}")
        
        # Test des colonnes de projets
        columns_response = api_client.get_project_columns()
        if columns_response['success']:
            print(f"📋 Colonnes de projets: {len(columns_response['columns'])} trouvées")
            
            # Afficher quelques colonnes V710
            v710_columns = [col for col in columns_response['columns'] if 'V710' in col['name']]
            print(f"🎯 Colonnes V710: {len(v710_columns)} trouvées")
            
            for col in v710_columns[:3]:
                print(f"   - {col['name']} ({col['fill_percentage']}% rempli)")
        
        print("\n🎉 Tous les tests API réussis !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion API: {e}")
        return False


if __name__ == "__main__":
    test_api_connection()
