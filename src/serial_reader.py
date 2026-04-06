"""
serial_reader.py
----------------
Simula a leitura de dados de um Arduino via porta serial e envia para a API Flask.

Em produção, o Arduino enviaria JSON pela serial a cada 5 segundos, ex:
  {"temperatura": 24.5, "umidade": 60.0, "pressao": 1013.2}

Como não há hardware disponível, os dados são gerados aleatoriamente dentro de
faixas realistas para uma estação meteorológica.

Para usar com hardware real:
  - Defina MOCK_MODE = False
  - Ajuste SERIAL_PORT para a porta do seu Arduino (ex: "COM3" ou "/dev/ttyUSB0")
"""

import json
import random
import time
import requests

# ──────────────── configurações ────────────────
API_URL     = "http://localhost:5000/leituras"
INTERVAL    = 5          # segundos entre leituras
LOCALIZACAO = "Inteli - São Paulo"
MOCK_MODE   = True       # True → dados simulados; False → porta serial real

# Apenas relevante quando MOCK_MODE = False
SERIAL_PORT = "COM3"
BAUD_RATE   = 9600
# ───────────────────────────────────────────────


def gerar_leitura_mock():
    """Gera uma leitura simulada com variação realista."""
    temperatura = round(random.uniform(18.0, 35.0), 1)
    umidade     = round(random.uniform(40.0, 90.0), 1)
    pressao     = round(random.uniform(1000.0, 1025.0), 1)
    return {
        "temperatura": temperatura,
        "umidade":     umidade,
        "pressao":     pressao,
        "localizacao": LOCALIZACAO,
    }


def enviar_leitura(dados):
    try:
        resp = requests.post(API_URL, json=dados, timeout=5)
        resp.raise_for_status()
        print(f"[OK] Enviado: {dados} → HTTP {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao enviar: {e}")


def loop_mock():
    print(f"[MOCK] Iniciando envio simulado a cada {INTERVAL}s. Ctrl+C para parar.")
    while True:
        dados = gerar_leitura_mock()
        enviar_leitura(dados)
        time.sleep(INTERVAL)


def loop_serial():
    import serial  # pyserial – instale com: pip install pyserial

    print(f"[SERIAL] Conectando em {SERIAL_PORT} @ {BAUD_RATE} baud...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=10) as ser:
        print("[SERIAL] Conectado. Aguardando dados do Arduino...")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            try:
                dados = json.loads(line)
                dados.setdefault("localizacao", LOCALIZACAO)
                enviar_leitura(dados)
            except json.JSONDecodeError:
                print(f"[AVISO] Linha ignorada (não é JSON): {line!r}")


if __name__ == "__main__":
    if MOCK_MODE:
        loop_mock()
    else:
        loop_serial()
