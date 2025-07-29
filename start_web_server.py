#!/usr/bin/env python3
"""
Script de démarrage du serveur web pour le Component Data Processor
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

def check_flask():
    """Vérifie si Flask est installé."""
    try:
        import flask
        return True
    except ImportError:
        return False

def install_flask():
    """Installe Flask si nécessaire."""
    print("📦 Installation de Flask...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask'], check=True)
        print("✅ Flask installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation de Flask")
        return False

def start_simple_server():
    """Démarre un serveur HTTP simple pour servir les fichiers statiques."""
    import http.server
    import socketserver
    from threading import Thread
    
    PORT = 8000
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="frontend/static", **kwargs)
    
    print(f"🌐 Démarrage du serveur simple sur http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📱 Interface disponible sur: http://localhost:{PORT}")
        print("🔧 Utilisez Ctrl+C pour arrêter")
        
        # Ouvrir le navigateur
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")

def create_static_html():
    """Crée une page HTML statique simple."""
    static_dir = Path("frontend/static")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Data Processor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-microchip me-2"></i>
                Component Data Processor
            </a>
        </div>
    </nav>

    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card">
                    <div class="card-body text-center py-5">
                        <i class="fas fa-microchip fa-4x text-primary mb-3"></i>
                        <h1 class="card-title">Component Data Processor</h1>
                        <p class="card-text lead">
                            Interface web pour le traitement automatisé des données de composants
                        </p>
                        
                        <div class="alert alert-info">
                            <h5><i class="fas fa-info-circle me-2"></i>Utilisation via ligne de commande</h5>
                            <p>En attendant que l'interface web soit pleinement opérationnelle, 
                               utilisez les commandes suivantes :</p>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <div class="card border-primary">
                                    <div class="card-body">
                                        <h6><i class="fas fa-file-excel me-2"></i>Créer des exemples</h6>
                                        <code>python runner.py samples</code>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card border-success">
                                    <div class="card-body">
                                        <h6><i class="fas fa-cogs me-2"></i>Traiter un fichier</h6>
                                        <code>python runner.py process file.xlsx</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <div class="card border-info">
                                    <div class="card-body">
                                        <h6><i class="fas fa-check-circle me-2"></i>Valider un fichier</h6>
                                        <code>python runner.py validate file.xlsx</code>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card border-warning">
                                    <div class="card-body">
                                        <h6><i class="fas fa-info me-2"></i>Statut du système</h6>
                                        <code>python runner.py status</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <hr>
                        
                        <h5><i class="fas fa-rocket me-2"></i>Workflow complet</h5>
                        <div class="text-start">
                            <ol>
                                <li><code>python runner.py setup</code> - Configuration initiale</li>
                                <li><code>python runner.py samples</code> - Créer des exemples</li>
                                <li><code>python runner.py process Sample_Input_Data.xlsx</code> - Test</li>
                                <li><code>python runner.py process votre_fichier.xlsx</code> - Traitement réel</li>
                            </ol>
                        </div>
                        
                        <div class="alert alert-success mt-3">
                            <h6><i class="fas fa-folder me-2"></i>Fichiers de sortie</h6>
                            <p class="mb-0">Les résultats sont générés dans le dossier <code>output/</code></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    with open(static_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ Page HTML statique créée")

def main():
    """Fonction principale."""
    print("🚀 Component Data Processor - Démarrage du serveur web")
    print("=" * 60)
    
    # Créer la page statique
    create_static_html()
    
    # Vérifier Flask
    if not check_flask():
        if not install_flask():
            print("⚠️  Flask non disponible, utilisation du serveur simple")
            start_simple_server()
            return
    
    # Essayer de démarrer Flask
    try:
        print("🌐 Tentative de démarrage du serveur Flask...")
        
        # Importer Flask ici pour éviter les problèmes
        from flask import Flask, render_template
        
        app = Flask(__name__, template_folder='frontend/templates')
        app.secret_key = 'component_processor_key'
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        print("📱 Serveur Flask démarré sur http://localhost:5000")
        webbrowser.open('http://localhost:5000')
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Erreur Flask: {e}")
        print("🔄 Basculement vers le serveur simple...")
        start_simple_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n💡 Utilisez directement la ligne de commande:")
        print("   python runner.py --help")
