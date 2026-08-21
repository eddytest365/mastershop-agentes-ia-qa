"""
test_notificaciones.py — Etapa 2: Acciones de Notificación del Agente
Cubre smoke tests del endpoint notification-actions (confirmado en /ai/agentes/logistics).

CT010_FT_AutomatizacionesSeguimientoSinRespuestaYSaludoInicial (parcial)

Endpoint confirmado:
  GET /api/v1/ai/notification-actions?agentId=<id>
"""

import requests
import pytest
from utils import (
    AI_API_BASE, DEFAULT_TIMEOUT,
    auth_headers, headers_otro_negocio, get_ai,
    NOTIFICATION_ACTIONS,
)

# ID del agente conocido (observado en Chrome: agentId=logistics)
AGENT_ID_LOGISTICS = "logistics"


# ─── CT010 — Notification actions (smoke) ────────────────────────────────────

def test_ct010_notification_actions_logistics_retorna_respuesta():
    """
    CT010 — GET /notification-actions?agentId=logistics retorna respuesta válida.
    Ruta confirmada en Chrome al navegar a /ai/agentes/logistics.
    """
    r = get_ai(NOTIFICATION_ACTIONS, params={"agentId": AGENT_ID_LOGISTICS})
    assert r.status_code in (200, 404), (
        f"notification-actions retornó {r.status_code}: {r.text[:200]}"
    )


def test_ct010_notification_actions_es_json():
    """CT010 — /notification-actions devuelve JSON parseable."""
    r = get_ai(NOTIFICATION_ACTIONS, params={"agentId": AGENT_ID_LOGISTICS})
    if r.status_code == 404:
        pytest.skip("Agent logistics no disponible en este entorno")
    assert r.status_code == 200
    try:
        datos = r.json()
    except Exception:
        pytest.fail("La respuesta de /notification-actions no es JSON válido")
    assert datos is not None


def test_ct010_notification_actions_sin_agentid_no_da_500():
    """CT010 — Llamar /notification-actions sin agentId no debe dar 500."""
    r = get_ai(NOTIFICATION_ACTIONS)
    assert r.status_code != 500, (
        f"Sin agentId causó 500: {r.text[:200]}"
    )


def test_ct010_notification_actions_negocio_ajeno_rechazado():
    """CT010 / CT009 — /notification-actions con negocio ajeno devuelve 401 o 403."""
    r = requests.get(
        f"{AI_API_BASE}{NOTIFICATION_ACTIONS}",
        headers=headers_otro_negocio(),
        params={"agentId": AGENT_ID_LOGISTICS},
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code in (401, 403), (
        f"Cross-tenant en /notification-actions no bloqueado. Status: {r.status_code}"
    )


def test_ct010_notification_actions_sin_token_rechazado():
    """CT010 / CT009 — /notification-actions sin token devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    r = requests.get(
        f"{AI_API_BASE}{NOTIFICATION_ACTIONS}",
        headers=headers,
        params={"agentId": AGENT_ID_LOGISTICS},
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code == 401
