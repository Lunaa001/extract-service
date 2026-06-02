# Extract Text Service - Microservicio de Extracción de PDFs

Microservicio especializado en la extracción de texto de archivos PDF con soporte para:
- **Extracción de texto embebido**: Usando pdfplumber (rápido)
- **OCR**: Usando Tesseract para PDFs escaneados o sin texto embebido
- **Multiidioma**: Soporte para español e inglés

## Características

- Extracción de texto de PDFs con fallback automático a OCR
- Extracción de metadatos del PDF (número de páginas, título)
- Validación de firmas PDF
- Límite configurable de páginas a procesar
- Manejo robusto de errores con RFC 9457 Problem Details
- Base64 decoding para transferencia segura

## Requisitos

- Python 3.12+
- Tesseract OCR instalado en el sistema
- Poppler utilities para conversión de PDF a imagen

### Dependencias del Sistema (Docker incluye esto)

```bash
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-cpp-dev
```

## Instalación y Ejecución

### Local

```bash
# Crear ambiente virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
# O usando uv:
uv pip install -e .

# Ejecutar servidor
uvicorn main:app --reload --port 8000
```

### Docker

```bash
# Construir imagen
docker build -t extract-service:latest .

# Ejecutar contenedor
docker run -p 8000:8000 extract-service:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## API Endpoints

### POST `/api/v1/pdf/process`

Extrae texto de un PDF enviado en base64.

**Request:**
```json
{
  "file_name": "documento.pdf",
  "content": "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo...",
  "max_pages": 10
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "PDF procesado correctamente",
  "content": "--- Page 1 ---\nTexto extraído del PDF...\n"
}
```

**Parámetros:**
- `file_name` (string, required): Nombre del archivo PDF
- `content` (string, required): Contenido del PDF en base64
- `max_pages` (integer, optional): Máximo número de páginas a procesar

### POST `/api/v1/pdf/metadata`

Extrae metadatos del PDF.

**Request:**
```json
{
  "file_name": "documento.pdf",
  "content": "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo..."
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Metadatos extraídos correctamente",
  "metadata": {
    "num_pages": 5,
    "title": "Unknown",
    "format": "PDF"
  }
}
```

## Códigos de Error

| Status | Descripción |
|--------|-----------|
| 400 | PDF inválido o base64 malformado |
| 500 | Error interno del servidor |

### Ejemplo Error (RFC 9457)

```json
{
  "type": "https://notebookum.com/problems/invalid-pdf",
  "title": "Invalid PDF File",
  "status": 400,
  "detail": "File must be a valid PDF (invalid PDF signature)",
  "instance": "/api/v1/pdf/process"
}
```

## Integración con NotebookUM

El monolítico NotebookUM usa este servicio automáticamente. La configuración se realiza en `config.py`:

```python
EXTRACT_SERVICE_URL = "http://extract-service:8000"
```

Ejemplo de uso en controllers:

```python
from app.services.pdf_extraction_service import PDFExtractionService

# Extraer texto
texto = PDFExtractionService.extract_text("/ruta/al/pdf.pdf", max_pages=10)

# Extraer metadatos
metadata = PDFExtractionService.extract_metadata("/ruta/al/pdf.pdf")
```

## Testing

```bash
# Ejecutar tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

## Variables de Entorno

```
# Configuración de logging
LOG_LEVEL=INFO

# Tesseract (si no está en PATH del sistema)
TESSERACT_CMD=/usr/bin/tesseract
```

## Rendimiento

- Extracción de texto embebido: ~0.1-0.5s por página
- OCR (Tesseract): ~1-3s por página
- Máximo recomendado: 10 páginas por request

## Troubleshooting

### Error: "tesseract is not installed"

Instala Tesseract:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# Windows
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

### Error: "poppler is not installed"

```bash
# macOS
brew install poppler

# Ubuntu/Debian
apt-get install poppler-utils

# Windows
# Descargar desde: https://github.com/oschwartz10612/poppler-windows/releases/
```

### Error de timeout

Aumenta el límite de páginas o reduce `max_pages`:
```python
PDFExtractionService.extract_text(pdf_path, max_pages=5)
```

## Arquitectura

```
extract-service/
├── app/
│   ├── services/
│   │   └── pdf_extractor.py      # Lógica de extracción (pdfplumber + Tesseract)
│   ├── controllers/
│   │   └── pdf_request.py        # Modelo de request
│   ├── routers/
│   │   └── pdf_router.py         # Endpoints HTTP
│   ├── models/
│   ├── utils/
│   │   ├── exceptions.py         # Excepciones RFC 9457
│   │   └── pdf_decoder.py        # Base64 decoding
│   └── __init__.py
├── tests/
│   ├── test_pdf_extractor.py     # Tests de extracción
│   ├── test_pdf_router.py        # Tests de API
│   └── docs/                     # PDFs de prueba
├── main.py                        # Punto de entrada
├── pyproject.toml                 # Dependencias
├── Dockerfile                     # Configuración Docker
└── docker-compose.yml             # Orquestación
```

## Licencia

MIT
