#!/usr/bin/env python3
"""
Frontend Flask Stable - Version parfaitement stable
Interface web stable avec le backend FastAPI stable
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend_stable")

# Configuration Flask
app = Flask(__name__)
app.secret_key = 'component-data-processor-stable-key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Configuration
BACKEND_URL = "http://localhost:8000"
UPLOAD_FOLDER = Path("frontend_uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

class StableFrontendAPI:
    """Client API stable pour le frontend"""
    
    def __init__(self, backend_url=BACKEND_URL):
        self.backend_url = backend_url.rstrip('/')
        self.timeout = 30
    
    def _request(self, method, endpoint, **kwargs):
        """Effectue une requête avec gestion d'erreurs"""
        try:
            url = f"{self.backend_url}{endpoint}"
            kwargs.setdefault('timeout', self.timeout)
            
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "message": f"Erreur HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Backend non disponible"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def is_available(self):
        """Vérifie si le backend est disponible"""
        health = self._request('GET', '/health')
        return health and health.get('success', False)
    
    def get_project_columns(self):
        """Récupère les colonnes de projets"""
        return self._request('GET', '/project-columns')
    
    def suggest_column(self, input_name):
        """Suggère une colonne"""
        return self._request('POST', '/suggest-column', json={"input_name": input_name})
    
    def find_best_column(self, project_hint=""):
        """Trouve la meilleure colonne"""
        return self._request('POST', '/find-best-project-column', json={"project_hint": project_hint})

# Instance du client API
api = StableFrontendAPI()

@app.route('/')
def index():
    """Page d'accueil"""
    backend_status = api.is_available()
    return render_template('index_stable.html', backend_available=backend_status)

# Route supprimée - Interface unique maintenant

@app.route('/enhanced')
def upload_enhanced():
    """Page de traitement complète"""
    return render_template('upload_complete.html')

@app.route('/api/status')
def api_status():
    """Status de l'API"""
    backend_available = api.is_available()
    return jsonify({
        "success": True,
        "backend_available": backend_available,
        "frontend_version": "2.0.0-stable",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/project-columns')
def api_project_columns():
    """API pour récupérer les colonnes de projets"""
    if not api.is_available():
        return jsonify({
            "success": False,
            "message": "Backend non disponible",
            "columns": []
        })
    
    result = api.get_project_columns()
    return jsonify(result)

@app.route('/api/suggest-column', methods=['POST'])
def api_suggest_column():
    """API pour suggérer une colonne"""
    try:
        data = request.get_json()
        project_hint = data.get('project_hint', '').strip()
        
        if not project_hint:
            return jsonify({
                "success": False,
                "message": "Nom de projet requis"
            })
        
        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible"
            })
        
        result = api.suggest_column(project_hint)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur suggestion: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route('/api/find-best-column', methods=['POST'])
def api_find_best_column():
    """API pour trouver la meilleure colonne"""
    try:
        data = request.get_json()
        project_hint = data.get('project_hint', '').strip()

        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible"
            })

        result = api.find_best_column(project_hint)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Proxy pour l'upload vers le backend"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "Aucun fichier fourni"
            })

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "Aucun fichier sélectionné"
            })

        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible"
            })

        # Transférer le fichier vers le backend
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "success": False,
                "message": f"Erreur backend: {response.status_code}"
            })

    except Exception as e:
        logger.error(f"Erreur upload proxy: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })


@app.route('/api/process', methods=['POST'])
def api_process():
    """Proxy pour le traitement vers le backend"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        filename = data.get('filename')
        project_column = data.get('project_column')

        if not all([file_id, filename, project_column]):
            return jsonify({
                "success": False,
                "message": "Paramètres manquants"
            })

        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible"
            })

        # Appeler le backend pour le traitement
        params = {
            'file_id': file_id,
            'filename': filename,
            'project_column': project_column
        }

        response = requests.post(f"{BACKEND_URL}/process", params=params, timeout=60)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "success": False,
                "message": f"Erreur backend: {response.status_code}"
            })

    except Exception as e:
        logger.error(f"Erreur process proxy: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload et traitement de fichier"""
    try:
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        project_column = request.form.get('project_column', '').strip()
        
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if not project_column:
            flash('Veuillez sélectionner une colonne de projet', 'error')
            return redirect(request.url)
        
        if not api.is_available():
            flash('Backend non disponible', 'error')
            return redirect(request.url)
        
        # Sauvegarder le fichier temporairement
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / safe_filename
        
        file.save(filepath)
        
        try:
            # Upload vers le backend
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                upload_response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)
            
            if upload_response.status_code != 200:
                flash('Erreur lors de l\'upload vers le backend', 'error')
                return redirect(request.url)
            
            upload_data = upload_response.json()
            
            if not upload_data.get('success'):
                flash(f'Erreur upload: {upload_data.get("message")}', 'error')
                return redirect(request.url)
            
            # Traitement
            process_response = requests.post(
                f"{BACKEND_URL}/process",
                params={
                    'file_id': upload_data['file_id'],
                    'filename': upload_data['filename'],
                    'project_column': project_column
                },
                timeout=60
            )
            
            if process_response.status_code == 200:
                process_data = process_response.json()
                if process_data.get('success'):
                    output_files = process_data.get('output_files', [])
                    if output_files:
                        files_info = ', '.join([f['filename'] for f in output_files])
                        flash(f'Traitement réussi avec la colonne {project_column}. Fichiers générés: {files_info}', 'success')

                        # Stocker les informations des fichiers dans la session pour affichage
                        from flask import session
                        session['last_output_files'] = output_files
                    else:
                        flash(f'Traitement réussi avec la colonne {project_column}', 'success')
                else:
                    flash(f'Traitement échoué: {process_data.get("message")}', 'error')
            else:
                flash('Erreur lors du traitement', 'error')
            
        finally:
            # Nettoyer le fichier temporaire
            if filepath.exists():
                filepath.unlink()
        
        return redirect(request.url)
        
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(request.url)

