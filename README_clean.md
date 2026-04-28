---
title: "Readme Full"
author: "Edwin José Nolasco"
date: "2026-04-28"
---

# 🇩🇴 rd-territorial-system

Motor de resolución territorial de alta precisión para República Dominicana.

API REST diseñada para resolver, normalizar y consultar entidades territoriales (provincias, municipios, distritos municipales, secciones, barrios y sub-barrios) con enfoque en:

- precisión semántica
- rendimiento en memoria
- control de acceso granular
- observabilidad y operación en producción

---

## 🎯 Objetivo

Proveer un servicio backend robusto y escalable que permita:

- Resolver nombres territoriales ambiguos
- Normalizar estructuras administrativas
- Soportar integraciones externas (apps, DSS, pipelines ML)
- Operar bajo condiciones reales de producción (seguridad + rate limiting + logging)

---

## 🧱 Arquitectura

```text
Cliente (API / SDK / DSS)
        │
        ▼
FastAPI (API v1)
        │
        ├── Seguridad
        │     - API Keys
        │     - Scopes
        │     - Client identification
        │
        ├── Rate Limiting
        │     - Memory / Redis backend
        │     - Per-client enforcement
        │
        ├── Resolver Engine
        │     - Índices en memoria
        │     - Matching determinístico
        │     - Resolución jerárquica
        │
        ├── Observabilidad
        │     - Logging estructurado
        │     - request_id / client_id
        │
        ▼
Catálogo Territorial (~20k entidades)
```

---

## 📦 Estado del sistema

- API v1 estable
- Catálogo nacional completo (32 provincias)
- ~20,000 entidades territoriales
- Resolver optimizado en memoria
- OpenAPI validado
- +175 tests pasando
- Cobertura ≥ 80%
- Rate limiting distribuido (Redis) validado

---

## 🚀 Inicio rápido

```bash
git clone https://github.com/edjnolasco/rd-territorial-system.git
cd rd-territorial-system

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Documentación:
http://localhost:8000/docs

---

## 🐳 Ejecución con Docker

```bash
docker-compose up --build
```

Servicios incluidos:

- API (FastAPI)
- Redis (rate limiting distribuido)

---

## 🔒 Seguridad

### Modos disponibles

| Modo     | Descripción |
|----------|------------|
| public   | Sin autenticación |
| api_key  | Requiere API Key |
| hybrid   | Público + protegido por scopes |

---

### API Keys

Ubicación:
data/api_keys.json

- soporte fallback vía variables de entorno
- nunca se exponen en logs
- uso de api_key_hash para trazabilidad segura

---

### Identificación de cliente

Cada request genera:

client_id:
- client:<id>
- api_key:<hash>
- ip fallback

Permite:

- rate limiting por cliente real
- trazabilidad completa

---

### Scopes

- control por endpoint
- soporte wildcard (*)

---

## ⚙️ Rate Limiting

Características:

- aplicado por client_id
- configurable por cliente
- soporta overrides

Backends:

- memory (desarrollo)
- redis (producción)

Respuesta estándar:

HTTP 429 Too Many Requests

---

## 📊 Observabilidad

Cada request incluye:

- request_id
- client_id
- api_key_hash

---

## 🧠 Resolver territorial

Capacidades:

- resolución jerárquica completa
- manejo de ambigüedad
- normalización de nombres
- matching robusto

---

## 📡 Ejemplos de uso

### Request básico

```bash
curl -X POST http://localhost:8000/api/v1/resolve   -H "Content-Type: application/json"   -d '{"query": "Azua", "level": "province"}'
```

---

### Con API Key

```bash
curl -X POST http://localhost:8000/api/v1/resolve   -H "Authorization: Bearer <API_KEY>"   -H "Content-Type: application/json"   -d '{"query": "Brisas del Norte", "level": "sub_barrio"}'
```

---

## ❗ Respuestas típicas

401 Unauthorized  
403 Forbidden  
429 Too Many Requests  

---

## 🧪 Testing

```text
```bash
python -m pytest
```
```

---

## 📁 Estructura del proyecto

```text
rd-territorial-system/
├── app/
├── src/
├── data/
├── tests/
├── Dockerfile
├── docker-compose.yml
```

---

## 📌 Consideraciones de diseño

- Resolver en memoria → latencia mínima
- Catálogo normalizado → consistencia
- Seguridad desacoplada → flexible
- Rate limiting por cliente → control real
- Observabilidad nativa → producción-ready

---

## 🔭 Casos de uso

- DSS territoriales
- Normalización de direcciones
- Integración con sistemas gubernamentales
- Pipelines de datos geoespaciales
- APIs públicas controladas

---

## 👤 Autor

Edwin José Nolasco  
PhD (c) Artificial Intelligence & Machine Learning
