#!/usr/bin/env python3
"""
Frontend Web complet et fonctionnel pour le Component Data Processor
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'component_processor_secret_key_2025'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Configuration
UPLOAD_FOLDER = Path('frontend/uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Page d'upload et de traitement des fichiers."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = UPLOAD_FOLDER / filename
            file.save(filepath)
            
            # Traiter le fichier avec le runner
            try:
                result = subprocess.run(
                    ['python', 'runner.py', 'process', str(filepath)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=Path(__file__).parent.parent
                )
                
                if result.returncode == 0:
                    flash('Fichier traité avec succès !', 'success')
                    return render_template('results.html', 
                                         filename=filename, 
                                         success=True,
                                         output=result.stdout)
                else:
                    flash(f'Erreur lors du traitement: {result.stderr}', 'error')
                    return render_template('results.html', 
                                         filename=filename, 
                                         success=False,
                                         error=result.stderr)
            
            except subprocess.TimeoutExpired:
                flash('Timeout: Le traitement a pris trop de temps', 'error')
                return render_template('results.html', 
                                     filename=filename, 
                                     success=False,
                                     error='Timeout')
            except Exception as e:
                flash(f'Erreur: {str(e)}', 'error')
                return render_template('results.html', 
                                     filename=filename, 
                                     success=False,
                                     error=str(e))
        
        else:
            flash('Type de fichier non autorisé. Utilisez .xlsx ou .xls', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/validate', methods=['POST'])
def validate_file():
    """Valide un fichier sans le traiter."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Fichier invalide'}), 400
        
        # Validation simple avec pandas
        import pandas as pd
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            
            try:
                df = pd.read_excel(tmp_file.name)
                
                content_errors = []
                
                if df.empty:
                    content_errors.append('Le fichier est vide')
                
                required_columns = ['PN', 'Project']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    content_errors.append(f'Colonnes manquantes: {", ".join(missing_columns)}')
                
                for col in required_columns:
                    if col in df.columns:
                        missing_count = df[col].isna().sum()
                        if missing_count > 0:
                            content_errors.append(f'Colonne "{col}": {missing_count} valeurs manquantes')
                
                result = {
                    'format_valid': True,
                    'format_error': '',
                    'content_valid': len(content_errors) == 0,
                    'content_errors': content_errors,
                    'overall_valid': len(content_errors) == 0
                }
                
                return jsonify(result)
            
            except Exception as e:
                return jsonify({'error': f'Erreur de lecture: {str(e)}'}), 500
            
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
    
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@app.route('/samples', methods=['GET', 'POST'])
def create_samples():
    """Crée des fichiers d'exemple."""
    if request.method == 'POST':
        try:
            result = subprocess.run(
                ['python', 'runner.py', 'samples'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode == 0:
                flash('Fichiers d\'exemple créés avec succès !', 'success')
                return render_template('samples.html', success=True)
            else:
                flash(f'Erreur: {result.stderr}', 'error')
                return render_template('samples.html', success=False)
        
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
            return render_template('samples.html', success=False)
    
    return render_template('samples.html', success=False)

@app.route('/download/<filename>')
def download_file(filename):
    """Télécharge un fichier de sortie."""
    try:
        output_dir = Path(__file__).parent.parent / 'output'
        file_path = output_dir / filename
        
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            flash('Fichier non trouvé', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API pour obtenir le statut du système."""
    try:
        import pandas, numpy, openpyxl
        dependencies_ok = True
    except ImportError:
        dependencies_ok = False
    
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / 'output'
    output_files = list(output_dir.glob('*')) if output_dir.exists() else []
    
    status = {
        'dependencies_ok': dependencies_ok,
        'output_files_count': len(output_files),
        'master_bom_exists': (base_dir / 'Master_BOM.xlsx').exists(),
        'config_exists': (base_dir / 'config' / 'default.json').exists(),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status)

@app.route('/api/files')
def api_files():
    """API pour lister les fichiers de sortie."""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / 'output'
    
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

@app.route('/help')
def help_page():
    """Page d'aide."""
    return render_template('help.html')

@app.route('/config')
def config_page():
    """Page de configuration."""
    return render_template('config.html', config={})

@app.route('/config', methods=['POST'])
def save_config():
    """Sauvegarde la configuration."""
    try:
        config_data = request.get_json()
        
        base_dir = Path(__file__).parent.parent
        config_file = base_dir / 'config' / 'default.json'
        config_file.parent.mkdir(exist_ok=True)
        
        import json
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Gestion des fichiers trop volumineux."""
    flash('Fichier trop volumineux (max 100MB)', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    print("🌐 Démarrage du frontend Component Data Processor...")
    print("📱 Interface web disponible sur: http://localhost:5000")
    print("🔧 Utilisez Ctrl+C pour arrêter le serveur")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
