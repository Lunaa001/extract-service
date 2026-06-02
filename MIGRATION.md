# Migración de Extracción de PDFs - Documentación

## Resumen de Cambios

Se ha completado la migración de la funcionalidad de extracción de texto de PDFs desde el monolítico **NotebookUM** hacia el microservicio **extract-service**.

### Cambio Principal: Algoritmo de Extracción

**Antes**: docling (versión 2.85.0)  
**Ahora**: pdfplumber + Tesseract OCR

## Cambios en `extract-service`

### 1. Dependencias (pyproject.toml)

```toml
# Eliminado:
- "docling==2.85.0"

# Agregado:
- "pdfplumber>=0.10.0"
- "pytesseract>=0.3.10"
- "pdf2image>=1.17.0"
- "Pillow>=10.0.0"
```

### 2. Servicio de Extracción (app/services/pdf_extractor.py)

Reemplazado completamente con la implementación de NotebookUM:

**Funciones:**
- `validate_pdf(file_content: bytes) -> bool`: Valida firma PDF
- `extract_pdf_text(pdf_bytes: bytes, max_pages: Optional[int]) -> str`: Extrae texto con OCR fallback
- `extract_metadata(pdf_bytes: bytes) -> dict`: Extrae metadatos
- `_extract_text_with_ocr(pdf_bytes: bytes, page_num: int) -> str`: Tesseract OCR

**Cambio**: Ahora trabaja con bytes en memoria (BytesIO) en lugar de archivos en disco.

### 3. Modelo de Request (app/controllers/pdf_request.py)

Agregado parámetro opcional:

```python
max_pages: int | None = Field(default=None, ge=1)
```

### 4. Router (app/routers/pdf_router.py)

- Actualizado `/api/v1/pdf/process` para usar `max_pages`
- Agregado endpoint `/api/v1/pdf/metadata` para extraer metadatos

### 5. Dockerfile

Agregadas dependencias de sistema necesarias:

```dockerfile
RUN apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libtesseract-dev
```

### 6. Tests (tests/test_pdf_extractor.py)

Completamente reescritos para:
- Validar funcionalidad de pdfplumber + Tesseract
- Usar PDFs reales de tests/docs/
- Agregar tests de validación, metadatos y OCR

## Cambios en NotebookUM

### 1. Dependencias (pyproject.toml)

```toml
# Eliminado (ahora en extract-service):
- "pdfplumber>=0.10.0"
- "pytesseract>=0.3.10"
- "pdf2image>=1.17.0"
- "pillow>=10.0.0"

# Mantenido:
- "requests>=2.33.1"  # Para llamar al microservicio
```

### 2. Configuración (config.py)

Agregada variable de entorno:

```python
EXTRACT_SERVICE_URL: str = Field(default="http://extract-service:8000")
```

### 3. Servicio de Extracción (app/services/pdf_extraction_service.py)

Transformado en cliente HTTP del microservicio:

```python
class PDFExtractionService:
    EXTRACT_PROCESS_ENDPOINT = f"{settings.EXTRACT_SERVICE_URL}/api/v1/pdf/process"
    EXTRACT_METADATA_ENDPOINT = f"{settings.EXTRACT_SERVICE_URL}/api/v1/pdf/metadata"
    
    @staticmethod
    def extract_text(file_path: str, max_pages: Optional[int]) -> str:
        # Lee el PDF localmente
        # Codifica a base64
        # Envía al microservicio
        # Retorna el texto extraído
```

**API de la clase sigue siendo idéntica** - No se requieren cambios en los controladores.

### 4. Dockerfile

Removidas dependencias de Tesseract (ahora en extract-service):

```dockerfile
# Eliminado:
# - tesseract-ocr
# - libtesseract-dev
# - imagemagick
```

## Flujo de Procesamiento

```
NotebookUM (POST /documents/upload)
    ↓
    1. Valida PDF localmente
    2. Lee archivo PDF
    3. Codifica a Base64
    ↓
extract-service (POST /api/v1/pdf/process)
    ↓
    4. Decodifica Base64
    5. Valida PDF
    6. Extrae con pdfplumber
    7. OCR con Tesseract si es necesario
    8. Retorna texto
    ↓
NotebookUM
    ↓
    9. Almacena en BD
    10. Retorna respuesta al cliente
```

## Validación de Funcionalidad

### 1. Tests en extract-service

```bash
cd extract-service
python -m pytest tests/test_pdf_extractor.py -v
python -m pytest tests/test_pdf_router.py -v
```

### 2. Tests en NotebookUM

Los tests existentes en `tests/test_docling_integration.py` deben actualizarse para usar el nuevo cliente.

### 3. Test Manual

```bash
# Iniciar extract-service
docker run -p 8000:8000 extract-service:latest

# En otra terminal, desde NotebookUM
python -c "
from app.services.pdf_extraction_service import PDFExtractionService
import os

# Probar con un PDF real
pdf_path = 'test_pdf.pdf'
if os.path.exists(pdf_path):
    text = PDFExtractionService.extract_text(pdf_path, max_pages=2)
    print('Texto extraído:', text[:100], '...')
    
    metadata = PDFExtractionService.extract_metadata(pdf_path)
    print('Metadatos:', metadata)
"
```

## Variables de Entorno

### NotebookUM

```bash
EXTRACT_SERVICE_URL=http://extract-service:8000  # Para producción en Docker
# O para desarrollo local:
EXTRACT_SERVICE_URL=http://localhost:8000
```

### extract-service

```bash
LOG_LEVEL=INFO
TESSERACT_CMD=/usr/bin/tesseract  # Si no está en PATH
```

## Rollback (si es necesario)

Si necesitas volver a la versión anterior basada en docling:

1. En extract-service:
   ```bash
   git checkout HEAD~ app/services/pdf_extractor.py pyproject.toml
   ```

2. En NotebookUM:
   ```bash
   git checkout HEAD~ app/services/pdf_extraction_service.py pyproject.toml config.py
   ```

3. Actualizar dependencias y ejecutar tests

## Beneficios de la Migración

✅ **Separación de responsabilidades**: Extracción de PDFs en microservicio dedicado  
✅ **Escalabilidad**: extract-service puede escalar independientemente  
✅ **Mantenibilidad**: Lógica de extracción centralizada  
✅ **Compatibilidad**: API idéntica en NotebookUM, sin cambios en controladores  
✅ **Performance**: OCR y extracción optimizados  
✅ **Robusto**: RFC 9457 Problem Details para manejo de errores  

## Notas Importantes

1. **El microservicio es ahora esencial** - NotebookUM requiere que extract-service esté corriendo para procesar PDFs
2. **Timeout recomendado**: 60s para extract_text (OCR puede ser lento)
3. **Máximo de páginas**: Recomendado max_pages=10 para no sobrecargar
4. **OCR en paralelo**: Para futuras mejoras, se puede paralelizar OCR en múltiples procesos
5. **Caché**: Considerar agregar Redis para cachear resultados de extracción

## Contacto / Soporte

Para problemas de integración, verificar:
- Logs de extract-service: `docker logs extract-service`
- Logs de NotebookUM: `docker logs notebookum`
- Conectividad: `curl -X POST http://extract-service:8000/api/v1/pdf/process`
