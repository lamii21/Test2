#!/usr/bin/env python3
"""
Interface Web simple et fonctionnelle pour le Component Data Processor
"""

import os
import subprocess
import tempfile
import re
import sys
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for

# Configuration Flask
app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Configuration
UPLOAD_FOLDER = Path('frontend/uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_project_column(column_name: str) -> bool:
    """Valide le nom de colonne de projet pour éviter l'injection."""
    if not column_name:
        return True
    # Autoriser lettres, chiffres, underscore, espaces, tirets, plus
    pattern = r'^[a-zA-Z0-9_\s\-\+]+$'
    return bool(re.match(pattern, column_name)) and len(column_name) <= 100

def validate_filename_safe(filename: str) -> bool:
    """Valide le nom de fichier pour éviter path traversal."""
    if not filename:
        return False
    # Interdire les caractères dangereux
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    return not any(char in filename for char in dangerous_chars)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/enhanced')
def upload_enhanced():
    """Page d'upload avec logique ETL-Automated-Tool avancée"""
    return render_template('upload_enhanced.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Validation supplémentaire de la taille
            if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
                flash('Fichier trop volumineux (max 100MB)', 'error')
                return redirect(request.url)

            filename = secure_filename(file.filename)
            if not filename:
                flash('Nom de fichier invalide', 'error')
                return redirect(request.url)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = UPLOAD_FOLDER / filename

            # Validation du chemin de destination
            try:
                filepath = filepath.resolve()
                upload_folder_resolved = UPLOAD_FOLDER.resolve()
                if not str(filepath).startswith(str(upload_folder_resolved)):
                    flash('Chemin de fichier invalide', 'error')
                    return redirect(request.url)
            except Exception:
                flash('Erreur de validation du fichier', 'error')
                return redirect(request.url)

            file.save(filepath)
            
            try:
                # Utiliser le backend FastAPI pour le traitement
                from frontend_api_client_stable import stable_api_client as api_client

                # Vérifier si le backend est disponible
                if not api_client.is_backend_available():
                    flash('Backend FastAPI non disponible', 'error')
                    return redirect(request.url)

                # Upload du fichier vers le backend
                upload_response = api_client.upload_file(str(filepath))

                if not upload_response.get('success'):
                    flash(f'Erreur upload: {upload_response.get("message", "Erreur inconnue")}', 'error')
                    return redirect(request.url)

                # Traitement via le backend
                project_column = request.form.get('project_column')
                if project_column and project_column.strip():
                    project_column_clean = project_column.strip()
                    if not validate_project_column(project_column_clean):
                        flash('Nom de colonne de projet invalide', 'error')
                        return redirect(request.url)
                else:
                    project_column_clean = None

                # Appeler l'API de traitement
                import requests
                process_response = requests.post(
                    f"{api_client.base_url}/process",
                    params={
                        'file_id': upload_response['file_id'],
                        'filename': upload_response['filename'],
                        'project_column': project_column_clean
                    },
                    timeout=300
                )

                if process_response.status_code != 200:
                    flash('Erreur lors du traitement', 'error')
                    return redirect(request.url)

                result_data = process_response.json()

                # Simuler l'objet result pour compatibilité
                class MockResult:
                    def __init__(self, data):
                        self.returncode = 0 if data.get('success') else 1
                        self.stdout = data.get('stdout', '')
                        self.stderr = data.get('stderr', '')

                result = MockResult(result_data)
                
                print(f"Code de retour: {result.returncode}")
                print(f"Sortie stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Erreurs stderr: {result.stderr}")

                # Analyser la sortie pour déterminer le succès
                success_indicators = [
                    "Traitement termine avec succes",
                    "Traitement terminé avec succès",
                    "Traitement réussi",
                    "Update completed successfully",
                    "SUCCÈS"
                ]

                is_success = (result.returncode == 0 and
                             any(indicator in result.stdout for indicator in success_indicators))

                if is_success:
                    # Extraire les statistiques
                    stats = {}
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Lignes originales:" in line:
                            stats['original_rows'] = line.split(':')[1].strip()
                        elif "Lignes nettoyées:" in line:
                            stats['cleaned_rows'] = line.split(':')[1].strip()
                        elif "Durée totale:" in line:
                            stats['duration'] = line.split(':')[1].strip()
                        elif "Inconnus ajoutés:" in line:
                            stats['new_components'] = line.split(':')[1].strip()

                    flash('Fichier traité avec succès !', 'success')
                    return render_template('results.html',
                                         filename=filename,
                                         success=True,
                                         output=result.stdout,
                                         stats=stats)
                else:
                    error_msg = result.stderr or "Erreur inconnue"
                    flash(f'Erreur lors du traitement: {error_msg}', 'error')
                    return render_template('results.html',
                                         filename=filename,
                                         success=False,
                                         error=error_msg,
                                         output=result.stdout)
            except Exception as e:
                flash(f'Erreur: {str(e)}', 'error')
                return render_template('results.html', 
                                     filename=filename, 
                                     success=False)
        else:
            flash('Type de fichier non autorisé', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/validate', methods=['POST'])
def validate_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Fichier invalide'}), 400
        
        import pandas as pd
        import sys
        from pathlib import Path

        # Ajouter le chemin pour importer le mapper
        sys.path.append(str(Path(__file__).parent))
        from src.utils.column_mapper import ColumnMapper

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)

            try:
                df = pd.read_excel(tmp_file.name)
                content_errors = []

                if df.empty:
                    content_errors.append('Le fichier est vide')

                # Utiliser le mapper pour trouver les colonnes
                mapper = ColumnMapper()
                available_columns = df.columns.tolist()

                # Valider les colonnes obligatoires
                is_valid, missing_columns = mapper.validate_required_columns(available_columns)

                if missing_columns:
                    # Afficher les colonnes disponibles pour aider l'utilisateur
                    content_errors.append(f'Colonnes obligatoires non trouvées: {", ".join(missing_columns)}')
                    content_errors.append(f'Colonnes disponibles dans votre fichier: {", ".join(available_columns)}')

                    # Suggestions de mapping
                    mapping_info = mapper.get_mapping_info(available_columns)
                    if mapping_info['mapped_columns']:
                        mapped_list = [f"{k} → {v}" for k, v in mapping_info['mapped_columns'].items()]
                        content_errors.append(f'Colonnes détectées: {", ".join(mapped_list)}')

                # Vérifier les valeurs manquantes pour les colonnes trouvées
                column_mapping = mapper.get_required_columns_mapping(available_columns)
                for standard_col, actual_col in column_mapping.items():
                    if actual_col:
                        missing_count = df[actual_col].isna().sum()
                        if missing_count > 0:
                            content_errors.append(f'Colonne "{actual_col}" ({standard_col}): {missing_count} valeurs manquantes')
                
                return jsonify({
                    'format_valid': True,
                    'format_error': '',
                    'content_valid': len(content_errors) == 0,
                    'content_errors': content_errors,
                    'overall_valid': len(content_errors) == 0
                })
            
            except Exception as e:
                return jsonify({'error': f'Erreur: {str(e)}'}), 500
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
    
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@app.route('/samples', methods=['GET', 'POST'])
def create_samples():
    if request.method == 'POST':
        try:
            print("🔄 Début de création des exemples via interface web...")

            result = subprocess.run(
                [sys.executable, 'runner.py', 'samples'],
                capture_output=True,
                text=True,
                timeout=120,  # Augmenter le timeout
                cwd=Path.cwd()  # S'assurer du bon répertoire
            )

            print(f"📊 Code de retour: {result.returncode}")
            print(f"📝 Sortie: {result.stdout}")
            if result.stderr:
                print(f"❌ Erreurs: {result.stderr}")

            if result.returncode == 0:
                # Vérifier que les fichiers ont bien été créés
                expected_files = ['Master_BOM.xlsx', 'Sample_Input_Data.xlsx']
                created_files = []
                missing_files = []

                for file_name in expected_files:
                    if Path(file_name).exists():
                        created_files.append(file_name)
                    else:
                        missing_files.append(file_name)

                if created_files:
                    flash(f'Fichiers créés avec succès: {", ".join(created_files)}', 'success')
                    return render_template('samples.html',
                                         success=True,
                                         created_files=created_files,
                                         output=result.stdout)
                else:
                    flash('Aucun fichier créé', 'error')
                    return render_template('samples.html',
                                         success=False,
                                         error="Aucun fichier généré")
            else:
                error_msg = result.stderr or "Erreur inconnue"
                flash(f'Erreur lors de la création: {error_msg}', 'error')
                return render_template('samples.html',
                                     success=False,
                                     error=error_msg,
                                     output=result.stdout)

        except subprocess.TimeoutExpired:
            flash('Timeout: La création a pris trop de temps', 'error')
            return render_template('samples.html', success=False, error="Timeout")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            flash(f'Erreur: {str(e)}', 'error')
            return render_template('samples.html', success=False, error=str(e))

    # GET request - afficher la page
    return render_template('samples.html', success=None)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # Validation de sécurité
        if not validate_filename_safe(filename):
            flash('Nom de fichier invalide', 'error')
            return redirect(url_for('index'))

        # Sécuriser le nom de fichier
        safe_filename = secure_filename(filename)
        if not safe_filename:
            flash('Nom de fichier invalide', 'error')
            return redirect(url_for('index'))

        # Chercher d'abord dans le dossier output
        output_dir = Path('output')
        file_path = output_dir / safe_filename

        # Vérifier que le chemin résolu est bien dans output
        try:
            file_path = file_path.resolve()
            output_dir = output_dir.resolve()
            if not str(file_path).startswith(str(output_dir)):
                flash('Accès non autorisé', 'error')
                return redirect(url_for('index'))
        except Exception:
            flash('Chemin de fichier invalide', 'error')
            return redirect(url_for('index'))

        if file_path.exists() and file_path.is_file():
            return send_file(file_path, as_attachment=True)

        # Si pas trouvé, chercher dans une liste blanche de fichiers autorisés
        allowed_root_files = ['Master_BOM.xlsx', 'Sample_Input_Data.xlsx']
        if safe_filename in allowed_root_files:
            root_file_path = Path(safe_filename)
            if root_file_path.exists() and root_file_path.is_file():
                return send_file(root_file_path, as_attachment=True)

        # Fichier non trouvé
        flash(f'Fichier non trouvé: {safe_filename}', 'error')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    try:
        try:
            import pandas, numpy, openpyxl
            dependencies_ok = True
        except ImportError:
            dependencies_ok = False
        
        output_dir = Path('output')
        output_files = list(output_dir.glob('*')) if output_dir.exists() else []
        
        return jsonify({
            'dependencies_ok': dependencies_ok,
            'output_files_count': len(output_files),
            'master_bom_exists': Path('Master_BOM.xlsx').exists(),
            'config_exists': Path('config/default.json').exists(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def api_files():
    try:
        output_dir = Path('output')
        if not output_dir.exists():
            return jsonify({'files': []})

        files = []
        for file_path in output_dir.glob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'download_url': url_for('download_file', filename=file_path.name)
                })

        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project-columns')
def api_project_columns():
    """Récupère les colonnes de projet disponibles via le backend FastAPI."""
    try:
        # Importer le client API
        from frontend_api_client_stable import stable_api_client as api_client

        # Vérifier si le backend est disponible
        if not api_client.is_backend_available():
            return jsonify({
                'success': False,
                'message': 'Backend FastAPI non disponible',
                'columns': []
            })

        # Récupérer les colonnes via l'API
        response = api_client.get_project_columns()
        return jsonify(response)

    except Exception as e:
        print(f"Erreur lors de la récupération des colonnes: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur de communication avec le backend: {str(e)}',
            'columns': []
        })


@app.route('/api/suggest-column', methods=['POST'])
def api_suggest_column():
    """API pour suggérer une colonne de projet avec logique ETL-Automated-Tool"""
    try:
        data = request.get_json()
        project_hint = data.get('project_hint', '')

        from frontend_api_client_stable import stable_api_client as api_client

        if not api_client.is_backend_available():
            return jsonify({
                'success': False,
                'message': 'Backend FastAPI non disponible'
            })

        # Appeler l'endpoint de suggestion du backend
        import requests
        response = requests.post(
            f"{api_client.backend_url}/suggest-column",
            json={"input_name": project_hint},
            timeout=10
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la suggestion'
            })

    except Exception as e:
        print(f"Erreur API suggestion colonne: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/api/find-best-column', methods=['POST'])
def api_find_best_column():
    """API pour trouver la meilleure colonne de projet"""
    try:
        data = request.get_json()
        project_hint = data.get('project_hint', '')

        from frontend_api_client_stable import stable_api_client as api_client

        if not api_client.is_backend_available():
            return jsonify({
                'success': False,
                'message': 'Backend FastAPI non disponible'
            })

        # Appeler l'endpoint du backend
        import requests
        response = requests.post(
            f"{api_client.backend_url}/find-best-project-column",
            json={"project_hint": project_hint},
            timeout=10
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la recherche'
            })

    except Exception as e:
        print(f"Erreur API meilleure colonne: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/health')
def health_check():
    """Endpoint de santé pour monitoring."""
    try:
        import shutil
        checks = {
            'master_bom_accessible': Path('Master_BOM.xlsx').exists(),
            'output_dir_writable': os.access('output', os.W_OK),
            'config_exists': Path('config/default.json').exists(),
            'disk_space_mb': shutil.disk_usage('.').free // (1024*1024)
        }

        all_healthy = all(checks.values()) and checks['disk_space_mb'] > 100
        status_code = 200 if all_healthy else 503

        return jsonify({
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/config')
def config_page():
    return render_template('config.html', config={})

@app.errorhandler(413)
def too_large(e):
    flash('Fichier trop volumineux (max 100MB)', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    print("🌐 Component Data Processor - Interface Web")
    print("📱 Disponible sur: http://localhost:5000")
    print("🔧 Ctrl+C pour arrêter")
    print("=" * 50)
    
    # Créer les dossiers nécessaires
    Path('frontend/templates').mkdir(parents=True, exist_ok=True)
    Path('frontend/static').mkdir(parents=True, exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
