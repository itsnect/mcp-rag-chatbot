"""
Herramientas MCP construidas a mano.
Cada herramienta es un dict con nombre, descripción, input y output,
más una función que la ejecuta.
"""

import psycopg2
import psycopg2.extras

CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "fintech",
    "user": "chatbot",
    "password": "chatbot123",
}

# ── Contratos MCP ─────────────────────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "get_account_balance",
        "description": "Obtiene el saldo actual de una cuenta dado el nombre del cliente.",
        "input":  {"cliente": "string"},
        "output": {"cliente": "string", "tipo": "string", "saldo": "float", "moneda": "string"},
    },
    {
        "name": "get_transactions",
        "description": "Obtiene las últimas transacciones de un cliente.",
        "input": {"cliente": "string"},
        "output": {"transacciones": "list"},
    },
]

# ── Implementaciones ──────────────────────────────────────────────────────────

def _connect():
    return psycopg2.connect(**CONN)


def get_account_balance(cliente: str) -> dict:
    conn = _connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT cliente, tipo, saldo, moneda
        FROM cuentas
        WHERE LOWER(cliente) LIKE LOWER(%s) AND activa = TRUE
        LIMIT 1
        """,
        (f"%{cliente}%",),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"error": f"No se encontró cuenta para '{cliente}'."}
    return dict(row)


def get_transactions(cliente: str, limite: int = 5) -> dict:
    conn = _connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT t.tipo, t.monto, t.descripcion, t.fecha
        FROM transacciones t
        JOIN cuentas c ON c.id = t.cuenta_id
        WHERE LOWER(c.cliente) LIKE LOWER(%s)
        ORDER BY t.fecha DESC
        LIMIT %s
        """,
        (f"%{cliente}%", limite),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"transacciones": [dict(r) for r in rows]}


# ── Dispatcher ────────────────────────────────────────────────────────────────

TOOL_MAP = {
    "get_account_balance": get_account_balance,
    "get_transactions":    get_transactions,
}


def execute_tool(name: str, params: dict) -> dict:
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"error": f"Herramienta '{name}' no existe."}
    return fn(**params)
