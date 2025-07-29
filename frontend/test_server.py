#!/usr/bin/env python3
"""
Serveur de test minimal pour le frontend
"""

from flask import Flask, render_template, jsonify

app = Flask(__name__)
app.secret_key = 'test_key'

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/upload')
def upload():
    """Page d'upload."""
    return render_template('upload.html')

@app.route('/samples')
def samples():
    """Page d'exemples."""
    return render_template('samples.html', success=False)

@app.route('/help')
def help_page():
    """Page d'aide."""
    return render_template('help.html')

@app.route('/config')
def config():
    """Page de configuration."""
    return render_template('config.html', config={})

@app.route('/api/status')
def api_status():
    """API statut."""
    return jsonify({
        'dependencies_ok': True,
        'output_files_count': 0,
        'master_bom_exists': False,
        'config_exists': True,
        'timestamp': '2025-07-29T08:00:00'
    })

@app.route('/api/files')
def api_files():
    """API fichiers."""
    return jsonify({'files': []})

if __name__ == '__main__':
    print("🌐 Serveur de test démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
