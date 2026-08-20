"""
utils.py — Módulo Agentes IA
Configuración central: base URL, auth, helpers de request.
Importado por todos los test_*.py de este módulo.

Rutas confirmadas (capturadas en Chrome Network, 2026-08-05):
  ✅ /connection/status
  ✅ /conversations
  ✅ /labels
  ✅ /notification-actions      (query: ?agentId=<id>)
  ✅ /predefined-messages
  ✅ /templates
  ✅ /templates/{id}/status

Rutas esperadas (no confirmadas — bloqueadas por BUG-001 PHONE_REGISTER_FAILED):
  ⏳ /webhook                   (POST — entrada de Meta)
  ⏳ /conversations/{id}
  ⏳ /conversations/{id}/messages
  ⏳ /conversations/{id}/assign
  ⏳ /conversations/{id}/notes
  ⏳ /conversations/{id}/status
  ⏳ /conversations/{id}/block
  ⏳ /conversations/{id}/labels
  ⏳ /conversations/{id}/export
  ⏳ /templates (POST)
  ⏳ /automations
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── Configuración ────────────────────────────────────────────────────────────
AI_API_BASE    = os.getenv("AI_BASE_URL", "https://ai-qa.api.mastershop.com") + "/api/v1/ai"
AI_TOKEN       = os.getenv("AI_BEARER_TOKEN")
AI_AUTH_ID     = os.getenv("AI_AUTH_ID")
AI_BUSINESS    = os.getenv("AI_ID_BUSINESS")
AI_BUSINESS_B  = os.getenv("AI_ID_BUSINESS_B", "99999")  # negocio ajeno (para CT016 / CT009-E2)

DEFAULT_TIMEOUT = 15  # segundos

# ─── Paths confirmados ✅ ─────────────────────────────────────────────────────
CONNECTION_STATUS   = "/connection/status"
CONVERSATIONS       = "/conversations"
LABELS              = "/labels"
NOTIFICATION_ACTIONS = "/notification-actions"   # ?agentId=<id>
PREDEFINED_MESSAGES = "/predefined-messages"
TEMPLATES           = "/templates"               # GET list / POST create
# TEMPLATES/{id}/status → construir con f"{TEMPLATES}/{uuid}/status"

# ─── Paths esperados ⏳ (bloqueados por BUG-001) ──────────────────────────────
WEBHOOK             = "/webhook"                 # POST — entrada Meta
# /conversations/{id}  → construir con f"{CONVERSATIONS}/{conv_id}"
# /conversations/{id}/messages, /assign, /notes, /status, /block, /labels, /export


# ─── Auth ─────────────────────────────────────────────────────────────────────
def auth_headers(token: str = None, business: str = None) -> dict:
    """
    Retorna los headers de autenticación.
    Pasa token="invalido" para simular token malo.
    Pasa business=AI_BUSINESS_B para simular otro negocio (multi-tenant).
    """
    return {
        "Authorization": f"Bearer {token or AI_TOKEN}",
        "x-auth-id":     AI_AUTH_ID,
        "x-idbusiness":  business or AI_BUSINESS,
        "Content-Type":  "application/json",
    }


def headers_otro_negocio() -> dict:
    """Headers con el negocio B — para pruebas de aislamiento multi-tenant."""
    return auth_headers(business=AI_BUSINESS_B)


# ─── Helpers de request ───────────────────────────────────────────────────────
def get_ai(path: str, params: dict = None, headers: dict = None) -> requests.Response:
    """GET a AI_API_BASE + path."""
    url = f"{AI_API_BASE}{path}"
    return requests.get(url, params=params, headers=headers or auth_headers(), timeout=DEFAULT_TIMEOUT)


def post_ai(path: str, json: dict = None, headers: dict = None) -> requests.Response:
    """POST a AI_API_BASE + path."""
    url = f"{AI_API_BASE}{path}"
    return requests.post(url, json=json, headers=headers or auth_headers(), timeout=DEFAULT_TIMEOUT)


# ─── Factories de payload ─────────────────────────────────────────────────────
def webhook_texto(wamid: str, telefono: str, texto: str) -> dict:
    """
    Payload estándar de webhook entrante de Meta.
    wamid es el ID único del mensaje (base de la idempotencia).
    """
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id":        wamid,
                        "from":      telefono,
                        "type":      "text",
                        "timestamp": "1700000000",
                        "text":      {"body": texto}
                    }],
                    "contacts": [{
                        "profile": {"name": "Cliente QA"},
                        "wa_id":   telefono
                    }]
                }
            }]
        }]
    }


# ─── Validación de config al importar ────────────────────────────────────────
def verificar_config():
    """Lanza error si falta alguna variable crítica en .env"""
    faltantes = [k for k, v in {
        "AI_BEARER_TOKEN": AI_TOKEN,
        "AI_AUTH_ID":      AI_AUTH_ID,
        "AI_ID_BUSINESS":  AI_BUSINESS,
    }.items() if not v]
    assert not faltantes, f"Faltan variables en .env: {faltantes}"
