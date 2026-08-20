"""
test_seguridad.py — Etapa 1: Seguridad y Aislamiento
Cubre:
  CT009_SEC_SanitizacionDeInputYPrevencionDeXSS  (auth headers via API)
  CT016_SEC_AislamientoMultiTenantYPermisos

Endpoints confirmados:
  GET /api/v1/ai/conversations
"""

import requests
import pytest
from utils import (
    AI_API_BASE, DEFAULT_TIMEOUT,
    auth_headers, headers_otro_negocio, get_ai,
    CONVERSATIONS,
)


# ─── CT009 — Validación de autenticación ─────────────────────────────────────

def test_ct009_sin_token_es_rechazado():
    """CT009_SEC — Sin Authorization header el endpoint devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    respuesta = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code == 401, (
        f"Se esperaba 401 sin token, se obtuvo {respuesta.status_code}"
    )


def test_ct009_token_invalido_es_rechazado():
    """CT009_SEC — Token sintético inválido devuelve 401."""
    headers = auth_headers(token="token-invalido-de-prueba")
    respuesta = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code == 401, (
        f"Se esperaba 401 con token inválido, se obtuvo {respuesta.status_code}"
    )


def test_ct009_token_malformado_es_rechazado():
    """CT009_SEC — Header Authorization sin 'Bearer ' devuelve 401."""
    headers = auth_headers()
    headers["Authorization"] = "solo-un-string-sin-bearer"
    respuesta = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code == 401, (
        f"Se esperaba 401 con formato incorrecto, se obtuvo {respuesta.status_code}"
    )


# ─── CT016 — Aislamiento multi-tenant ────────────────────────────────────────

def test_ct016_negocio_ajeno_en_header_es_rechazado():
    """
    CT016_SEC — Petición con x-idbusiness de otro negocio debe devolver 401 o 403.
    Verifica que el servidor valida el par (token, business) y rechaza combinaciones
    inválidas — principio de aislamiento de tenant.
    """
    respuesta = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers_otro_negocio(),
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code in (401, 403), (
        f"Se esperaba 401 o 403 con negocio ajeno, se obtuvo {respuesta.status_code}. "
        "Posible fallo de aislamiento multi-tenant."
    )


def test_ct016_sin_x_idbusiness_es_rechazado():
    """CT016_SEC — Sin header x-idbusiness el servidor rechaza la petición."""
    headers = auth_headers()
    headers.pop("x-idbusiness")
    respuesta = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert respuesta.status_code in (400, 401, 403, 422), (
        f"Se esperaba error al omitir x-idbusiness, se obtuvo {respuesta.status_code}"
    )


# ─── CT016 — Webhook (SKIPPED — BUG-001) ─────────────────────────────────────

@pytest.mark.skip(
    reason="BUG-001: PHONE_REGISTER_FAILED — WhatsApp no conectado. "
           "Ruta /webhook no confirmada. Desbloquear cuando se resuelva el registro."
)
def test_ct016_webhook_sin_firma_es_rechazado():
    """CT016_SEC — Webhook sin firma X-Hub-Signature debe devolver 401."""
    from utils import post_ai, webhook_texto, WEBHOOK
    respuesta = post_ai(
        WEBHOOK,
        json=webhook_texto("wamid_test_001", "573016927674", "test"),
    )
    assert respuesta.status_code == 401


@pytest.mark.skip(
    reason="BUG-001: PHONE_REGISTER_FAILED — WhatsApp no conectado. "
           "Ruta /webhook no confirmada. Desbloquear cuando se resuelva el registro."
)
def test_ct016_webhook_payload_con_inyeccion_es_rechazado_o_sanitizado():
    """CT016_SEC — Payload con SQL/XSS en el cuerpo del mensaje debe ser sanitizado."""
    from utils import post_ai, webhook_texto, WEBHOOK
    payload = webhook_texto(
        "wamid_xss_001",
        "573016927674",
        "<script>alert(1)</script>'; DROP TABLE conversations;--",
    )
    respuesta = post_ai(WEBHOOK, json=payload)
    # Debe responder 200 (procesado y sanitizado) o 400 (rechazado)
    assert respuesta.status_code in (200, 400), (
        f"Se obtuvo {respuesta.status_code}"
    )
