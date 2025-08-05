#!/usr/bin/env python3
"""
Backend FastAPI Stable - Version parfaitement stable
Sans emojis Unicode, avec gestion CORS complète et gestion d'erreurs robuste
"""

import logging
import subprocess
import sys
import os
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Configuration du logging sans emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_stable.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("backend_stable")

# Configuration
MASTER_BOM_PATH = "Master_BOM_Real.xlsx"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Créer l'application FastAPI
app = FastAPI(
    title="Component Data Processor API - Stable",
    description="API stable pour le traitement de données de composants",
    version="2.0.0"
)

# Configuration CORS complète
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class SuggestColumnRequest(BaseModel):
    input_name: str

class FindBestColumnRequest(BaseModel):
    project_hint: str = ""

class ProcessRequest(BaseModel):
    file_id: str
    filename: str
    project_column: str
    key_column: str = "PN"

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur globale: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erreur interne du serveur",
            "error": str(exc)
        }
    )

@app.get("/health")
async def health_check():
    """Vérification de l'état du système"""
    try:
        master_bom_exists = Path(MASTER_BOM_PATH).exists()
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "master_bom_available": master_bom_exists,
            "upload_dir": str(UPLOAD_DIR),
            "version": "2.0.0-stable"
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/project-columns")
async def get_project_columns():
    """Retourne les colonnes de projets avec analyse complète"""
    try:
        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouve")
        
        # Charger le Master BOM
        df = pd.read_excel(master_bom_path)
        logger.info(f"Master BOM charge: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Analyser les colonnes de projets (colonnes 2-23, index 1-22)
        project_columns = []
        start_col = 1  # Colonne 2 (index 1)
        end_col = min(23, len(df.columns))  # Jusqu'à colonne 23
        
        for col_idx in range(start_col, end_col):
            if col_idx < len(df.columns):
                col_name = df.columns[col_idx]
                
                # Calculer les statistiques
                total_entries = len(df)
                non_null_entries = df[col_name].notna().sum()
                fill_percentage = (non_null_entries / total_entries * 100) if total_entries > 0 else 0
                
                # Identifier les colonnes de projets
                is_project_column = any(keyword in str(col_name).upper() 
                                      for keyword in ['V710', 'J74', 'B2', 'PP'])
                
                project_columns.append({
                    "name": str(col_name),
                    "fill_count": int(non_null_entries),
                    "total_count": int(total_entries),
                    "fill_percentage": float(round(fill_percentage, 1)),
                    "is_project_column": is_project_column
                })
        
        # Trier par pourcentage de remplissage décroissant
        project_columns.sort(key=lambda x: x["fill_percentage"], reverse=True)
        
        logger.info(f"Analyse terminee: {len(project_columns)} colonnes de projets")
        
        return {
            "success": True,
            "message": f"{len(project_columns)} colonnes de projets trouvees",
            "columns": project_columns,
            "total_columns": len(project_columns)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation des colonnes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-column")
async def suggest_column(request: SuggestColumnRequest):
    """Suggère la meilleure colonne basée sur un nom d'entrée"""
    try:
        input_name = request.input_name.strip()
        
        if not input_name:
            return {
                "success": False,
                "message": "Nom d'entree requis"
            }
        
        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouve")
        
        # Charger le Master BOM
        df = pd.read_excel(master_bom_path)
        
        # Obtenir les colonnes disponibles (colonnes 2-23)
        available_columns = []
        for col_idx in range(1, min(23, len(df.columns))):
            if col_idx < len(df.columns):
                available_columns.append(df.columns[col_idx])
        
        # Logique de suggestion simple mais efficace
        best_column = ""
        best_score = 0.0
        
        # Extraire les parties du nom d'entrée
        input_parts = input_name.upper().split('_')
        
        for col_name in available_columns:
            col_parts = str(col_name).upper().split('_')
            
            # Calculer le score de correspondance
            score = 0.0
            matches = 0
            
            for input_part in input_parts:
                for col_part in col_parts:
                    if input_part in col_part or col_part in input_part:
                        matches += 1
                        break
            
            if len(input_parts) > 0:
                score = matches / len(input_parts)
            
            if score > best_score:
                best_score = score
                best_column = col_name
        
        logger.info(f"Suggestion pour '{input_name}': {best_column} (score: {best_score:.2f})")
        
        return {
            "success": True,
            "suggested_column": best_column,
            "confidence": float(best_score),
            "input_name": input_name,
            "available_columns_count": len(available_columns)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find-best-project-column")
async def find_best_project_column(request: FindBestColumnRequest):
    """Trouve la meilleure colonne de projet avec analyse complète"""
    try:
        project_hint = request.project_hint.strip()
        
        master_bom_path = Path(MASTER_BOM_PATH)
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouve")
        
        # Charger le Master BOM
        df = pd.read_excel(master_bom_path)
        
        # Obtenir l'analyse complète des colonnes
        columns_response = await get_project_columns()
        columns_analysis = columns_response["columns"]
        
        # Si un indice de projet est fourni, utiliser la suggestion
        if project_hint:
            suggest_response = await suggest_column(SuggestColumnRequest(input_name=project_hint))
            best_column = suggest_response["suggested_column"]
            confidence = suggest_response["confidence"]
        else:
            # Prendre la colonne avec le meilleur remplissage parmi les colonnes de projets
            project_columns = [col for col in columns_analysis if col["is_project_column"]]
            if project_columns:
                best_column = project_columns[0]["name"]
                confidence = project_columns[0]["fill_percentage"] / 100
            else:
                best_column = columns_analysis[0]["name"] if columns_analysis else ""
                confidence = 0.0
        
        logger.info(f"Meilleure colonne trouvee: {best_column} (confiance: {confidence:.2f})")
        
        return {
            "success": True,
            "best_column": best_column,
            "confidence": float(confidence),
            "project_hint": project_hint,
            "analysis": {
                "total_columns": len(columns_analysis),
                "columns_analysis": columns_analysis[:10]  # Top 10 pour éviter les réponses trop lourdes
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de la meilleure colonne: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload d'un fichier avec validation"""
    try:
        # Validation du fichier
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier requis")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Format de fichier non supporte")
        
        # Générer un ID unique
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nom de fichier sécurisé
        safe_filename = f"{timestamp}_{file_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Sauvegarder le fichier
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validation du contenu
        try:
            df = pd.read_excel(file_path)
            rows_count = len(df)
            cols_count = len(df.columns)
        except Exception as e:
            # Supprimer le fichier en cas d'erreur
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=f"Fichier Excel invalide: {e}")
        
        logger.info(f"Fichier uploade: {safe_filename} ({rows_count} lignes, {cols_count} colonnes)")
        
        return {
            "success": True,
            "message": "Fichier uploade avec succes",
            "file_id": file_id,
            "filename": safe_filename,
            "original_filename": file.filename,
            "rows_count": rows_count,
            "cols_count": cols_count,
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_file(
    file_id: str,
    filename: str,
    project_column: str,
    key_column: str = "PN"
):
    """Traite un fichier uploadé avec la colonne de projet spécifiée"""
    try:
        # Trouver le fichier
        file_path = None
        for path in UPLOAD_DIR.glob(f"*{file_id}*"):
            if filename in path.name:
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouve")
        
        logger.info(f"Debut du traitement: {filename} avec colonne {project_column}")
        
        # Utiliser ETL-Automated-Tool pour lookup simple en lecture seule
        from enhanced_lookup_processor import enhanced_lookup_processor
        import pandas as pd

        # Charger les données
        master_bom_path = Path("Master_BOM_Real.xlsx")
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouve")

        master_bom = pd.read_excel(master_bom_path)
        target_df = pd.read_excel(file_path)

        logger.info(f"Master BOM: {len(master_bom)} lignes")
        logger.info(f"Donnees d'entree: {len(target_df)} lignes")

        # Trouver la colonne PN dans le fichier d'entrée
        input_pn_col = None
        possible_pn_cols = ['PN', 'YAZAKI PN', 'Yazaki PN', 'yazaki pn', 'Part Number']

        for col in possible_pn_cols:
            if col in target_df.columns:
                input_pn_col = col
                break

        if input_pn_col is None:
            # Chercher une colonne contenant 'PN'
            for col in target_df.columns:
                if 'PN' in col.upper():
                    input_pn_col = col
                    break

        if input_pn_col is None:
            raise HTTPException(status_code=400, detail=f"Aucune colonne PN trouvée dans le fichier d'entrée. Colonnes disponibles: {list(target_df.columns)}")

        logger.info(f"Colonne PN du fichier d'entrée: {input_pn_col}")

        # Effectuer le lookup avec ETL-Automated-Tool (lecture seule)
        result_df, stats = enhanced_lookup_processor.add_activation_status(
            master_bom, target_df, input_pn_col, project_column
        )

        logger.info(f"Lookup termine: {stats}")

        # Sauvegarder le résultat
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_file = Path("output") / f"Update_{timestamp}.xlsx"
        output_file.parent.mkdir(exist_ok=True)

        result_df.to_excel(output_file, index=False)
        logger.info(f"Resultat sauvegarde: {output_file}")

        success = True
        
        if success:
            logger.info(f"Traitement reussi pour {filename}")

            # Chercher les fichiers de sortie générés
            output_files = []
            output_dir = Path("output")
            if output_dir.exists():
                # Chercher les fichiers générés récemment (dernières 5 minutes)
                import time
                current_time = time.time()
                for output_file in output_dir.glob("*.xlsx"):
                    file_age = current_time - output_file.stat().st_mtime
                    if file_age < 300:  # 5 minutes
                        output_files.append({
                            "filename": output_file.name,
                            "size": output_file.stat().st_size,
                            "download_url": f"/download/{output_file.name}"
                        })

            return {
                "success": True,
                "message": "Traitement termine avec succes",
                "file_id": file_id,
                "filename": filename,
                "project_column": project_column,
                "key_column": key_column,
                "output_files": output_files
            }
        else:
            logger.error(f"Traitement echoue pour {filename}")
            return {
                "success": False,
                "message": "Traitement echoue",
                "file_id": file_id,
                "filename": filename
            }
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/download/{filename}", methods=["GET", "HEAD"])
async def download_file(filename: str, request: Request):
    """Télécharge un fichier de sortie"""
    try:
        # Sécurité: vérifier que le nom de fichier est sûr
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Nom de fichier invalide")

        # Chercher le fichier dans le répertoire output
        output_dir = Path("output")
        file_path = output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouve")

        # Vérifier que c'est un fichier Excel
        if not filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Type de fichier non autorise")

        logger.info(f"Telechargement: {filename}")

        # Pour les requêtes HEAD, retourner seulement les headers
        if request.method == "HEAD":
            from fastapi.responses import Response
            return Response(
                headers={
                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "Content-Length": str(file_path.stat().st_size),
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

        # Pour les requêtes GET, retourner le fichier
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du telechargement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list-outputs")
async def list_output_files():
    """Liste les fichiers de sortie disponibles"""
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            return {
                "success": True,
                "files": [],
                "message": "Aucun fichier de sortie disponible"
            }

        files = []
        for file_path in output_dir.glob("*.xlsx"):
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "download_url": f"/download/{file_path.name}"
            })

        # Trier par date de modification (plus récent en premier)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return {
            "success": True,
            "files": files,
            "count": len(files)
        }

    except Exception as e:
        logger.error(f"Erreur lors de la liste des fichiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preview/{filename}")
async def preview_file(filename: str):
    """Aperçu d'un fichier Excel (premières lignes)"""
    try:
        # Sécurité: vérifier que le nom de fichier est sûr
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Nom de fichier invalide")

        # Chercher le fichier dans le répertoire output
        output_dir = Path("output")
        file_path = output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouve")

        # Vérifier que c'est un fichier Excel
        if not filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Type de fichier non autorise pour apercu")

        logger.info(f"Apercu: {filename}")

        # Lire le fichier Excel et retourner un aperçu
        import pandas as pd

        try:
            # Lire seulement les 10 premières lignes
            df = pd.read_excel(file_path, nrows=10)

            # Convertir en format JSON pour l'aperçu
            preview_data = {
                "filename": filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "sample_data": df.head(5).fillna("").to_dict('records'),
                "file_size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            }

            return {
                "success": True,
                "preview": preview_data
            }

        except Exception as e:
            logger.error(f"Erreur lecture Excel: {e}")
            return {
                "success": False,
                "message": f"Impossible de lire le fichier Excel: {str(e)}"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'apercu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("BACKEND FASTAPI STABLE - Version 2.0.0")
    print("=" * 60)
    print("Fonctionnalites:")
    print("- Gestion CORS complete")
    print("- Pas d'emojis Unicode")
    print("- Gestion d'erreurs robuste")
    print("- Logging complet")
    print("- Validation des donnees")
    print("=" * 60)
    
    uvicorn.run(
        "backend_stable:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Désactiver le reload pour plus de stabilité
        log_level="info"
    )
