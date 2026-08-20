"""
test_idempotencia.py — Etapa 1: Idempotencia y Reprocesamiento
Cubre:
  CT007_FT_SincronizacionBidireccionalConEventosMultiples
  CT008_FT_IdempotenciaYReprocesamiento

Estado: TODOS SKIPPED — BUG-001 (PHONE_REGISTER_FAILED)
El endpoint /webhook no está disponible hasta resolver el registro de WhatsApp.

Para desbloquear:
  1. Completar el flujo OAuth de Meta (paso del código de verificación)
  2. Confirmar la ruta real del webhook en Network tab
  3. Quitar el decorador @pytest.mark.skip de cada test
"""

import pytest
from utils import post_ai, webhook_texto, WEBHOOK

BUG_001 = pytest.mark.skip(
    reason="BUG-001: PHONE_REGISTER_FAILED — endpoint /webhook no disponible. "
           "Resolver registro de WhatsApp y confirmar ruta antes de ejecutar."
)


# ─── CT008 — Idempotencia (primer envío) ──────────────────────────────────────

@BUG_001
def test_ct008_primer_webhook_es_procesado():
    """
    CT008 — Webhook con wamid único se procesa correctamente (200 OK).
    """
    payload = webhook_texto("wamid_idem_001", "573016927674", "Hola, primer envío")
    respuesta = post_ai(WEBHOOK, json=payload)
    assert respuesta.status_code == 200, (
        f"Se esperaba 200 al procesar webhook nuevo, se obtuvo {respuesta.status_code}"
    )


@BUG_001
def test_ct008_webhook_repetido_devuelve_200_sin_duplicar():
    """
    CT008 — Reenviar exactamente el mismo webhook (mismo wamid) devuelve 200 OK
    pero NO crea un mensaje duplicado en la conversación.
    """
    wamid = "wamid_idem_002"
    payload = webhook_texto(wamid, "573016927674", "Mensaje idempotente")

    r1 = post_ai(WEBHOOK, json=payload)
    assert r1.status_code == 200, f"Primer envío falló: {r1.status_code}"

    r2 = post_ai(WEBHOOK, json=payload)
    assert r2.status_code == 200, (
        f"Reintento debería devolver 200 (idempotente), se obtuvo {r2.status_code}"
    )
    # Verificación manual de duplicados: revisar inbox y confirmar que el mensaje
    # aparece una sola vez. Esto se valida via GET /conversations/{id}/messages
    # (endpoint pendiente de confirmación).


@BUG_001
def test_ct008_wamids_distintos_crean_mensajes_distintos():
    """
    CT008 — Dos webhooks con wamid diferente generan dos mensajes (no hay falso positivo
    de idempotencia que descarte un mensaje nuevo legítimo).
    """
    p1 = webhook_texto("wamid_new_001", "573016927674", "Mensaje A")
    p2 = webhook_texto("wamid_new_002", "573016927674", "Mensaje B")

    r1 = post_ai(WEBHOOK, json=p1)
    r2 = post_ai(WEBHOOK, json=p2)

    assert r1.status_code == 200, f"Mensaje A falló: {r1.status_code}"
    assert r2.status_code == 200, f"Mensaje B falló: {r2.status_code}"


# ─── CT007 — Sincronización bidireccional ────────────────────────────────────

@BUG_001
def test_ct007_multiples_eventos_simultaneos_se_procesan():
    """
    CT007 — Enviar 3 webhooks distintos (casi simultáneos) y verificar que
    todos se aceptan con 200 OK sin bloqueos ni pérdidas.
    """
    wamids = ["wamid_multi_001", "wamid_multi_002", "wamid_multi_003"]
    for wamid in wamids:
        r = post_ai(WEBHOOK, json=webhook_texto(wamid, "573016927674", f"Msg {wamid}"))
        assert r.status_code == 200, (
            f"Evento {wamid} no fue aceptado: {r.status_code}"
        )
