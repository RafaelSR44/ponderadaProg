from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
import database

app = Flask(__name__)
database.init_db()

# ─────────────────────────────────────────────
# Web pages
# ─────────────────────────────────────────────

@app.route("/")
def index():
    leituras = database.listar_leituras(limit=10)
    stats = database.estatisticas()
    return render_template("index.html", leituras=leituras, stats=stats)


@app.route("/historico")
def historico():
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page
    leituras = database.listar_leituras(limit=per_page, offset=offset)
    return render_template("historico.html", leituras=leituras, page=page)


@app.route("/editar/<int:leitura_id>", methods=["GET", "POST"])
def editar(leitura_id):
    leitura = database.obter_leitura(leitura_id)
    if not leitura:
        abort(404)
    if request.method == "POST":
        database.atualizar_leitura(
            leitura_id,
            temperatura=float(request.form["temperatura"]),
            umidade=float(request.form["umidade"]),
            pressao=float(request.form["pressao"]) if request.form.get("pressao") else None,
            localizacao=request.form.get("localizacao"),
        )
        return redirect(url_for("historico"))
    return render_template("editar.html", leitura=leitura)


@app.route("/deletar/<int:leitura_id>", methods=["POST"])
def deletar_view(leitura_id):
    database.deletar_leitura(leitura_id)
    return redirect(url_for("historico"))


# ─────────────────────────────────────────────
# REST API
# ─────────────────────────────────────────────

@app.route("/leituras", methods=["GET"])
def api_listar():
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    return jsonify(database.listar_leituras(limit=limit, offset=offset))


@app.route("/leituras", methods=["POST"])
def api_criar():
    data = request.get_json(force=True)
    if data is None:
        return jsonify({"erro": "JSON inválido"}), 400
    temp = data.get("temperatura")
    umid = data.get("umidade")
    if temp is None or umid is None:
        return jsonify({"erro": "temperatura e umidade são obrigatórios"}), 422
    row_id = database.inserir_leitura(
        temperatura=float(temp),
        umidade=float(umid),
        pressao=data.get("pressao"),
        localizacao=data.get("localizacao", "Inteli - São Paulo"),
    )
    leitura = database.obter_leitura(row_id)
    return jsonify(leitura), 201


@app.route("/leituras/<int:leitura_id>", methods=["GET"])
def api_obter(leitura_id):
    leitura = database.obter_leitura(leitura_id)
    if not leitura:
        return jsonify({"erro": "Leitura não encontrada"}), 404
    return jsonify(leitura)


@app.route("/leituras/<int:leitura_id>", methods=["PUT"])
def api_atualizar(leitura_id):
    data = request.get_json(force=True)
    if data is None:
        return jsonify({"erro": "JSON inválido"}), 400
    updated = database.atualizar_leitura(
        leitura_id,
        temperatura=data.get("temperatura"),
        umidade=data.get("umidade"),
        pressao=data.get("pressao"),
        localizacao=data.get("localizacao"),
    )
    if not updated:
        return jsonify({"erro": "Leitura não encontrada ou nenhum campo fornecido"}), 404
    return jsonify(database.obter_leitura(leitura_id))


@app.route("/leituras/<int:leitura_id>", methods=["DELETE"])
def api_deletar(leitura_id):
    deleted = database.deletar_leitura(leitura_id)
    if not deleted:
        return jsonify({"erro": "Leitura não encontrada"}), 404
    return jsonify({"mensagem": f"Leitura {leitura_id} deletada com sucesso"})


@app.route("/api/estatisticas", methods=["GET"])
def api_estatisticas():
    return jsonify(database.estatisticas())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
