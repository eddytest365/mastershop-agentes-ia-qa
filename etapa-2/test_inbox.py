"""
test_inbox.py — Etapa 2: Inbox Unificado con Búsqueda y Filtros
Cubre:
  CT001_E2E_InboxUnificadoConBúsquedaYFiltros
  CT009_SEC_AislamientoTenantYValidacionDePermisos

Endpoints confirmados:
  GET /api/v1/ai/conversations
  GET /api/v1/ai/labels
"""

import requests
import pytest
from utils import (
    AI_API_BASE, DEFAULT_TIMEOUT,
    auth_headers, headers_otro_negocio, get_ai,
    CONVERSATIONS, LABELS,
)


# ─── CT001 — Inbox: conversaciones ───────────────────────────────────────────

def test_ct001_inbox_carga_conversaciones():
    """CT001 — GET /conversations retorna 200 con credenciales válidas."""
    respuesta = get_ai(CONVERSATIONS)
    assert respuesta.status_code == 200, (
        f"Inbox no cargó. Status: {respuesta.status_code} | {respuesta.text[:200]}"
    )


def test_ct001_inbox_body_parseable():
    """CT001 — El inbox retorna JSON con estructura de lista o paginación."""
    respuesta = get_ai(CONVERSATIONS)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert isinstance(datos, (list, dict)), (
        f"Se esperaba lista o dict, se obtuvo: {type(datos)}"
    )


def test_ct001_inbox_busqueda_por_nombre():
    """CT001 — Búsqueda por nombre no rompe el endpoint (no debe dar 500)."""
    r = get_ai(CONVERSATIONS, params={"search": "Jose"})
    assert r.status_code != 500, f"Búsqueda causó 500: {r.text[:200]}"
    assert r.status_code in (200, 400, 422)


def test_ct001_inbox_busqueda_por_telefono():
    """CT001 — Búsqueda por teléfono no da 500."""
    r = get_ai(CONVERSATIONS, params={"phone": "+573012345678"})
    assert r.status_code != 500


def test_ct001_inbox_filtro_estado_pendiente():
    """CT001 — Filtro por estado pendiente no da 500."""
    r = get_ai(CONVERSATIONS, params={"status": "pending"})
    assert r.status_code != 500


def test_ct001_inbox_filtro_estado_resuelta():
    """CT001 — Filtro por estado resuelta no da 500."""
    r = get_ai(CONVERSATIONS, params={"status": "resolved"})
    assert r.status_code != 500


def test_ct001_inbox_combinacion_busqueda_y_filtro():
    """CT001 — Búsqueda + filtro de estado combinados no da 500."""
    r = get_ai(CONVERSATIONS, params={"search": "Jose", "status": "pending"})
    assert r.status_code != 500


def test_ct001_inbox_paginacion():
    """CT001 — Paginación básica (page + limit) no da 500."""
    r = get_ai(CONVERSATIONS, params={"page": 1, "limit": 20})
    assert r.status_code not in (500,)


# ─── CT001 — Inbox: etiquetas ─────────────────────────────────────────────────

def test_ct001_labels_retorna_200():
    """CT001 — GET /labels retorna 200 (etiquetas disponibles para filtrar inbox)."""
    respuesta = get_ai(LABELS)
    assert respuesta.status_code == 200, (
        f"Labels no cargó. Status: {respuesta.status_code} | {respuesta.text[:200]}"
    )


def test_ct001_labels_es_lista():
    """CT001 — /labels devuelve una lista o un objeto con items."""
    respuesta = get_ai(LABELS)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert isinstance(datos, (list, dict)), f"Tipo inesperado: {type(datos)}"


# ─── CT009 — Seguridad y aislamiento de tenant ──────────────────────────────

def test_ct009_sin_token_es_rechazado():
    """CT009_SEC — Sin Authorization el inbox devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    r = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code == 401, f"Se esperaba 401, se obtuvo {r.status_code}"


def test_ct009_token_invalido_es_rechazado():
    """CT009_SEC — Token inválido devuelve 401."""
    headers = auth_headers(token="token-invalido-qa")
    r = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code == 401, f"Se esperaba 401, se obtuvo {r.status_code}"


def test_ct009_negocio_ajeno_es_rechazado():
    """CT009_SEC — x-idbusiness de otro negocio devuelve 401 o 403."""
    r = requests.get(
        f"{AI_API_BASE}{CONVERSATIONS}",
        headers=headers_otro_negocio(),
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code in (401, 403), (
        f"Cross-tenant no bloqueado. Status: {r.status_code}. "
        "Fallo de aislamiento multi-tenant."
    )


def test_ct009_labels_negocio_ajeno_es_rechazado():
    """CT009_SEC — /labels con negocio ajeno devuelve 401 o 403."""
    r = requests.get(
        f"{AI_API_BASE}{LABELS}",
        headers=headers_otro_negocio(),
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code in (401, 403), (
        f"Cross-tenant en /labels no bloqueado. Status: {r.status_code}"
    )
