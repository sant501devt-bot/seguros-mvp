import pdfplumber 

def extraer_texto_pdf(ruta_pdf: str) -> str:
    """
    Lee un archivo PDF de una póliza y extrae todo su texto paginado.
    """
    texto_extraido = ""
    
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for numero_pagina, pagina in enumerate(pdf.pages, start=1):
                contenido_pagina = pagina.extract_text()
                if contenido_pagina:
                    texto_extraido += f"\n--- PÁGINA {numero_pagina} ---\n"
                    texto_extraido += contenido_pagina
                    
        if not texto_extraido.strip():
            raise ValueError("El PDF no contiene texto legible (posiblemente sea una imagen escaneada sin OCR).")
            
        return texto_extraido
        
    except Exception as e:
        print(f"Error al leer el archivo PDF: {e}")
        raise e


if __name__ == "__main__":
  
    ruta_test = "poliza_ejemplo.pdf" 
    
    try:
        resultado = extraer_texto_pdf(ruta_test)
        print("--- TEXTO EXTRAÍDO CON ÉXITO ---")
        print(resultado[:500]) 
    except Exception as err:
        print(f"No se pudo completar la prueba: {err}")