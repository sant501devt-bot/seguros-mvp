import json
import os
import tempfile
import traceback

from fastapi import FastAPI, File, UploadFile, HTTPException

from polizas import auditar_poliza_pdf
from db_service import guardar_auditoria

app = FastAPI(title="API Auditoria De Seguros MVP")


@app.get("/")
def home():
    return {"mensaje": "El servidor ha cargado con exito"}


@app.post("/auditar")
async def auditar_documento(file: UploadFile = File(...), nombre_proyecto: str = "Proyecto General"):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        ruta_temporal = tmp.name
    try:
        resultado_json = auditar_poliza_pdf(ruta_temporal)

        guardar_auditoria(nombre_proyecto, resultado_json)

        return {
            "estado": "exitoso",
            "archivo": file.filename,
            "analisis": resultado_json,
        }

    except Exception as e:
        print("\n================ ERROR EXACTO DETECTADO ================")
        traceback.print_exc()
        print("========================================================\n")
        raise HTTPException(status_code=500, detail=f"Error procesando la poliza: {str(e)}")

    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)