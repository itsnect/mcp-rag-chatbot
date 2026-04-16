"""
Pobla PostgreSQL con datos mock de cuentas y transacciones.
Ejecutar una sola vez antes de grabar.
"""

import psycopg2

CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "fintech",
    "user": "chatbot",
    "password": "chatbot123",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS cuentas (
    id          SERIAL PRIMARY KEY,
    cliente     VARCHAR(100) NOT NULL,
    tipo        VARCHAR(50)  NOT NULL,  -- 'corriente' | 'ahorro'
    saldo       NUMERIC(12,2) NOT NULL,
    moneda      VARCHAR(10)  DEFAULT 'CLP',
    activa      BOOLEAN      DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transacciones (
    id              SERIAL PRIMARY KEY,
    cuenta_id       INTEGER REFERENCES cuentas(id),
    tipo            VARCHAR(50) NOT NULL,  -- 'deposito' | 'retiro' | 'transferencia'
    monto           NUMERIC(12,2) NOT NULL,
    descripcion     TEXT,
    fecha           TIMESTAMP DEFAULT NOW()
);
"""

CUENTAS = [
    ("Ana García",    "corriente", 1_250_000.00),
    ("Pedro Rojas",   "ahorro",    3_800_000.00),
    ("María López",   "corriente",   450_000.00),
    ("Carlos Vega",   "ahorro",    9_100_000.00),
    ("Sofía Muñoz",   "corriente", 2_300_000.00),
]

TRANSACCIONES = [
    (1, "deposito",      500_000, "Sueldo enero"),
    (1, "retiro",        200_000, "Pago arriendo"),
    (2, "deposito",    1_000_000, "Bono anual"),
    (3, "transferencia", 150_000, "Pago factura"),
    (4, "deposito",    2_500_000, "Venta propiedad"),
    (5, "retiro",        300_000, "Compra supermercado"),
    (1, "transferencia", 100_000, "Envío a Pedro"),
    (2, "retiro",        250_000, "Viaje fin de semana"),
]

def main():
    conn = psycopg2.connect(**CONN)
    cur = conn.cursor()

    print("Creando tablas...")
    cur.execute(SCHEMA)

    print("Insertando cuentas...")
    for cliente, tipo, saldo in CUENTAS:
        cur.execute(
            "INSERT INTO cuentas (cliente, tipo, saldo) VALUES (%s, %s, %s)",
            (cliente, tipo, saldo)
        )

    print("Insertando transacciones...")
    for cuenta_id, tipo, monto, desc in TRANSACCIONES:
        cur.execute(
            "INSERT INTO transacciones (cuenta_id, tipo, monto, descripcion) VALUES (%s, %s, %s, %s)",
            (cuenta_id, tipo, monto, desc)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Base de datos lista.")

if __name__ == "__main__":
    main()
