# Task: PDF Binary Processing via FastAPI

## Contexto

Desarrollar un endpoint en una aplicación Python/FastAPI que reciba un JSON con un PDF codificado en Base64, decodifique el contenido a `bytes` y lo pase a un servicio interno para su procesamiento.

---

## Stack Tecnológico

- **Lenguaje:** Python 3.12+
- **Framework:** FastAPI
- **Validación de esquemas:** Pydantic v2

---

## Funcionalidades a Implementar

### 1. Modelo de Request (`controllers/pdf_request.py`)

Crear un modelo Pydantic que represente el cuerpo del request entrante.

**Requisitos:**
- Campo `content` de tipo `str` que contenga el PDF codificado en Base64.
- Validar que `content` no esté vacío.
- Agregar un validador que verifique que el string sea Base64 válido antes de continuar.

**Estructura esperada del JSON de entrada:**
```json
{
  "file_name": "<nombre_del_archivo_en_string>", 
  "content": "<base64_encoded_pdf_string>"
}
```

---

### 2. Decodificación Base64 a Bytes (`utils/pdf_decoder.py`)

Crear una función utilitaria responsable de convertir el campo `content` (Base64 string) a `bytes`.

**Requisitos:**
- Importar el módulo estándar `base64`.
- La función debe recibir el string Base64 y retornar `bytes`.
- Manejar excepciones del tipo `binascii.Error` cuando el string no sea Base64 válido, lanzando un `ValueError` con mensaje descriptivo.
- La función debe ser pura (sin efectos secundarios).

**Firma esperada:**
```python
def decode_pdf_content(content_b64: str) -> bytes:
    ...
```

---

### 3. Servicio de Procesamiento de PDF (`services/pdf_extractor.py`)

Utilizar el servicio services/pdf_extractor.py para obtener el texto del documento pdf.


**Firma del metodo utilizado:**
```python
def extract_pdf_text(pdf_bytes: bytes) -> str:
    ...
```

---

### 4. Endpoint FastAPI (`routers/pdf_router.py`)

Crear el router con el endpoint que orqueste el flujo completo.

**Requisitos:**
- Método HTTP: `POST`
- Path: `/api/v1/pdf/process`
- Recibir el body usando el modelo Pydantic del punto 1.
- Llamar a la función de decodificación del punto 2.
- Pasar los `bytes` resultantes al servicio del punto 3.
- Retornar una respuesta JSON con el resultado del servicio.
- Manejar excepciones con `utils/exceptions.py`:
  - Utilizar rfc 9457 Reference: https://www.rfc-editor.org/rfc/rfc9457.html 

**Respuesta exitosa esperada (ejemplo):**
```json
{
  "status": "ok",
  "message": "PDF procesado correctamente",
  "content": "<texto del pdf>"
}
```

---

### 5. Registro del Router en la Aplicación (`main.py`)

Integrar el router creado en la aplicación FastAPI principal.

**Requisitos:**
- Instanciar `FastAPI()`.
- Incluir el router con `app.include_router(...)`.
- Configurar `title`, `version` y `description` en la instancia de FastAPI.

---

## Estructura de Archivos Esperada

```
app/
├── main.py
├── routers/
│   └── pdf_router.py
├── controllers/
│   └── pdf_request.py
├── services/
│   └── pdf_service.py
└── utils/
    └── pdf_decoder.py
```

---

## Criterios de Aceptación

- [ ] El endpoint acepta un JSON con el campo `content` en Base64.
- [ ] El campo `content` es decodificado correctamente a `bytes` usando `base64.b64decode`.
- [ ] Si el Base64 es inválido, se retorna `rfc 9457` con mensaje de error claro.
- [ ] Los `bytes` son pasados al servicio sin que este conozca el request HTTP.
- [ ] El endpoint retorna `HTTP 200` con un JSON con el texto extraido del pdf.
- [ ] Toda la lógica de decodificación está separada del router.
- [ ] El código incluye type hints en todas las funciones.

---

## Notas Técnicas

- Usar `base64.b64decode(content, validate=True)` para una decodificación estricta.
- El módulo `binascii` (estándar de Python) expone `binascii.Error` para capturar Base64 malformado.
- FastAPI con Pydantic v2 valida automáticamente el body; los validadores de campo se declaran con `@field_validator`.
- No instalar dependencias externas para el parsing Base64; usar únicamente la librería estándar de Python.
