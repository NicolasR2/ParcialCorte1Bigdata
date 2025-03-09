import pytest
import pandas as pd
import boto3
from io import StringIO
from proyecto1 import process_html, S3_BUCKET_CSV  # Reemplaza 'your_module' con el nombre real de tu módulo

@pytest.fixture
def test_file_name():
    """Define el nombre del archivo de prueba en S3"""
    return "test_file.html"  # Asegúrate de que este archivo existe en S3

def test_process_html_s3(test_file_name):
    """Prueba que el procesamiento de HTML desde S3 se ejecuta correctamente"""
    result = process_html(test_file_name)
    
    assert result["status"] == "success"
    assert "csv_file" in result  # Se generó un CSV
    assert result["csv_file"].endswith(".csv")  # El archivo generado es CSV

def test_csv_structure(test_file_name):
    """Prueba que el CSV generado tiene las columnas esperadas"""
    result = process_html(test_file_name)
    assert result["status"] == "success"
    
    # Descargar el CSV de S3 para verificarlo
    s3 = boto3.client("s3")
    csv_file = result["csv_file"]
    response = s3.get_object(Bucket=S3_BUCKET_CSV, Key=csv_file)
    
    # Leer el CSV en un DataFrame de pandas
    df = pd.read_csv(StringIO(response["Body"].read().decode("utf-8")))
    
    # Columnas esperadas
    expected_columns = ["FechaDescarga", "Titulo", "Precio", "Ubicacion", "Habitaciones", "Banos", "Mts2"]
    assert list(df.columns) == expected_columns, f"Columnas incorrectas: {df.columns}"

def test_no_multiple_null_or_na_values(test_file_name):
    """Prueba que el CSV no tenga más de un valor nulo o 'N/A'"""
    result = process_html(test_file_name)
    assert result["status"] == "success"
    
    # Descargar el CSV de S3 para verificarlo
    s3 = boto3.client("s3")
    csv_file = result["csv_file"]
    response = s3.get_object(Bucket=S3_BUCKET_CSV, Key=csv_file)
    
    # Leer el CSV en un DataFrame de pandas
    df = pd.read_csv(StringIO(response["Body"].read().decode("utf-8")))

    # Contar valores nulos y 'N/A'
    null_count = df.isnull().sum().sum()
    na_count = (df == "N/A").sum().sum()
    total_issues = null_count + na_count

    # Si hay más de un valor nulo o 'N/A', la prueba debe fallar
    assert total_issues <= 1, f"El CSV tiene más de un valor nulo o 'N/A' ({total_issues} encontrados)"

if __name__ == "__main__":  # No es obligatorio, pero permite ejecutar con 'pytest'
    pytest.main()
