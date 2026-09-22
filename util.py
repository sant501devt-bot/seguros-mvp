import shutil
import tempfile
 
 
def ruta_segura_para_upload(ruta_pdf: str) -> str:
    """
    Copia el PDF a un archivo temporal con nombre 100% ASCII.
    Necesario porque client.files.upload() usa el nombre del archivo
    en un encabezado HTTP, y httpx no acepta tildes/ñ ahí (UnicodeEncodeError).
    Devuelve la ruta nueva; el original no se toca.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfile(ruta_pdf, tmp.name)
        return tmp.name