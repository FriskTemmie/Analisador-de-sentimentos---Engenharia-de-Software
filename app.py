from flask import Flask, request, jsonify, render_template
from collections import Counter
import re

app = Flask(__name__)

# Dicionário inicial
palavras_positivas = ["feliz", "alegre", "ótimo", "excelente", "maravilhoso", "bom", "amor", "adorar", "incrível", "fantástico", "perfeito", "legal", "bacana", "sucesso", "vitória", "paz", "amizade", "sorrir", "esperança", "lindo", "bonito", "agradável", "divertido", "animado", "satisfeito", "grato"]

palavras_negativas = ["triste", "ruim", "péssimo", "horrível", "terrível", "ódio", "odiar", "chorar", "fracasso", "derrota", "medo", "raiva", "feio", "chato", "desagradável", "entediado", "frustrado", "decepcionado", "cansado", "preocupado", "ansioso", "difícil", "problema", "mal", "infeliz"]

palavras_intensidade = ["muito", "muita", "extremamente", "super", "demasiado", "demasiada", "abundantemente"]

def analisar_sentimento(frase):
    texto = frase.lower()
    tokens = re.findall(r"\w+", texto, flags=re.UNICODE)

    pos_found = []
    pos_total = 0
    neg_found = []
    neg_total = 0
    intens_found = []
    intens_mult = 0
    pointer = False

    for i, t in enumerate(tokens):
        if pointer:
            if t in palavras_positivas:
                pos_total += intens_mult
                # print(f'pos = {pos_total}')
            if t in palavras_negativas:
                neg_total += intens_mult
                # print(f'neg {neg_total}')
            if t not in palavras_intensidade:
                intens_mult = 0
            pointer = False

        if t in palavras_positivas:
            pos_found.append(t)
        if t in palavras_negativas:
            neg_found.append(t)
        if t in palavras_intensidade:
            intens_found.append(t)
            pointer = True
            intens_mult += 1

    pos_count = len(pos_found)
    pos_total += len(pos_found)
    neg_count = len(neg_found)
    neg_total += len(neg_found)
    intens_count = len(intens_found)

    return {
        "frase": frase,
        "pos_count": pos_count,
        "pos_total": pos_total,
        "neg_count": neg_count,
        "neg_total": neg_total,
        "intens_count": intens_count,
        "pos_list": pos_found,
        "neg_list": neg_found,
        "intens_list": intens_found,
        "sentimento": ("positivo" if pos_total > neg_total else "negativo" if neg_total > pos_total else "neutro")
    }

@app.route("/analisar", methods=["POST"])
def rota_analisar():
    payload = request.json or {}
    frase = payload.get("frase", "")
    if not frase.strip():
        return jsonify({"error": "Frase vazia"}), 400
    resultado = analisar_sentimento(frase)
    return jsonify(resultado)

@app.route("/adicionar", methods=["POST"])
def rota_adicionar():
    payload = request.json or {}
    palavra = (payload.get("palavra") or "").strip().lower()
    tipo = payload.get("tipo")  # "positiva", "negativa" ou "intensidade"
    if not palavra or tipo not in ("positiva", "negativa", "intensidade"):
        return jsonify({"error": "Dados inválidos"}), 400

    if tipo == "positiva":
        target = palavras_positivas
        label = "POSITIVAS"
    elif tipo == "negativa":
        target = palavras_negativas
        label = "NEGATIVAS"
    else:
        target = palavras_intensidade
        label = "INTENSIDADE"

    if palavra in target:
        return jsonify({"ok": False, "mensagem": f"Palavra já existe em {label}."}), 409

    target.append(palavra)
    return jsonify({"ok": True, "mensagem": f"Palavra '{palavra}' adicionada às {label}."})

@app.route("/estatisticas", methods=["GET"])
def rota_estatisticas():
    total_pos = len(palavras_positivas)
    total_neg = len(palavras_negativas)
    total_intens = len(palavras_intensidade)
    return jsonify({
        "total_positivas": total_pos,
        "total_negativas": total_neg,
        "total_intensidade": total_intens,
        "total_geral": total_pos + total_neg + total_intens,
        "positivas": palavras_positivas,
        "negativas": palavras_negativas,
        "intensidade": palavras_intensidade
    })

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
