import boto3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

S3_BUCKET_HTML = "landingcasas211"
S3_BUCKET_CSV = "casasfinal211"

s3 = boto3.client("s3")

def process_html(file_name):
    """Procesa un archivo HTML almacenado en S3 y lo convierte en un CSV."""
    print(f"Procesando archivo: {file_name}")
    try:
        response = s3.get_object(Bucket=S3_BUCKET_HTML, Key=file_name)
        html_content = response["Body"].read().decode("utf-8")
        print("HTML descargado correctamente de S3")
    except Exception as e:
        error_msg = f"Error al obtener el archivo de S3: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}

    soup = BeautifulSoup(html_content, "html.parser")
    listings = soup.find_all("div", class_="listing-card__content")
    
    if not listings:
        print("No se encontraron anuncios en el HTML")
        return {"status": "error", "message": "No se encontraron anuncios"}

    data = []
    for listing in listings:
        fecha_descarga = datetime.today().strftime("%Y-%m-%d")

        def extract_text(selector):
            element = listing.select_one(selector)
            return element.text.strip() if element else "N/A"
        
        data.append([
            fecha_descarga,
            extract_text(".title[data-test='snippet__title']"),
            extract_text(".price__actual[data-test='price__actual']"),
            extract_text(".listing-card__location__geo"),
            extract_text("p[data-test='bedrooms']"),
            extract_text("p[data-test='bathrooms']"),
            extract_text("p[data-test='floor-area']"),
        ])
    
    print(f"Se procesaron {len(data)} propiedades")
    
    df = pd.DataFrame(
        data,
        columns=["FechaDescarga", "Titulo", "Precio", "Ubicacion", "Habitaciones", "Banos", "Mts2"],
    )
    print("DataFrame creado con éxito")
    
    csv_file = file_name.replace(".html", ".csv")
    try:
        s3.put_object(Bucket=S3_BUCKET_CSV, Key=csv_file, Body=df.to_csv(index=False))
        print(f"Archivo CSV guardado en S3: {csv_file}")
    except Exception as e:
        error_msg = f"Error al subir el archivo CSV a S3: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}
    
    return {"status": "success", "csv_file": csv_file}

def app(event, context):
    """Función Lambda principal que se activa con eventos S3."""
    print("Evento recibido:", event)
    try:
        file_name = event["Records"][0]["s3"]["object"]["key"]
        print(f"Archivo recibido desde evento S3: {file_name}")
    except (KeyError, IndexError) as e:
        error_msg = f"Error al extraer file_name del evento: {e}"
        print(error_msg)
        return {"status": "error", "message": "Evento S3 mal formado"}
    
    return process_html(file_name)
