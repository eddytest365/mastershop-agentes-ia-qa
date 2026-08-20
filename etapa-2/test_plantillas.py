"""
test_plantillas.py — Etapa 2: Plantillas y Mensajes Predeterminados
Cubre:
  CT005_E2E_CrearYUsarPlantillaWhatsApp     (listado + status)
  CT006_FT_MensajesPredeterminadosEnConversaciónActiva
  CT012_FT_ListadoYEstadosDePlantillas

Endpoints confirmados:
  GET /api/v1/ai/templates
  GET /api/v1/ai/templates/{id}/status
  GET /api/v1/ai/predefined-messages
"""

import requests
import pytest
from utils import (
    AI_API_BASE, DEFAULT_TIMEOUT,
    auth_headers, headers_otro_negocio, get_ai,
    TEMPLATES, PREDEFINED_MESSAGES,
)


# ─── CT012 / CT005 — Listado de plantillas ───────────────────────────────────

def test_ct012_templates_retorna_200():
    """CT012 — GET /templates devuelve 200 con credenciales válidas."""
    respuesta = get_ai(TEMPLATES)
    assert respuesta.status_code == 200, (
        f"Templates no cargó. Status: {respuesta.status_code} | {respuesta.text[:200]}"
    )


def test_ct012_templates_es_json():
    """CT012 — /templates devuelve JSON parseable."""
    respuesta = get_ai(TEMPLATES)
    assert respuesta.status_code == 200
    try:
        datos = respuesta.json()
    except Exception:
        pytest.fail("La respuesta de /templates no es JSON válido")
    assert isinstance(datos, (list, dict))


def test_ct012_templates_filtro_por_estado():
    """CT012 — Filtrar por estado (approved, paused, rejected, pending) no da 500."""
    for estado in ("approved", "paused", "rejected", "pending"):
        r = get_ai(TEMPLATES, params={"status": estado})
        assert r.status_code != 500, (
            f"Filtro status={estado} causó 500: {r.text[:200]}"
        )


def test_ct012_templates_busqueda_por_nombre():
    """CT012 — Parámetro de búsqueda en /templates no da 500."""
    r = get_ai(TEMPLATES, params={"search": "Confirmacion"})
    assert r.status_code != 500


def test_ct012_templates_negocio_ajeno_rechazado():
    """CT012 / CT009 — /templates con negocio ajeno devuelve 401 o 403."""
    r = requests.get(
        f"{AI_API_BASE}{TEMPLATES}",
        headers=headers_otro_negocio(),
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code in (401, 403), (
        f"Cross-tenant en /templates no bloqueado. Status: {r.status_code}"
    )


def test_ct012_templates_sin_token_rechazado():
    """CT012 / CT009 — /templates sin token devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    r = requests.get(
        f"{AI_API_BASE}{TEMPLATES}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code == 401


# ─── CT012 — Status individual de plantilla ───────────────────────────────────

def test_ct012_template_status_endpoint_existe():
    """
    CT012 — GET /templates/{id}/status existe como ruta (confirmado en Chrome).
    Usa el primer template del listado para verificar el endpoint.
    Si no hay templates, el test se omite automáticamente.
    """
    listado = get_ai(TEMPLATES)
    if listado.status_code != 200:
        pytest.skip("No se pudo obtener listado de templates para este test")

    datos = listado.json()
    # Extraer primer template de lista o paginación
    if isinstance(datos, list):
        items = datos
    else:
        items = datos.get("data", datos.get("items", datos.get("results", [])))

    if not items:
        pytest.skip("No hay templates disponibles para verificar /status")

    template_id = items[0].get("id") or items[0].get("uuid") or items[0].get("_id")
    if not template_id:
        pytest.skip("No se pudo extraer ID del primer template")

    r = get_ai(f"{TEMPLATES}/{template_id}/status")
    assert r.status_code in (200, 404), (
        f"GET /templates/{template_id}/status retornó {r.status_code}"
    )


# ─── CT006 — Mensajes predeterminados ────────────────────────────────────────

def test_ct006_predefined_messages_retorna_200():
    """CT006 — GET /predefined-messages devuelve 200 con credenciales válidas."""
    respuesta = get_ai(PREDEFINED_MESSAGES)
    assert respuesta.status_code == 200, (
        f"Predefined messages no cargó. Status: {respuesta.status_code} | "
        f"{respuesta.text[:200]}"
    )


def test_ct006_predefined_messages_es_json():
    """CT006 — /predefined-messages devuelve JSON parseable."""
    respuesta = get_ai(PREDEFINED_MESSAGES)
    assert respuesta.status_code == 200
    try:
        datos = respuesta.json()
    except Exception:
        pytest.fail("La respuesta de /predefined-messages no es JSON válido")
    assert isinstance(datos, (list, dict))


def test_ct006_predefined_messages_negocio_ajeno_rechazado():
    """CT006 / CT009 — /predefined-messages con negocio ajeno devuelve 401 o 403."""
    r = requests.get(
        f"{AI_API_BASE}{PREDEFINED_MESSAGES}",
        headers=headers_otro_negocio(),
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code in (401, 403), (
        f"Cross-tenant en /predefined-messages no bloqueado. Status: {r.status_code}"
    )


def test_ct006_predefined_messages_sin_token_rechazado():
    """CT006 / CT009 — /predefined-messages sin token devuelve 401."""
    headers = auth_headers()
    headers.pop("Authorization")
    r = requests.get(
        f"{AI_API_BASE}{PREDEFINED_MESSAGES}",
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
    assert r.status_code == 401
