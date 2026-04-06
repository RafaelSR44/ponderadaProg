# Estação Meteorológica IoT

Sistema de medição meteorológica com Flask REST API, SQLite e interface web. Os dados de sensores são simulados por um mock Python (sem necessidade de hardware físico para execução).

## Arquitetura

```
Arduino (DHT11) → Serial → serial_reader.py → POST /leituras → Flask API → SQLite
                                                                         ↓
                                                              Interface Web (Jinja2 + Chart.js)
```

## Estrutura do Projeto

```
ponderadaProg/
├── arduino/
│   └── estacao.ino          # Sketch Arduino (referência de hardware)
├── src/
│   ├── app.py               # Servidor Flask (API + páginas web)
│   ├── database.py          # Módulo SQLite (CRUD + estatísticas)
│   ├── serial_reader.py     # Leitor serial / mock de dados
│   ├── seed.py              # Script para popular o banco com 35 leituras
│   ├── estacao.db           # Banco SQLite (gerado automaticamente)
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html       # Dashboard com gráfico
│   │   ├── historico.html   # Tabela completa + paginação
│   │   └── editar.html      # Formulário de edição
│   └── static/
│       ├── css/style.css
│       └── js/main.js
└── README.md
```

## Pré-requisitos

- Python 3.10+
- pip

## Instalação

```bash
pip install flask requests
```

> Para uso com hardware real, instale também: `pip install pyserial`

## Como Executar

### 1. Iniciar o servidor Flask

```bash
cd src
python app.py
```

Acesse [http://localhost:5000](http://localhost:5000)

### 2. Popular o banco com dados de exemplo (opcional)

```bash
cd src
python seed.py
```

Insere 35 leituras com timestamps distribuídos nas últimas 35 horas.

### 3. Iniciar o leitor de dados (mock)

Em outro terminal:

```bash
cd src
python serial_reader.py
```

Envia uma leitura simulada à API a cada 5 segundos.

#### Modo hardware real

Edite `serial_reader.py` e defina:

```python
MOCK_MODE   = False
SERIAL_PORT = "COM3"   # ajuste para sua porta
```

## Endpoints da API

| Método | Endpoint            | Descrição                      |
|--------|---------------------|--------------------------------|
| GET    | `/`                 | Dashboard web                  |
| GET    | `/leituras`         | Lista todas as leituras (JSON) |
| POST   | `/leituras`         | Cria nova leitura              |
| GET    | `/leituras/<id>`    | Retorna leitura pelo ID        |
| PUT    | `/leituras/<id>`    | Atualiza leitura pelo ID       |
| DELETE | `/leituras/<id>`    | Remove leitura pelo ID         |
| GET    | `/api/estatisticas` | Estatísticas agregadas         |

### Exemplo – POST /leituras

```bash
curl -X POST http://localhost:5000/leituras \
     -H "Content-Type: application/json" \
     -d '{"temperatura": 25.3, "umidade": 65.0, "pressao": 1013.2}'
```

## Schema do Banco

```sql
CREATE TABLE leituras (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    temperatura REAL     NOT NULL,
    umidade     REAL     NOT NULL,
    pressao     REAL,
    localizacao TEXT     DEFAULT 'Inteli - São Paulo',
    timestamp   DATETIME DEFAULT (datetime('now','localtime'))
);
```
