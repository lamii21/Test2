# Guide de déploiement - Component Data Processor

## Vue d'ensemble

Ce guide décrit les différentes méthodes de déploiement du Component Data Processor, des installations locales aux déploiements en production.

## Prérequis système

### Minimum requis
- **Python**: 3.7 ou supérieur
- **RAM**: 2 GB minimum, 4 GB recommandé
- **Stockage**: 1 GB d'espace libre
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommandé pour production
- **Python**: 3.9 ou supérieur
- **RAM**: 8 GB ou plus
- **Stockage**: SSD avec 10 GB d'espace libre
- **CPU**: 4 cœurs ou plus

## Installation locale

### 1. Installation standard

```bash
# Cloner le repository
git clone https://github.com/your-org/component-data-processor.git
cd component-data-processor

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Tester l'installation
python main.py --version
```

### 2. Installation avec pip (si packagé)

```bash
pip install component-data-processor

# Ou depuis un repository privé
pip install -i https://pypi.your-company.com component-data-processor
```

### 3. Installation pour développement

```bash
# Installation en mode développement
pip install -e .

# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Exécuter les tests
python tests/run_tests.py --coverage
```

## Configuration

### 1. Configuration de base

Créer un fichier `config.json`:

```json
{
  "files": {
    "master_bom_path": "/path/to/Master_BOM.xlsx",
    "output_dir": "/path/to/output"
  },
  "logging": {
    "level": "INFO",
    "log_to_file": true
  },
  "processing": {
    "required_columns": ["PN", "Project"],
    "convert_to_uppercase": true
  }
}
```

### 2. Variables d'environnement

```bash
# Configuration via variables d'environnement
export COMPONENT_PROCESSOR_MASTER_BOM="/data/Master_BOM.xlsx"
export COMPONENT_PROCESSOR_OUTPUT_DIR="/data/output"
export COMPONENT_PROCESSOR_LOG_LEVEL="INFO"
export COMPONENT_PROCESSOR_BACKUP="true"
```

### 3. Configuration pour différents environnements

#### Développement (`config/dev.json`)
```json
{
  "logging": {
    "level": "DEBUG",
    "log_to_console": true
  },
  "files": {
    "backup_enabled": false,
    "cleanup_old_files": false
  }
}
```

#### Production (`config/prod.json`)
```json
{
  "logging": {
    "level": "WARNING",
    "log_to_console": false
  },
  "files": {
    "backup_enabled": true,
    "cleanup_old_files": true,
    "cleanup_days": 30
  }
}
```

## Déploiement en production

### 1. Déploiement sur serveur Linux

#### Installation système
```bash
# Installer Python et dépendances système
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# Créer un utilisateur dédié
sudo useradd -m -s /bin/bash component-processor
sudo su - component-processor

# Installer l'application
git clone https://github.com/your-org/component-data-processor.git
cd component-data-processor
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Service systemd
Créer `/etc/systemd/system/component-processor.service`:

```ini
[Unit]
Description=Component Data Processor
After=network.target

[Service]
Type=simple
User=component-processor
WorkingDirectory=/home/component-processor/component-data-processor
Environment=PATH=/home/component-processor/component-data-processor/venv/bin
ExecStart=/home/component-processor/component-data-processor/venv/bin/python main.py --config /etc/component-processor/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl enable component-processor
sudo systemctl start component-processor
sudo systemctl status component-processor
```

### 2. Déploiement avec Docker

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 processor

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ src/
COPY main.py .
COPY config/ config/

# Changer le propriétaire des fichiers
RUN chown -R processor:processor /app

# Créer les répertoires de données
RUN mkdir -p /data/input /data/output /data/logs
RUN chown -R processor:processor /data

# Basculer vers l'utilisateur non-root
USER processor

# Exposer le port (si API REST)
EXPOSE 8000

# Point d'entrée
ENTRYPOINT ["python", "main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  component-processor:
    build: .
    container_name: component-processor
    volumes:
      - ./data/input:/data/input
      - ./data/output:/data/output
      - ./data/logs:/data/logs
      - ./config/prod.json:/app/config.json
    environment:
      - COMPONENT_PROCESSOR_OUTPUT_DIR=/data/output
      - COMPONENT_PROCESSOR_LOG_LEVEL=INFO
    restart: unless-stopped
    
  # Optionnel: Base de données pour Master BOM
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: component_db
      POSTGRES_USER: processor
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Commandes Docker
```bash
# Construire l'image
docker build -t component-processor .

# Exécuter avec docker-compose
docker-compose up -d

# Voir les logs
docker-compose logs -f component-processor

