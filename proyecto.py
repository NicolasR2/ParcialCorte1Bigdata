import boto3
import requests
import datetime

# Configuración de AWS
BUCKET_NAME = "landingcasas211"
s3_client = boto3.client("s3")

def download_html(event, context):
    """Descarga las primeras 10 páginas de mitula y las guarda en S3"""
    base_url = "https://casas.mitula.com.co/find?page={}&operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29"
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    for page in range(1, 11):  # Itera de la página 1 a la 10
        url = base_url.format(page)
        response = requests.get(url)
        
        if response.status_code == 200:
            file_name = f"{today}-page-{page}.html"
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=response.text.encode("utf-8"),
                ContentType="text/html"
            )
            print(f"Guardado en S3: {file_name}")
        else:
            print(f"Error descargando {url}, código {response.status_code}")
    
    return {"message": "Descarga completada"}
