#!/usr/bin/env python3
"""
Interface Web simple et fonctionnelle pour le Component Data Processor
"""

import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for

# Configuration Flask
app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')
app.secret_key = 'component_processor_key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Configuration
UPLOAD_FOLDER = Path('frontend/uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

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
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = UPLOAD_FOLDER / filename
            file.save(filepath)
            
            try:
                result = subprocess.run(
                    ['python', 'runner.py', 'process', str(filepath)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
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
                ['python', 'runner.py', 'samples'],
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
        # Chercher d'abord dans le dossier output
        output_dir = Path('output')
        file_path = output_dir / filename

        if file_path.exists():
            return send_file(file_path, as_attachment=True)

        # Si pas trouvé, chercher dans le répertoire racine (pour Master_BOM.xlsx, etc.)
        root_file_path = Path(filename)
        if root_file_path.exists():
            return send_file(root_file_path, as_attachment=True)

        # Fichier non trouvé
        flash(f'Fichier non trouvé: {filename}', 'error')
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