# Traiter un fichier
docker-compose exec component-processor python main.py /data/input/file.xlsx
```

### 3. Déploiement sur Kubernetes

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: component-processor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: component-processor
  template:
    metadata:
      labels:
        app: component-processor
    spec:
      containers:
      - name: component-processor
        image: your-registry/component-processor:latest
        env:
        - name: COMPONENT_PROCESSOR_LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: config
          mountPath: /app/config.json
          subPath: config.json
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: config
        configMap:
          name: component-processor-config
      - name: data
        persistentVolumeClaim:
          claimName: component-processor-data
```

#### configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: component-processor-config
data:
  config.json: |
    {
      "files": {
        "master_bom_path": "/data/Master_BOM.xlsx",
        "output_dir": "/data/output"
      },
      "logging": {
        "level": "INFO"
      }
    }
```

## Monitoring et maintenance

### 1. Logging

#### Configuration des logs
```json
{
  "logging": {
    "level": "INFO",
    "log_to_file": true,
    "log_file_pattern": "/var/log/component-processor/app_{timestamp}.log"
  }
}
```

#### Rotation des logs avec logrotate
```bash
# /etc/logrotate.d/component-processor
/var/log/component-processor/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 component-processor component-processor
}
```

### 2. Monitoring avec Prometheus

#### Métriques exposées
```python
# Exemple d'extension pour métriques
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
files_processed = Counter('files_processed_total', 'Total files processed')
processing_errors = Counter('processing_errors_total', 'Total processing errors')

# Histogrammes
processing_duration = Histogram('processing_duration_seconds', 'Processing duration')

# Jauges
active_processes = Gauge('active_processes', 'Number of active processes')
```

### 3. Alerting

#### Alertes Prometheus
```yaml
groups:
- name: component-processor
  rules:
  - alert: ProcessingErrors
    expr: increase(processing_errors_total[5m]) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate in component processor"
      
  - alert: ProcessorDown
    expr: up{job="component-processor"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Component processor is down"
```

## Sécurité

### 1. Sécurisation des fichiers

```bash
# Permissions restrictives
chmod 600 config/prod.json
chmod 700 /data/input /data/output

# Chiffrement des fichiers sensibles
gpg --cipher-algo AES256 --compress-algo 1 --symmetric config/prod.json
```

### 2. Sécurisation réseau

```bash
# Firewall (UFW)
sudo ufw allow ssh
sudo ufw allow from 10.0.0.0/8 to any port 8000
sudo ufw enable
```

### 3. Authentification

```python
# Exemple d'authentification API
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalid'}), 401
        return f(*args, **kwargs)
    return decorated
```

## Sauvegarde et récupération

### 1. Stratégie de sauvegarde

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/component-processor"

# Sauvegarder les données
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /data/

# Sauvegarder la configuration
cp /etc/component-processor/config.json "$BACKUP_DIR/config_$DATE.json"

# Nettoyer les anciennes sauvegardes (> 30 jours)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### 2. Procédure de récupération

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Arrêter le service
sudo systemctl stop component-processor

# Restaurer les données
tar -xzf "$BACKUP_FILE" -C /

# Redémarrer le service
sudo systemctl start component-processor
```

## Dépannage

### 1. Problèmes courants

#### Erreur de permissions
```bash
# Vérifier les permissions
ls -la /data/
sudo chown -R component-processor:component-processor /data/
```

#### Problème de mémoire
```bash
# Vérifier l'utilisation mémoire
free -h
# Ajuster la configuration
echo "MAX_BATCH_SIZE = 1000" >> config/prod.py
```

#### Fichier Master BOM verrouillé
```bash
# Vérifier les processus utilisant le fichier
lsof /data/Master_BOM.xlsx
# Tuer les processus si nécessaire
```

### 2. Logs de débogage

```bash
# Activer le mode debug
export COMPONENT_PROCESSOR_LOG_LEVEL=DEBUG

# Suivre les logs en temps réel
tail -f /var/log/component-processor/app_$(date +%Y%m%d).log

# Analyser les erreurs
grep ERROR /var/log/component-processor/*.log | tail -20
```

## Performance

### 1. Optimisation

```python
# Configuration optimisée pour gros volumes
{
  "processing": {
    "max_batch_size": 5000,
    "parallel_processing": true,
    "cache_enabled": true
  }
}
```

### 2. Monitoring des performances

```bash
# Surveiller l'utilisation CPU/mémoire
htop

# Profiler l'application
python -m cProfile main.py input.xlsx

# Analyser les performances I/O
iotop
```
