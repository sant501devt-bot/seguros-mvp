import os
import time
import traceback
from dotenv import load_dotenv
from google import genai
from google.genai import types

from audit_schema import ResultadoAuditoria, calcular_prioridad, nivel_urgencia

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en las variables de entorno.")

client = genai.Client(api_key=api_key)


def auditar_poliza_pdf(ruta_pdf: str) -> dict:
    archivo_gemini = None
    try:
        archivo_gemini = client.files.upload(file=ruta_pdf)

        prompt = "Analiza esta póliza de seguro y extrae los datos clave según el schema proporcionado."

        modelos_validos = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
        response = None

        for modelo in modelos_validos:
            for intento in range(1, 4):
                try:
                    print(f"Enviando petición a {modelo} (Intento {intento})...")
                    response = client.models.generate_content(
                        model=modelo,
                        contents=[archivo_gemini, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ResultadoAuditoria,  # <- vuelve a usar el schema real
                            temperature=0.1,
                        ),
                    )
                    if response and response.text:
                        print(f"Petición exitosa con {modelo}")
                        break
                except Exception as e_model:
                    error_msg = str(e_model)
                    print(f"Intento {intento} fallido con {modelo}: {error_msg}")
                    if "503" in error_msg or "UNAVAILABLE" in error_msg:
                        time.sleep(intento * 2)
                    else:
                        break

            if response and response.text:
                break

        if not response or not response.text:
            raise RuntimeError("No se obtuvo respuesta de la IA.")

        # response.text ya viene como JSON válido según ResultadoAuditoria,
        # gracias a response_schema -- no hace falta limpiar markdown a mano.
        resultado_validado = ResultadoAuditoria.model_validate_json(response.text)

        # La prioridad y la urgencia las calcula PYTHON con la fórmula real,
        # no se le pide a la IA que las invente.
        prioridad = calcular_prioridad(resultado_validado)
        urgencia = nivel_urgencia(prioridad)

        resultado_dict = resultado_validado.model_dump()
        resultado_dict["prioridad"] = prioridad
        resultado_dict["urgencia"] = urgencia

        return resultado_dict

    except Exception as e:
        print("\n--- ERROR DENTRO DE POLIZAS.PY ---")
        traceback.print_exc()
        raise e

    finally:
        if archivo_gemini:
            try:
                client.files.delete(name=archivo_gemini.name)
            except Exception:
                pass
