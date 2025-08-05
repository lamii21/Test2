#!/usr/bin/env python3
"""
Démarrage du Système Stable - Version parfaitement stable
Gestion automatique du backend et frontend avec monitoring
"""

import subprocess
import sys
import time
import signal
import threading
import requests
import psutil
from datetime import datetime
from pathlib import Path

class StableSystemManager:
    """Gestionnaire du système stable"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = 8000
        self.frontend_port = 5000
        self.running = True
        
    def print_banner(self):
        """Affiche la bannière du système"""
        print("=" * 70)
        print("COMPONENT DATA PROCESSOR v2.0 - SYSTÈME STABLE")
        print("Backend FastAPI Stable + Frontend Flask Enhanced")
        print("=" * 70)
        print(f"Demarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def check_port_available(self, port):
        """Vérifie si un port est disponible"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0
        except:
            return True
    
    def kill_process_on_port(self, port):
        """Tue les processus utilisant un port spécifique"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            print(f"[CLEANUP] Arret du processus {proc.info['name']} (PID: {proc.info['pid']}) sur port {port}")
                            proc.terminate()
                            proc.wait(timeout=5)
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"[ERREUR] Nettoyage port {port}: {e}")
        return False
    
    def start_backend(self):
        """Démarre le backend stable"""
        print("[BACKEND] Demarrage du backend FastAPI stable...")
        
        # Nettoyer le port si nécessaire
        if not self.check_port_available(self.backend_port):
            print(f"[BACKEND] Port {self.backend_port} occupe, nettoyage...")
            self.kill_process_on_port(self.backend_port)
            time.sleep(2)
        
        try:
            # Démarrer le backend stable
            self.backend_process = subprocess.Popen([
                sys.executable, "backend_stable.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Attendre que le backend soit prêt
            for i in range(30):
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"[BACKEND] Demarrage reussi!")
                        print(f"[BACKEND] Version: {data.get('version', 'unknown')}")
                        print(f"[BACKEND] Status: {data.get('status', 'unknown')}")
                        print(f"[BACKEND] URL: http://localhost:{self.backend_port}")
                        print(f"[BACKEND] Documentation: http://localhost:{self.backend_port}/docs")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"[BACKEND] Attente demarrage... ({i+1}/30)")
            
            print("[BACKEND] ERREUR: Timeout lors du demarrage")
            return False
            
        except Exception as e:
            print(f"[BACKEND] ERREUR: {e}")
            return False
    
    def start_frontend(self):
        """Démarre le frontend Flask"""
        print("\n[FRONTEND] Demarrage du frontend Flask...")
        
        # Nettoyer le port si nécessaire
        if not self.check_port_available(self.frontend_port):
            print(f"[FRONTEND] Port {self.frontend_port} occupe, nettoyage...")
            self.kill_process_on_port(self.frontend_port)
            time.sleep(2)
        
        try:
            # Modifier le frontend pour utiliser le client stable
            self.update_frontend_to_stable()
            
            # Démarrer le frontend
            self.frontend_process = subprocess.Popen([
                sys.executable, "simple_web.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Attendre que le frontend soit prêt
            for i in range(20):
                try:
                    response = requests.get(f"http://localhost:{self.frontend_port}", timeout=2)
                    if response.status_code == 200:
                        print(f"[FRONTEND] Demarrage reussi!")
                        print(f"[FRONTEND] URL: http://localhost:{self.frontend_port}")
                        print(f"[FRONTEND] Interface avancee: http://localhost:{self.frontend_port}/enhanced")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"[FRONTEND] Attente demarrage... ({i+1}/20)")
            
            print("[FRONTEND] ERREUR: Timeout lors du demarrage")
            return False
            
        except Exception as e:
            print(f"[FRONTEND] ERREUR: {e}")
            return False
    
    def update_frontend_to_stable(self):
        """Met à jour le frontend pour utiliser le client API stable"""
        try:
            # Lire le fichier frontend
            with open("simple_web.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remplacer l'import du client API
            if "from frontend_api_client import api_client" in content:
                content = content.replace(
                    "from frontend_api_client import api_client",
                    "from frontend_api_client_stable import stable_api_client as api_client"
                )
                
                # Sauvegarder
                with open("simple_web.py", "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("[FRONTEND] Configuration mise a jour pour utiliser le client stable")
        except Exception as e:
            print(f"[FRONTEND] Erreur mise a jour: {e}")
    
    def test_integration(self):
        """Test d'intégration du système"""
        print("\n[TEST] Test d'integration du systeme...")
        
        try:
            # Test backend
            health = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if health.status_code != 200:
                print("[TEST] ERREUR: Backend non accessible")
                return False
            
            # Test colonnes
            columns = requests.get(f"http://localhost:{self.backend_port}/project-columns", timeout=10)
            if columns.status_code != 200:
                print("[TEST] ERREUR: API colonnes non accessible")
                return False
            
            columns_data = columns.json()
            if not columns_data.get('success'):
                print("[TEST] ERREUR: API colonnes retourne une erreur")
                return False
            
            cols_count = len(columns_data.get('columns', []))
            print(f"[TEST] Backend OK: {cols_count} colonnes detectees")
            
            # Test frontend
            frontend = requests.get(f"http://localhost:{self.frontend_port}", timeout=5)
            if frontend.status_code != 200:
                print("[TEST] ERREUR: Frontend non accessible")
                return False
            
            print("[TEST] Frontend OK: Interface accessible")
            
            # Test API frontend
            frontend_api = requests.get(f"http://localhost:{self.frontend_port}/api/project-columns", timeout=10)
            if frontend_api.status_code == 200:
                print("[TEST] API Frontend OK: Communication backend etablie")
            else:
                print("[TEST] AVERTISSEMENT: API Frontend non accessible")
            
            print("[TEST] INTEGRATION REUSSIE!")
            return True
            
        except Exception as e:
            print(f"[TEST] ERREUR: {e}")
            return False
    
    def monitor_processes(self):
        """Surveille les processus en arrière-plan"""
        while self.running:
            try:
                # Vérifier le backend
                if self.backend_process and self.backend_process.poll() is not None:
                    print("[MONITOR] Backend arrete inattenduement!")
                    self.running = False
                    break
                
                # Vérifier le frontend
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("[MONITOR] Frontend arrete inattenduement!")
                    self.running = False
                    break
                
                time.sleep(5)  # Vérification toutes les 5 secondes
                
            except Exception as e:
                print(f"[MONITOR] Erreur: {e}")
                break
    
    def cleanup(self):
        """Nettoie les processus"""
        print("\n[CLEANUP] Arret des services...")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("[CLEANUP] Frontend arrete")
            except:
                try:
                    self.frontend_process.kill()
                except:
                    pass
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("[CLEANUP] Backend arrete")
            except:
                try:
                    self.backend_process.kill()
                except:
                    pass
        
        print("[CLEANUP] Nettoyage termine")
    
    def run(self):
        """Lance le système complet"""
        try:
            self.print_banner()
            
            # Démarrer le backend
            if not self.start_backend():
                print("[ERREUR] Impossible de demarrer le backend")
                return 1
            
            # Démarrer le frontend
            if not self.start_frontend():
                print("[ERREUR] Impossible de demarrer le frontend")
                self.cleanup()
                return 1
            
            # Test d'intégration
            if not self.test_integration():
                print("[ERREUR] Tests d'integration echoues")
                self.cleanup()
                return 1
            
            # Démarrer le monitoring
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            # Afficher les informations finales
            print("\n" + "=" * 70)
            print("SYSTEME STABLE OPERATIONNEL!")
            print("=" * 70)
            print("Services disponibles:")
            print(f"  Interface Web:     http://localhost:{self.frontend_port}")
            print(f"  Interface Avancee: http://localhost:{self.frontend_port}/enhanced")
            print(f"  API Backend:       http://localhost:{self.backend_port}")
            print(f"  Documentation:     http://localhost:{self.backend_port}/docs")
            print()
            print("Fonctionnalites:")
            print("  - Backend FastAPI stable (sans emojis Unicode)")
            print("  - Gestion CORS complete")
            print("  - Client API robuste")
            print("  - Monitoring automatique")
            print("  - Gestion d'erreurs avancee")
            print()
            print("Appuyez sur Ctrl+C pour arreter tous les services")
            print("=" * 70)
            
            # Attendre indéfiniment
            while self.running:
                time.sleep(1)
            
            return 0
            
        except KeyboardInterrupt:
            print("\n[INFO] Arret demande par l'utilisateur")
        except Exception as e:
            print(f"\n[ERREUR] Erreur inattendue: {e}")
        finally:
            self.running = False
            self.cleanup()
            return 0

def main():
    """Fonction principale"""
    manager = StableSystemManager()
    
    # Gestionnaire de signal pour arrêt propre
    def signal_handler(signum, frame):
        print(f"\n[SIGNAL] Signal {signum} recu")
        manager.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return manager.run()

if __name__ == "__main__":
    sys.exit(main())
