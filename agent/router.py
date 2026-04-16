"""
Router del agente.
Decide si la pregunta va a ChromaDB (RAG) o a PostgreSQL vía MCP.
Usa Claude para tomar la decisión y ejecutar la herramienta correcta.
"""

import json
import chromadb
import anthropic

from mcp.tools import MCP_TOOLS, execute_tool
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

debug_console = Console()

def debug(title: str, data):
    debug_console.print(f"\n[bold yellow]── {title} ──[/bold yellow]")
    debug_console.print(Syntax(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        "json",
        theme="monokai",
    ))

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION  = "politicas_banco"

chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection     = chroma_client.get_collection(COLLECTION)

claude = anthropic.Anthropic()

SYSTEM_PROMPT = f"""Eres un asistente bancario inteligente.

Tienes acceso a dos fuentes de información:

1. RAG (base de datos vectorial): contiene políticas, límites y reglas generales del banco.
   Úsala para preguntas sobre cómo funciona algo, cuáles son los límites, qué se permite.

2. MCP (base de datos relacional): contiene datos reales de cuentas y transacciones.
   Úsala para preguntas sobre el saldo, movimientos o información específica de un cliente.

Herramientas MCP disponibles:
{json.dumps(MCP_TOOLS, indent=2, ensure_ascii=False)}

Cuando necesites datos de un cliente, usa la herramienta MCP correspondiente.
Cuando la pregunta sea sobre políticas o reglas, responde usando el contexto RAG.
Sé conciso y directo en tus respuestas.
"""


def query_rag(question: str) -> str:
    """Busca en ChromaDB los chunks más relevantes."""
    results = collection.query(query_texts=[question], n_results=3)
    docs = results["documents"][0]
    return "\n\n".join(docs)


def run(question: str) -> str:
    """
    Procesa la pregunta:
    1. Consulta RAG para tener contexto de políticas.
    2. Envía a Claude con herramientas MCP disponibles.
    3. Si Claude usa una herramienta, ejecuta y devuelve resultado.
    """

    rag_context = query_rag(question)

    messages = [
        {
            "role": "user",
            "content": (
                f"Contexto de políticas del banco:\n{rag_context}\n\n"
                f"Pregunta del usuario: {question}"
            ),
        }
    ]

    # Construir tools en formato Anthropic
    tools = [
        {
            "name": t["name"],
            "description": t["description"],
            "input_schema": {
                "type": "object",
                "properties": {k: {"type": v} for k, v in t["input"].items()},
                "required": list(t["input"].keys()),
            },
        }
        for t in MCP_TOOLS
    ]

    # ── DEBUG: lo que le mandamos a Claude ───────────────────────────────
    debug("📤 REQUEST A CLAUDE", {
        "pregunta": question,
        "rag_context_preview": rag_context[:300] + "..." if len(rag_context) > 300 else rag_context,
        "herramientas_disponibles": [t["name"] for t in tools],
    })

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )

    # ── DEBUG: decisión de Claude ─────────────────────────────────────────
    debug("🧠 DECISIÓN DE CLAUDE", {
        "stop_reason": response.stop_reason,
        "ruta": "MCP → PostgreSQL" if response.stop_reason == "tool_use" else "RAG → ChromaDB",
    })

    # Si Claude quiere usar una herramienta MCP
    if response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")

        # ── DEBUG: contrato MCP que Claude eligió ─────────────────────────
        debug("🔧 HERRAMIENTA MCP SELECCIONADA", {
            "nombre": tool_use.name,
            "input": tool_use.input,
        })

        tool_result = execute_tool(tool_use.name, tool_use.input)

        # ── DEBUG: resultado de PostgreSQL ────────────────────────────────
        debug("📥 RESULTADO DE POSTGRESQL", tool_result)

        # Volver a Claude con el resultado de la herramienta
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(tool_result, ensure_ascii=False, default=str),
                }
            ],
        })

        final = claude.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )
        return final.content[0].text

    # ── DEBUG: respuesta directa desde RAG ───────────────────────────────
    debug("📚 RESPONDIENDO DESDE RAG", {
        "chunks_usados": len(rag_context.split("\n\n")),
    })

    return response.content[0].text