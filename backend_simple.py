#!/usr/bin/env python3
"""
Backend FastAPI simplifié pour Component Data Processor
Version standalone sans imports relatifs
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import logging
from pathlib import Path
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import uuid
import subprocess
import sys
from enhanced_lookup_processor import enhanced_lookup_processor
import json

# Configuration simple
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000
MASTER_BOM_PATH = "Master_BOM_Real.xlsx"
UPLOAD_DIR = Path("frontend/uploads")
CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]

# Créer le répertoire d'upload
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Component Data Processor API",
    description="API REST pour le traitement des données de composants YAZAKI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Événement de démarrage"""
    logger.info("🚀 Démarrage du backend FastAPI simplifié")
    logger.info(f"📊 Master BOM: {MASTER_BOM_PATH}")


@app.get("/health")
async def health_check():
    """Vérification de l'état du système"""
    uptime = time.time() - start_time
    master_bom_exists = Path(MASTER_BOM_PATH).exists()
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "uptime": uptime,
        "master_bom_available": master_bom_exists,
        "upload_dir_writable": True
    }


@app.get("/project-columns")
async def get_project_columns():
    """
    Récupère les colonnes de projets disponibles dans le Master BOM
    """
    try:
        master_bom_path = Path(MASTER_BOM_PATH)
        
        if not master_bom_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Master BOM non trouvé: {MASTER_BOM_PATH}"
            )
        
        # Charger le Master BOM
        master_bom = pd.read_excel(master_bom_path)

        # Utiliser la logique avancée d'ETL-Automated-Tool
        analysis = enhanced_lookup_processor.analyze_project_columns(master_bom)

        logger.info(f"📊 {analysis['total_columns']} colonnes de projets trouvées")

        return {
            "success": True,
            "message": f"{analysis['total_columns']} colonnes de projets trouvées",
            "columns": analysis["columns_analysis"],
            "total_columns": analysis["total_columns"]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des colonnes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest-column")
async def suggest_column(request: dict):
    """
    Suggère la meilleure colonne de projet basée sur un nom d'entrée
    Inspiré d'ETL-Automated-Tool
    """
    try:
        input_name = request.get("input_name", "")

        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")

        # Charger le Master BOM
        master_bom = pd.read_excel(master_bom_path)

        # Obtenir les colonnes disponibles
        available_columns = enhanced_lookup_processor.get_column_suggestions(master_bom)

        # Suggérer la meilleure colonne
        suggested_column, confidence = enhanced_lookup_processor.suggest_column(
            input_name, available_columns
        )

        return {
            "success": True,
            "suggested_column": suggested_column,
            "confidence": float(confidence),
            "input_name": input_name,
            "available_columns": available_columns
        }

    except Exception as e:
        logger.error(f"Erreur lors de la suggestion de colonne: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/find-best-project-column")
async def find_best_project_column(request: dict):
    """
    Trouve la meilleure colonne de projet avec analyse complète
    """
    try:
        project_hint = request.get("project_hint", "")

        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")

        # Charger le Master BOM
        master_bom = pd.read_excel(master_bom_path)

        # Trouver la meilleure colonne
        best_column, confidence, analysis = enhanced_lookup_processor.find_best_project_column(
            master_bom, project_hint
        )

        return {
            "success": True,
            "best_column": best_column,
            "confidence": float(confidence),
            "project_hint": project_hint,
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Erreur lors de la recherche de la meilleure colonne: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/advanced-lookup")
async def advanced_lookup(request: dict):
    """
    Effectue un lookup avancé avec la logique d'ETL-Automated-Tool
    """
    try:
        file_id = request.get("file_id")
        filename = request.get("filename")
        project_column = request.get("project_column")
        key_column = request.get("key_column", "PN")

        if not all([file_id, filename, project_column]):
            raise HTTPException(
                status_code=400,
                detail="file_id, filename et project_column sont requis"
            )

        # Trouver le fichier uploadé
        filepath = None
        for file_path in UPLOAD_DIR.glob(f"*{file_id}*"):
            if filename in file_path.name:
                filepath = file_path
                break

        if not filepath or not filepath.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")

        # Charger le Master BOM
        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")

        master_bom = pd.read_excel(master_bom_path)
        target_df = pd.read_excel(filepath)

        # Effectuer le lookup avancé
        result_df, stats = enhanced_lookup_processor.add_activation_status(
            master_bom, target_df, key_column, project_column
        )

        # Sauvegarder le résultat
        output_filename = f"lookup_result_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = UPLOAD_DIR / output_filename
        result_df.to_excel(output_path, index=False)

        return {
            "success": True,
            "message": "Lookup avancé terminé avec succès",
            "stats": stats,
            "result_preview": result_df.head(10).to_dict('records'),
            "output_file": output_filename,
            "total_processed": len(result_df)
        }

    except Exception as e:
        logger.error(f"Erreur lors du lookup avancé: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload et traitement d'un fichier"""
    try:
        # Validation du fichier
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Format de fichier non supporté")

        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{file_id}_{file.filename}"
        filepath = UPLOAD_DIR / filename

        # Sauvegarder le fichier
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)

        logger.info(f"📁 Fichier uploadé: {filename}")

        return {
            "success": True,
            "message": f"Fichier '{file.filename}' uploadé avec succès",
            "file_id": file_id,
            "filename": filename
        }

    except Exception as e:
        logger.error(f"❌ Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_file(
    file_id: str,
    filename: str,
    project_column: Optional[str] = None
):
    """Traite un fichier avec la colonne de projet spécifiée"""
    try:
        # Construire le chemin du fichier
        filepath = None
        for file_path in UPLOAD_DIR.glob(f"*{file_id}*"):
            if filename in file_path.name:
                filepath = file_path
                break

        if not filepath or not filepath.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")

        # Construire la commande de traitement
        cmd = [sys.executable, "runner.py", "process", str(filepath)]

        if project_column:
            cmd.extend(["--project-column", project_column])

        logger.info(f"🔄 Traitement: {' '.join(cmd)}")

        # Exécuter le traitement
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )

        success = result.returncode == 0

        # Analyser la sortie pour déterminer le succès
        if success:
            success_indicators = [
                "Traitement termine avec succes",
                "Traitement terminé avec succès",
                "SUCCÈS"
            ]
            success = any(indicator in result.stdout for indicator in success_indicators)

        return {
            "success": success,
            "message": "Traitement terminé" if success else "Traitement échoué",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Timeout - traitement trop long",
            "stdout": "",
            "stderr": "Timeout après 5 minutes"
        }
    except Exception as e:
        logger.error(f"❌ Erreur traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Component Data Processor API v2.0",
        "docs": "/docs",
        "health": "/health",
        "project_columns": "/project-columns",
        "upload": "/upload",
        "process": "/process"
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du backend FastAPI simplifié...")
    print(f"📡 Host: {BACKEND_HOST}")
    print(f"🔌 Port: {BACKEND_PORT}")
    print(f"📚 Documentation: http://localhost:{BACKEND_PORT}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        log_level="info"
    )
