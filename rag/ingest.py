"""
Carga docs.txt en ChromaDB dividiendo por párrafos.
Ejecutar una sola vez antes de grabar.
"""

import chromadb

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION  = "politicas_banco"
DOCS_PATH   = "data/docs.txt"


def main():
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    # Eliminar colección si ya existe (útil para regrabar)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION)

    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        texto = f.read()

    # Dividir por párrafos (doble salto de línea)
    chunks = [c.strip() for c in texto.split("\n\n") if c.strip()]

    print(f"Cargando {len(chunks)} chunks en ChromaDB...")

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )

    print(f"✅ {len(chunks)} chunks cargados en colección '{COLLECTION}'.")


if __name__ == "__main__":
    main()
