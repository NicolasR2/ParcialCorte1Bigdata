import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from proyecto1 import process_html


@pytest.fixture
def test_file_name():
    return "test_file.html"


@pytest.fixture
def sample_html():
    """HTML con múltiples anuncios"""
    return (
        """
        <div class="listing-card__content">
            <h2 class="title" data-test="snippet__title">Casa en venta</h2>
            <span class="price__actual" data-test="price__actual">$200,000</span>
            <span class="listing-card__location__geo">Bogotá, Colombia</span>
            <p data-test="bedrooms">3 habitaciones</p>
            <p data-test="bathrooms">2 baños</p>
            <p data-test="floor-area">120 m2</p>
        </div>
        <div class="listing-card__content">
            <h2 class="title" data-test="snippet__title">Apartamento en Medellín</h2>
            <span class="price__actual" data-test="price__actual">$150,000</span>
            <span class="listing-card__location__geo">Medellín, Colombia</span>
            <p data-test="bedrooms">2 habitaciones</p>
            <p data-test="bathrooms">1 baño</p>
            <p data-test="floor-area">80 m2</p>
        </div>
        """
    ).encode("utf-8")  # Se usa `.encode("utf-8")` para soportar tildes


@pytest.fixture
def sample_html_missing_values():
    """HTML con anuncios pero con algunos valores faltantes"""
    return (
        """
        <div class="listing-card__content">
            <h2 class="title" data-test="snippet__title">Casa sin precio</h2>
            <span class="listing-card__location__geo">Bogotá, Colombia</span>
            <p data-test="bedrooms">3 habitaciones</p>
            <p data-test="bathrooms">2 baños</p>
        </div>
        """
    ).encode("utf-8")


@pytest.fixture
def sample_html_empty():
    """HTML sin anuncios"""
    return "<html><body><h1>No Listings</h1></body></html>".encode("utf-8")


@pytest.fixture
def mock_s3_client(sample_html):
    """Mock para simular interacciones con S3"""
    mock_s3 = MagicMock()

    # Simular la descarga de HTML desde S3
    mock_s3.get_object.return_value = {"Body": BytesIO(sample_html)}

    # Simular la subida de CSV sin errores
    mock_s3.put_object.return_value = {}
    return mock_s3


@patch("proyecto1.s3")
def test_process_html_multiple(mock_s3, test_file_name, mock_s3_client):
    """Prueba con múltiples anuncios en el HTML"""
    mock_s3.get_object.side_effect = mock_s3_client.get_object
    mock_s3.put_object.side_effect = mock_s3_client.put_object

    result = process_html(test_file_name)

    assert result["status"] == "success"
    assert "csv_file" in result


@patch("proyecto1.s3")
def test_process_html_missing_values(mock_s3, test_file_name, sample_html_missing_values):
    """Prueba cuando hay valores faltantes en algunos anuncios"""
    mock_s3.get_object.return_value = {"Body": BytesIO(sample_html_missing_values)}
    mock_s3.put_object.return_value = {}

    result = process_html(test_file_name)

    assert result["status"] == "success"


@patch("proyecto1.s3")
def test_process_html_empty(mock_s3, test_file_name, sample_html_empty):
    """Prueba cuando no hay anuncios en el HTML"""
    mock_s3.get_object.return_value = {"Body": BytesIO(sample_html_empty)}

    result = process_html(test_file_name)

    assert result["status"] == "error"
    assert result["message"] == "No se encontraron anuncios"
