#!/usr/bin/env python3
"""
Client API Frontend Stable - Version parfaitement stable
Communication robuste avec le backend FastAPI
"""

import requests
import logging
from typing import Dict, Any, Optional
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend_api_client_stable")

class StableAPIClient:
    """Client API stable pour communication avec le backend"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip('/')
        self.timeout = 30  # Timeout plus long pour la stabilité
        self.session = requests.Session()
        
        # Headers par défaut
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Effectue une requête HTTP avec gestion d'erreurs robuste"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            # Configuration par défaut
            kwargs.setdefault('timeout', self.timeout)
            
            logger.info(f"Requete {method} vers {url}")
            
            response = self.session.request(method, url, **kwargs)
            
            # Log de la réponse
            logger.info(f"Reponse {response.status_code} de {url}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur JSON: {e}")
                    return {
                        "success": False,
                        "message": "Reponse JSON invalide"
                    }
            else:
                logger.error(f"Erreur HTTP {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "message": f"Erreur HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Impossible de se connecter a {url}")
            return {
                "success": False,
                "message": "Backend non disponible"
            }
        except requests.exceptions.Timeout:
            logger.error(f"Timeout pour {url}")
            return {
                "success": False,
                "message": "Timeout de la requete"
            }
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}"
            }
    
    def is_backend_available(self) -> bool:
        """Vérifie si le backend est disponible"""
        try:
            response = self._make_request('GET', '/health')
            return response and response.get('success', False)
        except:
            return False
    
    def get_health(self) -> Dict[str, Any]:
        """Récupère l'état de santé du backend"""
        return self._make_request('GET', '/health') or {
            "success": False,
            "message": "Backend non disponible"
        }
    
    def get_project_columns(self) -> Dict[str, Any]:
        """Récupère les colonnes de projets"""
        return self._make_request('GET', '/project-columns') or {
            "success": False,
            "message": "Erreur lors de la recuperation des colonnes",
            "columns": []
        }
    
    def suggest_column(self, input_name: str) -> Dict[str, Any]:
        """Suggère une colonne basée sur un nom d'entrée"""
        data = {"input_name": input_name}
        return self._make_request('POST', '/suggest-column', json=data) or {
            "success": False,
            "message": "Erreur lors de la suggestion"
        }
    
    def find_best_project_column(self, project_hint: str = "") -> Dict[str, Any]:
        """Trouve la meilleure colonne de projet"""
        data = {"project_hint": project_hint}
        return self._make_request('POST', '/find-best-project-column', json=data) or {
            "success": False,
            "message": "Erreur lors de la recherche"
        }
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload un fichier vers le backend"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                # Requête sans les headers JSON pour multipart/form-data
                response = requests.post(
                    f"{self.backend_url}/upload",
                    files=files,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "message": f"Erreur upload: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Erreur upload: {e}")
            return {
                "success": False,
                "message": f"Erreur upload: {str(e)}"
            }
    
    def process_file(self, file_id: str, filename: str, project_column: str, key_column: str = "PN") -> Dict[str, Any]:
        """Traite un fichier uploadé"""
        params = {
            'file_id': file_id,
            'filename': filename,
            'project_column': project_column,
            'key_column': key_column
        }
        
        return self._make_request('POST', '/process', params=params) or {
            "success": False,
            "message": "Erreur lors du traitement"
        }
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Récupère les informations du backend"""
        health = self.get_health()
        if health.get('success'):
            return {
                "available": True,
                "url": self.backend_url,
                "version": health.get('version', 'unknown'),
                "status": health.get('status', 'unknown')
            }
        else:
            return {
                "available": False,
                "url": self.backend_url,
                "error": health.get('message', 'Backend non disponible')
            }

# Instance globale du client API stable
stable_api_client = StableAPIClient()

# Fonction de compatibilité avec l'ancien client
def get_api_client():
    """Retourne le client API stable"""
    return stable_api_client

# Tests de base
if __name__ == "__main__":
    print("=" * 50)
    print("TEST DU CLIENT API STABLE")
    print("=" * 50)
    
    client = StableAPIClient()
    
    # Test de connexion
    print("1. Test de connexion...")
    if client.is_backend_available():
        print("   [OK] Backend disponible")
        
        # Test health
        health = client.get_health()
        print(f"   Version: {health.get('version', 'unknown')}")
        print(f"   Status: {health.get('status', 'unknown')}")
        
        # Test colonnes
        print("\n2. Test colonnes de projets...")
        columns = client.get_project_columns()
        if columns.get('success'):
            print(f"   [OK] {len(columns.get('columns', []))} colonnes trouvees")
        else:
            print(f"   [ERREUR] {columns.get('message')}")
        
        # Test suggestion
        print("\n3. Test suggestion...")
        suggestion = client.suggest_column("FORD_J74_V710_B2_PP_YOTK")
        if suggestion.get('success'):
            print(f"   [OK] Suggestion: {suggestion.get('suggested_column')}")
            print(f"   Confiance: {suggestion.get('confidence', 0):.2f}")
        else:
            print(f"   [ERREUR] {suggestion.get('message')}")
            
    else:
        print("   [ERREUR] Backend non disponible")
        print("   Assurez-vous que le backend est demarré sur http://localhost:8000")
    
    print("\n" + "=" * 50)
