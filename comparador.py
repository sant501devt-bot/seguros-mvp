import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from audit_schema import ResultadoComparacion
from pdf import extraer_texto_pdf 

load_dotenv("data.env")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

with open("poliza_comparador.txt", "r", encoding="utf-8") as f:
    system_instruction = f.read()


def comparar_poliza_siniestro(ruta_poliza_pdf: str, ruta_siniestro_pdf: str) -> str:
    """
    Recibe la póliza y el reporte del siniestro (ambos PDFs), y le pide a la IA
    que determine, ítem por ítem, qué está cubierto, qué no, y qué queda en zona gris.
    """
    texto_poliza = extraer_texto_pdf(ruta_poliza_pdf)
    texto_siniestro = extraer_texto_pdf(ruta_siniestro_pdf)

    prompt = (
        f"--- TEXTO DE LA PÓLIZA ---\n{texto_poliza}\n\n"
        f"--- TEXTO DEL REPORTE DE SINIESTRO ---\n{texto_siniestro}\n\n"
        "Compara el siniestro contra la póliza y determina la cobertura de cada ítem."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ResultadoComparacion,
            temperature=0.1,
        ),
    )

    return response.text


if __name__ == "__main__":
    poliza_test = "mi_poliza_real.pdf"
    siniestro_test = "reporte_siniestro.pdf"

    if os.path.exists(poliza_test) and os.path.exists(siniestro_test):
        print("Comparando póliza contra siniestro...")
        resultado_json = comparar_poliza_siniestro(poliza_test, siniestro_test)
        print("\n--- RESULTADO DE LA COMPARACIÓN ---")
        print(resultado_json)
    else:
        print("Coloca 'mi_poliza_real.pdf' y 'reporte_siniestro.pdf' en la carpeta para probar.")