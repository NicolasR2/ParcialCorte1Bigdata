import boto3
import requests
import datetime
import logging

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de AWS
BUCKET_NAME = "landingcasas211"
s3_client = boto3.client("s3")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.google.com/",
}


def app(event, context):
    """Descarga las primeras 10 páginas de mitula y las guarda en S3."""
    base_url = (
        "https://casas.mitula.com.co/find?page={}&operationType=sell&"
        "propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-"
        "0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29"
    )
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    for page in range(1, 11):  # Itera de la página 1 a la 10
        url = base_url.format(page)
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Lanza una excepción si el código no es 200

            file_name = f"{today}-page-{page}.html"
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=response.text.encode("utf-8"),
                ContentType="text/html",
            )
            logger.info(f"Guardado en S3: {file_name}")

        except requests.RequestException as e:
            logger.error(f"Error descargando {url}: {e}")

    return {"message": "Descarga completada"}