@app.errorhandler(413)
def too_large(e):
    flash('Fichier trop volumineux (max 100MB)', 'error')
    return redirect(request.url)

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Erreur interne: {e}")
    flash('Erreur interne du serveur', 'error')
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """Télécharge un fichier via le backend"""
    try:
        if not api.is_available():
            flash('Backend non disponible', 'error')
            return redirect(url_for('index'))

        # Sécurité: vérifier que le nom de fichier est sûr
        if ".." in filename or "/" in filename or "\\" in filename:
            flash('Nom de fichier invalide', 'error')
            return redirect(url_for('index'))

        # Rediriger directement vers le backend pour le téléchargement
        backend_url = f"{BACKEND_URL}/download/{filename}"
        logger.info(f"Redirection téléchargement: {filename}")

        return redirect(backend_url)

    except Exception as e:
        logger.error(f"Erreur téléchargement: {e}")
        flash('Erreur lors du téléchargement', 'error')
        return redirect(url_for('index'))


@app.route('/api/list-outputs')
def api_list_outputs():
    """API pour lister les fichiers de sortie"""
    try:
        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible",
                "files": []
            })

        response = requests.get(f"{BACKEND_URL}/list-outputs", timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Ajouter les URLs de téléchargement via le frontend
            for file_info in data.get('files', []):
                file_info['frontend_download_url'] = url_for('download_file', filename=file_info['filename'])
            return jsonify(data)
        else:
            return jsonify({
                "success": False,
                "message": f"Erreur backend: {response.status_code}",
                "files": []
            })

    except Exception as e:
        logger.error(f"Erreur liste outputs: {e}")
        return jsonify({
            "success": False,
            "message": str(e),
            "files": []
        })


@app.route('/results')
def results_page():
    """Page des résultats avec téléchargements"""
    return render_template('results.html')


@app.route('/api/preview/<filename>')
def api_preview_file(filename):
    """API pour l'aperçu d'un fichier"""
    try:
        if not api.is_available():
            return jsonify({
                "success": False,
                "message": "Backend non disponible"
            })

        # Appeler le backend pour l'aperçu
        response = requests.get(f"{BACKEND_URL}/preview/{filename}", timeout=10)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "success": False,
                "message": f"Erreur backend: {response.status_code}"
            })

    except Exception as e:
        logger.error(f"Erreur aperçu: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == '__main__':
    print("=" * 60)
    print("FRONTEND FLASK STABLE - Version 2.0.0")
    print("=" * 60)
    print("Fonctionnalités:")
    print("- Interface web stable")
    print("- Communication robuste avec backend")
    print("- Gestion d'erreurs complète")
    print("- Upload sécurisé")
    print("- IA de suggestion de colonnes")
    print("=" * 60)
    print()
    print("Vérification du backend...")
    
    if api.is_available():
        print("[OK] Backend disponible")
        health = api._request('GET', '/health')
        if health and health.get('success'):
            print(f"[OK] Version backend: {health.get('version', 'unknown')}")
    else:
        print("[ATTENTION] Backend non disponible")
        print("Assurez-vous que le backend est démarré sur http://localhost:8000")
    
    print()
    print("Démarrage du frontend sur http://localhost:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Désactiver le debug pour plus de stabilité
        threaded=True
    )
