import boto3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

S3_BUCKET_HTML = "landingcasas211"
S3_BUCKET_CSV = "casasfinal211"

s3 = boto3.client("s3")


def process_html(file_name):
    print(f"Procesando archivo: {file_name}")

    try:
        response = s3.get_object(Bucket=S3_BUCKET_HTML, Key=file_name)
        html_content = response["Body"].read().decode("utf-8")
        print("HTML descargado correctamente de S3")
    except Exception as e:
        print(f"Error al obtener el archivo de S3: {e}")
        return {"status": "error", "message": f"Error al obtener HTML: {e}"}

    soup = BeautifulSoup(html_content, "html.parser")
    print("HTML parseado con BeautifulSoup")

    listings = soup.find_all("div", class_="listing-card__content")
    if not listings:
        print("No se encontraron anuncios en el HTML")
        return {"status": "error", "message": "No se encontraron anuncios"}

    data = []
    for listing in listings:
        fecha_descarga = datetime.today().strftime("%Y-%m-%d")

        titulo = listing.select_one(".title[data-test='snippet__title']")
        titulo = titulo.text.strip() if titulo else "N/A"

        precio = listing.select_one(".price__actual[data-test='price__actual']")
        precio = precio.text.strip() if precio else "N/A"

        ubicacion = listing.select_one(".listing-card__location__geo")
        ubicacion = ubicacion.text.strip() if ubicacion else "N/A"

        habitaciones = listing.select_one("p[data-test='bedrooms']")
        habitaciones = habitaciones.text.strip() if habitaciones else "N/A"

        banos = listing.select_one("p[data-test='bathrooms']")
        banos = banos.text.strip() if banos else "N/A"

        mts2 = listing.select_one("p[data-test='floor-area']")
        mts2 = mts2.text.strip() if mts2 else "N/A"

        data.append(
            [fecha_descarga, titulo, precio, ubicacion, habitaciones, banos, mts2]
        )

    print(f"Se procesaron {len(data)} propiedades")

    df = pd.DataFrame(
        data,
        columns=["FechaDescarga", "Titulo", "Precio", "Ubicacion",
                 "Habitaciones", "Banos", "Mts2"],
    )
    print("DataFrame creado con éxito")

    csv_file = file_name.replace(".html", ".csv")
    try:
        s3.put_object(
            Bucket=S3_BUCKET_CSV, Key=csv_file, Body=df.to_csv(index=False)
        )
        print(f"Archivo CSV guardado en S3: {csv_file}")
    except Exception as e:
        print(f"Error al subir el archivo CSV a S3: {e}")
        return {"status": "error", "message": f"Error al subir CSV: {e}"}

    return {"status": "success", "csv_file": csv_file}

def app(event, context):
    print("Evento recibido:", event)
    try:
        file_name = event["Records"][0]["s3"]["object"]["key"]
        print(f"Archivo recibido desde evento S3: {file_name}")
    except (KeyError, IndexError) as e:
        print(f"Error al extraer file_name del evento: {e}")
        return {"status": "error", "message": "Evento S3 mal formado"}

    return process_html(file_name)