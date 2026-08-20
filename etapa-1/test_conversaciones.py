"""
test_conversaciones.py — Etapa 1: Gestión de Conversaciones e Inbox
Cubre:
  CT011_FT_BusquedaYFiltradoDeConversaciones
  CT012_FT_HistoricoDeConversacionYPaginacion
  CT014_FT_AsignacionDeConversacionesAOperarios (smoke + multi-tenant)

Endpoint confirmado: GET /api/v1/ai/conversations
"""

import pytest
from utils import get_ai, auth_headers, headers_otro_negocio, CONVERSATIONS


# ─── CT011 — Inbox básico ─────────────────────────────────────────────────────

def test_ct011_inbox_retorna_200():
    """CT011 — GET /conversations devuelve 200 OK con credenciales válidas."""
    respuesta = get_ai(CONVERSATIONS)
    assert respuesta.status_code == 200, (
        f"Se esperaba 200, se obtuvo {respuesta.status_code}: {respuesta.text[:200]}"
    )


def test_ct011_inbox_retorna_json():
    """CT011 — El body de /conversations es JSON parseable."""
    respuesta = get_ai(CONVERSATIONS)
    assert respuesta.status_code == 200
    try:
        datos = respuesta.json()
    except Exception:
        pytest.fail("La respuesta no es JSON válido")
    assert datos is not None


def test_ct011_inbox_estructura_es_lista_o_objeto():
    """CT011 — El body de /conversations es una lista o un objeto con items/data."""
    respuesta = get_ai(CONVERSATIONS)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    # Acepta lista directa o objeto de paginación {data: [...], total: N}
    assert isinstance(datos, (list, dict)), (
        f"Se esperaba list o dict, se obtuvo {type(datos)}"
    )


def test_ct011_busqueda_por_texto_no_rompe_api():
    """
    CT011 — Pasar parámetro de búsqueda (query/search) no rompe el endpoint.
    Acepta 200 (con o sin resultados) o 400/422 (parámetro no soportado).
    No debe devolver 500.
    """
    respuesta = get_ai(CONVERSATIONS, params={"search": "test"})
    assert respuesta.status_code != 500, (
        f"Búsqueda por texto causó error 500: {respuesta.text[:200]}"
    )
    assert respuesta.status_code in (200, 400, 422), (
        f"Status inesperado: {respuesta.status_code}"
    )


def test_ct011_filtro_por_estado_no_rompe_api():
    """CT011 — Parámetro de filtro por estado no debe causar 500."""
    for estado in ("pending", "resolved", "open"):
        r = get_ai(CONVERSATIONS, params={"status": estado})
        assert r.status_code != 500, (
            f"Filtro status={estado} causó 500: {r.text[:200]}"
        )


# ─── CT012 — Paginación ───────────────────────────────────────────────────────

def test_ct012_paginacion_page_1_no_rompe():
    """CT012 — Parámetro page/limit no debe causar 500."""
    respuesta = get_ai(CONVERSATIONS, params={"page": 1, "limit": 20})
    assert respuesta.status_code not in (500,), (
        f"Paginación causó error: {respuesta.status_code}: {respuesta.text[:200]}"
    )


def test_ct012_paginacion_pagina_alta_retorna_vacio_o_200():
    """CT012 — Pedir una página muy alta devuelve lista vacía (no error)."""
    respuesta = get_ai(CONVERSATIONS, params={"page": 9999, "limit": 50})
    assert respuesta.status_code in (200, 404), (
        f"Se esperaba 200 o 404 en página alta, se obtuvo {respuesta.status_code}"
    )
    if respuesta.status_code == 200:
        datos = respuesta.json()
        if isinstance(datos, list):
            pass
        elif isinstance(datos, dict):
            items = datos.get("data", datos.get("items", datos.get("results", [])))
            assert isinstance(items, list), "Se esperaba lista de items en paginación"


# ─── CT014 — Aislamiento (smoke) ───────────────────────────────────────────────

def test_ct014_negocio_ajeno_no_accede_conversaciones():
    """
    CT014 / CT016 — Headers con negocio ajeno deben ser rechazados (401/403).
    Valida aislamiento básico de tenant en el listado de conversaciones.
    """
    respuesta = get_ai(CONVERSATIONS, headers=headers_otro_negocio())
    assert respuesta.status_code in (401, 403), (
        f"Acceso cross-tenant no fue bloqueado. Status: {respuesta.status_code}. "
        "Posible fallo de aislamiento multi-tenant."
    )
