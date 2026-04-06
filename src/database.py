import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "estacao.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leituras (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL    NOT NULL,
            umidade     REAL    NOT NULL,
            pressao     REAL,
            localizacao TEXT    DEFAULT 'Inteli - São Paulo',
            timestamp   DATETIME DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()


# ---------- CREATE ----------
def inserir_leitura(temperatura, umidade, pressao=None, localizacao="Inteli - São Paulo"):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO leituras (temperatura, umidade, pressao, localizacao) VALUES (?, ?, ?, ?)",
        (temperatura, umidade, pressao, localizacao),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


# ---------- READ ALL ----------
def listar_leituras(limit=100, offset=0):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM leituras ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- READ ONE ----------
def obter_leitura(leitura_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM leituras WHERE id = ?", (leitura_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- UPDATE ----------
def atualizar_leitura(leitura_id, temperatura=None, umidade=None, pressao=None, localizacao=None):
    fields, values = [], []
    if temperatura is not None:
        fields.append("temperatura = ?"); values.append(temperatura)
    if umidade is not None:
        fields.append("umidade = ?"); values.append(umidade)
    if pressao is not None:
        fields.append("pressao = ?"); values.append(pressao)
    if localizacao is not None:
        fields.append("localizacao = ?"); values.append(localizacao)
    if not fields:
        return False
    values.append(leitura_id)
    conn = get_connection()
    cur = conn.execute(
        f"UPDATE leituras SET {', '.join(fields)} WHERE id = ?", values
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


# ---------- DELETE ----------
def deletar_leitura(leitura_id):
    conn = get_connection()
    cur = conn.execute("DELETE FROM leituras WHERE id = ?", (leitura_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


# ---------- STATS ----------
def estatisticas():
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*)          AS total,
            AVG(temperatura)  AS temp_media,
            MIN(temperatura)  AS temp_min,
            MAX(temperatura)  AS temp_max,
            AVG(umidade)      AS umidade_media,
            MIN(umidade)      AS umidade_min,
            MAX(umidade)      AS umidade_max,
            AVG(pressao)      AS pressao_media
        FROM leituras
    """).fetchone()
    conn.close()
    return dict(row)
