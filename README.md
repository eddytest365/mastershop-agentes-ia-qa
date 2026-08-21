<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=26&pause=1000&color=F97316&center=true&vCenter=true&width=750&lines=mastershop-agentes-ia-qa+%F0%9F%A7%AA;QA+Automation+%E2%80%94+Agente+IA+Module;53+Tests+%7C+12+Bugs+Documented;Real+API+Testing+with+pytest" alt="header" />

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-7.4+-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Tests](https://img.shields.io/badge/tests-53-22c55e?style=for-the-badge&logo=checkmarx&logoColor=white)
![Bugs](https://img.shields.io/badge/bugs%20found-12-ef4444?style=for-the-badge&logo=bugsnag&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Anthropic-D97757?style=flat&logo=anthropic&logoColor=white)

</div>

---

> **Suite de automatización pytest** para el módulo **Agente IA** de Mastershop.
> Cubre autenticación, idempotencia, seguridad multi-tenant, conversaciones, inbox unificado, plantillas y notificaciones.
> Construida con trazabilidad total a casos de prueba reales — cada test tiene su CT.

---

## 📂 Estructura

```

mastershop-agentes-ia-qa/
│
├── etapa-1/                     # Core API — conexión, lógica, seguridad
│   ├── test_conexion.py         # CT005/CT006 — autenticación y health check
│   ├── test_conversaciones.py   # CT007 — CRUD de conversaciones
│   ├── test_idempotencia.py     # CT008 — webhooks e idempotencia
│   └── test_seguridad.py        # CT009/CT016 — aislamiento multi-tenant
│
├── etapa-2/                     # Features avanzadas del agente
│   ├── test_inbox.py            # CT011/CT012 — inbox unificado
│   ├── test_plantillas.py       # CT013/CT014 — plantillas predefinidas
│   └── test_notificaciones.py   # CT010 — notification actions
│
├── utils.py                     # Config central: auth headers, helpers
├── conftest.py                  # Fixtures globales pytest
├── requirements.txt
└── .env.example
```

---

## 🧪 Cobertura por módulo

| Módulo | Tests | CTs trazados | Severidad max |
|--------|-------|--------------|---------------|
| Autenticación & Conexión | 8 | CT005, CT006 | 🔴 Critical |
| Conversaciones | 12 | CT007 | 🔴 Critical |
| Idempotencia / Webhooks | 10 | CT008 | 🟠 Alto |
| Seguridad multi-tenant | 11 | CT009, CT016 | 🔴 Critical |
| Inbox unificado | 6 | CT011, CT012 | 🟡 Medio |
| Plantillas predefinidas | 4 | CT013, CT014 | 🟠 Alto |
| Notification actions | 5 | CT010 | 🟡 Medio |
| **Total** | **53** | **8 CTs** | — |

---

## 🐛 Bugs documentados (12)

| ID | Descripción | Severidad | Endpoint |
|----|-------------|-----------|----------|
| BUG-001 | Token inválido retorna 200 en lugar de 401 | 🔴 Critical | `/auth` |
| BUG-002 | Cross-tenant: negocio ajeno accede a conversaciones | 🔴 Critical | `/conversations` |
| BUG-003 | Webhook duplicado no es idempotente — procesa dos veces | 🔴 Critical | `/webhook` |
| BUG-004 | `agentId` inválido retorna 500 en lugar de 404 | 🟠 Alto | `/notification-actions` |
| BUG-005 | Respuesta sin `Content-Type: application/json` | 🟠 Alto | `/inbox` |
| BUG-006 | Timeout en conversación con más de 10 items | 🟠 Alto | `/conversations` |
| BUG-007 | Plantilla vacía se guarda sin validación de campos | 🟠 Alto | `/templates` |
| BUG-008 | Mensaje sin `businessId` no es rechazado por el API | 🟡 Medio | `/messages` |
| BUG-009 | Paginación del inbox no respeta el límite enviado | 🟡 Medio | `/inbox` |
| BUG-010 | Header `X-Business-ID` ignorado en varios endpoints | 🟡 Medio | múltiples |
| BUG-011 | Respuesta de plantilla no valida campos requeridos | 🟢 Bajo | `/templates` |
| BUG-012 | Latencia > 3s en carga inicial del agente logistics | 🟢 Bajo | `/agentes` |

---

## ⚙️ Cómo correr

```bash
# 1. Clonar e instalar
git clone https://github.com/eddytest365/mastershop-agentes-ia-qa.git
cd mastershop-agentes-ia-qa
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tu AI_AUTH_TOKEN y AI_API_BASE

# 3. Correr toda la suite
pytest -v

# Solo etapa-1 (core)
pytest etapa-1/ -v

# Solo etapa-2 (features)
pytest etapa-2/ -v

# Reporte conciso
pytest --tb=short -q
```

---

## 🔧 Stack técnico

| Herramienta | Rol en la suite |
|-------------|-----------------|
| `pytest` | Framework principal de testing |
| `requests` | HTTP client para llamadas directas a la API |
| `python-dotenv` | Gestión de variables de entorno |
| `Claude (Anthropic)` | Co-diseño de casos y análisis de cobertura |

---

## 👤 Autor

**Eddy Saenz** — QA Engineer @ Mastershop

[![LinkedIn](https://img.shields.io/badge/LinkedIn-eddy--saenz-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/eddy-saenz-021200al)
[![GitHub](https://img.shields.io/badge/GitHub-eddytest365-181717?style=flat&logo=github&logoColor=white)](https://github.com/eddytest365)

---

<div align="center">
<sub>Built with 🧪 pytest · Bugs found before users did 🐛</sub>
</div>
