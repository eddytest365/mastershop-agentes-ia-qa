"""
test_conexion.py — Etapa 1: Conexión y Configuración
Cubre CT006_SEC_TokenOAuthExpiradoYRefresh (parcial, via connection/status)
y smoke test del módulo.

Endpoint confirmado: GET /api/v1/ai/connection/status
"""

import requests
import pytest
from utils import (
    AI_API_BASE, DEFAULT_TIMEOUT,
    auth_headers, get_ai,
    CONNECTION_STATUS,
)


# ─── CT006 — Token expirado / inválido devuelve 401 ──────────────────────────

def test_ct006_token_expirado_es_rechazado():
    """
    CT006_SEC — Si el token es inválido/expirado, el endpoint devuelve 401.
    Simula expiración usando un token sintético fuera de formato.
    """
    headers = auth_headers(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expirado.invalido")
    respuesta = requests.get(
        f"{AI_API_BASE}{CONNECTION_STATUS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code == 401, (
        f"Se esperaba 401 con token expirado, se obtuvo {respuesta.status_code}"
    )


def test_ct006_sin_token_es_rechazado():
    """CT006_SEC — Sin header Authorization el endpoint devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    respuesta = requests.get(
        f"{AI_API_BASE}{CONNECTION_STATUS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code == 401, (
        f"Se esperaba 401 sin token, se obtuvo {respuesta.status_code}"
    )


# ─── Smoke test de conexión ───────────────────────────────────────────────────

def test_connection_status_responde():
    """
    Smoke test: GET /connection/status responde (2xx o el 4xx del BUG-001).
    Verifica que el endpoint existe y retorna JSON.
    PHONE_REGISTER_FAILED da 200/400 — cualquiera es válido acá; lo importante
    es que la ruta resuelve y responde JSON.
    """
    respuesta = get_ai(CONNECTION_STATUS)
    assert respuesta.status_code in (200, 400, 422), (
        f"Se esperaba respuesta conocida, se obtuvo {respuesta.status_code}: "
        f"{respuesta.text[:200]}"
    )
    # Debe responder JSON
    try:
        respuesta.json()
    except Exception:
        pytest.fail("La respuesta no es JSON válido")


def test_connection_status_body_tiene_estructura():
    """
    El cuerpo de connection/status debe tener al menos una clave (no vacío).
    Registra el estado real en caso de BUG-001.
    """
    respuesta = get_ai(CONNECTION_STATUS)
    cuerpo = respuesta.json()
    assert isinstance(cuerpo, dict), "Se esperaba un objeto JSON"
    assert len(cuerpo) > 0, f"Respuesta vacía: {cuerpo}"
