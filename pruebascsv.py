import pytest
import pandas as pd
from io import StringIO
from unittest.mock import patch, MagicMock
from proyecto1 import process_html

@pytest.fixture
def test_file_name():
    """Define el nombre del archivo de prueba en S3"""
    return "test_file.html"

@pytest.fixture
def sample_html():
    """Devuelve una muestra de HTML simulada para pruebas"""
    return """
    <div class="listing-card__content">
        <h2 class="title" data-test="snippet__title">Casa en venta</h2>
        <span class="price__actual" data-test="price__actual">$200,000</span>
        <span class="listing-card__location__geo">Bogotá, Colombia</span>
        <p data-test="bedrooms">3 habitaciones</p>
        <p data-test="bathrooms">2 baños</p>
        <p data-test="floor-area">120 m2</p>
    </div>
    """

@pytest.fixture
def mock_s3_client(sample_html):
    """Mock para simular interacciones con S3"""
    mock_s3 = MagicMock()
    
    # Simular la descarga de HTML desde S3
    mock_s3.get_object.return_value = {
        "Body": StringIO(sample_html)
    }

    # Simular la subida de CSV a S3 sin errores
    mock_s3.put_object.return_value = {}

    return mock_s3

@patch("proyecto1.s3")
def test_process_html_s3(mock_s3, test_file_name, mock_s3_client):
    """Prueba el procesamiento de HTML con mock en lugar de llamar a S3 real"""
    mock_s3.get_object.side_effect = mock_s3_client.get_object
    mock_s3.put_object.side_effect = mock_s3_client.put_object

    result = process_html(test_file_name)

    assert result["status"] == "success"
    assert "csv_file" in result
    assert result["csv_file"].endswith(".csv")

@patch("proyecto1.s3")
def test_csv_structure(mock_s3, test_file_name, mock_s3_client):
    """Prueba que el CSV generado tiene las columnas esperadas"""
    mock_s3.get_object.side_effect = mock_s3_client.get_object
    mock_s3.put_object.side_effect = mock_s3_client.put_object

    result = process_html(test_file_name)
    assert result["status"] == "success"

    # Simular la descarga del CSV desde S3
    csv_content = mock_s3_client.get_object()["Body"].getvalue()
    df = pd.read_csv(StringIO(csv_content))

    expected_columns = ["FechaDescarga", "Titulo", "Precio", "Ubicacion", "Habitaciones", "Banos", "Mts2"]
    assert list(df.columns) == expected_columns, f"Columnas incorrectas: {df.columns}"

@patch("proyecto1.s3")
def test_no_multiple_null_or_na_values(mock_s3, test_file_name, mock_s3_client):
    """Prueba que el CSV no tenga más de un valor nulo o 'N/A'"""
    mock_s3.get_object.side_effect = mock_s3_client.get_object
    mock_s3.put_object.side_effect = mock_s3_client.put_object

    result = process_html(test_file_name)
    assert result["status"] == "success"

    csv_content = mock_s3_client.get_object()["Body"].getvalue()
    df = pd.read_csv(StringIO(csv_content))

    null_count = df.isnull().sum().sum()
    na_count = (df == "N/A").sum().sum()
    total_issues = null_count + na_count

    assert total_issues <= 1, f"El CSV tiene más de un valor nulo o 'N/A' ({total_issues} encontrados)"

if __name__ == "__main__":
    pytest.main()
