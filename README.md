# Agente Bancario — RAG + MCP + Claude

Chatbot bancario en consola que combina RAG (ChromaDB) con herramientas MCP (PostgreSQL).

## Stack

- **LLM:** Claude (Anthropic)
- **RAG:** ChromaDB (vectorial en contenedor)
- **BD relacional:** PostgreSQL (Docker)
- **Consola:** Rich

## Setup

```bash
# 1. Levantar contenedores
docker compose up -d

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Poblar PostgreSQL con datos mock
python data/insert_mock.py

# 4. Cargar documentos en ChromaDB
python rag/ingest.py

# 5. Exportar API key de Anthropic
export ANTHROPIC_API_KEY=sk-...

# 6. Correr el chatbot
python main.py
```

## Preguntas de ejemplo

**RAG (políticas):**
- ¿Cuál es el límite de retiro en cajero?
- ¿Cuántos retiros gratuitos tiene una cuenta de ahorro?
- ¿Hasta qué hora puedo hacer transferencias el mismo día?

**MCP (datos reales):**
- ¿Cuál es el saldo de Ana García?
- ¿Cuáles son las últimas transacciones de Pedro Rojas?

## Estructura

```
chatbot/
├── docker-compose.yml     # PostgreSQL + ChromaDB
├── data/
│   ├── insert_mock.py     # poblar PostgreSQL
│   └── docs.txt           # políticas del banco
├── rag/
│   └── ingest.py          # cargar docs a ChromaDB
├── mcp/
│   └── tools.py           # herramientas MCP a mano
├── agent/
│   └── router.py          # decide RAG vs MCP
└── main.py                # chatbot en consola
```

## Código fuente

Disponible en [nectdnb.vercel.app](https://nectdnb.vercel.app)
