# Orbyn Lead Bot

Bot de Telegram para recibir leads, analizarlos, calificarlos contra un ICP y guardar el resultado en Google Sheets.

## Que hace

El bot recibe un mensaje de texto con informacion de un lead y responde si el lead esta cualificado o no.

Tambien guarda cada lead procesado en Google Sheets con:

- fecha y hora
- texto recibido
- decision
- motivo

## Flujo

```txt
Telegram recibe mensaje
↓
LLM o modo mock extrae datos del lead
↓
Python aplica reglas de calificacion
↓
Telegram responde al usuario
↓
Apps Script guarda el resultado en Google Sheets
```

## Tecnologias usadas

- Python
- python-telegram-bot
- python-dotenv
- Google Gemini API con `google-genai`
- Requests para enviar datos al Web App de Google Apps Script
- Google Sheets mediante Google Apps Script

## Estructura del proyecto

```txt
main.py
models/
  lead.py
services/
  llm_service.py
  qualifier_service.py
  sheets_service.py
skills/
requirements.txt
.env.example
```

## Archivos principales

### `main.py`

Inicializa el bot de Telegram, registra los handlers y maneja los mensajes.

No contiene logica de Google Sheets ni reglas de calificacion. Solo coordina el flujo:

```txt
mensaje -> analyze_lead -> responder -> log_lead
```

### `services/llm_service.py`

Extrae informacion desde el texto recibido.

Soporta dos modos:

- `LLM_PROVIDER=mock`: no llama a ningun proveedor externo y usa reglas locales simples.
- `LLM_PROVIDER=gemini`: intenta usar Gemini. Si falla, usa fallback local.

Devuelve siempre el mismo formato final:

```python
{
    "company_type": "...",
    "employees": 12,
    "location": "...",
    "interest": "...",
    "qualified": True,
    "reason": "..."
}
```

### `models/lead.py`

Define el modelo `Lead`.

Sirve para ordenar los datos extraidos antes de aplicar las reglas de calificacion.

### `services/qualifier_service.py`

Aplica las reglas ICP en Python.

Un lead califica si cumple:

- empresa de servicios o consultoria
- minimo 5 empleados
- Espana o Latinoamerica
- interes en automatizacion o IA

### `services/sheets_service.py`

Envia el resultado a Google Apps Script usando un POST.

El payload enviado es:

```json
{
  "fecha": "2026-05-29 18:00:00",
  "lead_recibido": "texto original",
  "decision": "Cualificado",
  "motivo": "motivo de la decision"
}
```

Si Google Sheets o Apps Script fallan, el bot igual responde al usuario y muestra el error en consola.

## Configuracion

Crear un archivo `.env` basado en `.env.example`:

```env
TELEGRAM_BOT_TOKEN=
GEMINI_API_KEY=

LLM_PROVIDER=mock
GEMINI_MODEL=gemini-2.0-flash-lite

GOOGLE_APPS_SCRIPT_URL=
```

### Variables

`TELEGRAM_BOT_TOKEN`

Token del bot creado en BotFather.

`GEMINI_API_KEY`

API key de Gemini. Solo se usa si `LLM_PROVIDER=gemini`.

`LLM_PROVIDER`

Proveedor de analisis del lead.

Valores disponibles:

- `mock`: recomendado para pruebas, no consume cuota.
- `gemini`: usa Gemini y fallback local si falla.

`GEMINI_MODEL`

Modelo de Gemini a usar. Por defecto:

```env
GEMINI_MODEL=gemini-2.0-flash-lite
```

`GOOGLE_APPS_SCRIPT_URL`

URL del Web App publicado en Google Apps Script.

## Google Apps Script

El bot no escribe directo en Google Sheets con service account.

En su lugar, envia un POST a un Web App de Apps Script. Ese script debe recibir el JSON y agregar una fila en la hoja.

Ejemplo basico de Apps Script:

```javascript
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    data.fecha,
    data.lead_recibido,
    data.decision,
    data.motivo
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

Despues de publicar el script como Web App, copiar la URL `/exec` en `GOOGLE_APPS_SCRIPT_URL`.

## Instalacion

```powershell
python -m pip install -r requirements.txt
```

## Como correr el bot

```powershell
python main.py
```

Luego escribirle al bot por Telegram.

## Ejemplos para probar

Lead cualificado:

```txt
Somos una consultoria de automatizacion en Uruguay con 12 empleados y queremos implementar IA.
```

Lead no cualificado:

```txt
Tengo una tienda en Estados Unidos con 3 empleados y quiero una web.
```

## Seguridad

No subir `.env` ni credenciales reales al repositorio.

El proyecto incluye `.gitignore` para ignorar:

- `.env`
- `__pycache__/`
- `*.pyc`
- archivos de credenciales JSON

## Estado actual

- Telegram funcionando.
- Modo mock funcionando.
- Calificacion por reglas Python funcionando.
- Logging a Google Sheets via Apps Script funcionando.
- Gemini queda opcional y puede usarse cuando haya cuota disponible.
