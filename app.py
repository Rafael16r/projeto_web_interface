"""
app.py — Servidor Flask para o projeto Visitar Guimarães.

Endpoints:
  GET  /api/places          → lista pontos de interesse (suporta ?q=&lang=)
  GET  /api/places/<id>     → detalhe de um ponto
  POST /api/contact         → valida/modera mensagem com Google Gemini
  POST /api/newsletter      → subscrição de newsletter (guarda em SQLite)

Dependências:
  pip install flask flask-cors google-generativeai

Variáveis de ambiente necessárias:
  GEMINI_API_KEY=<a-tua-chave>   (obtém em https://aistudio.google.com/apikey)

Como correr:
  python database.py      # apenas na primeira vez (cria a BD)
  python app.py
"""

import os
import sqlite3
import re

# Carrega variáveis do ficheiro .env (se existir)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

import unicodedata

from flask import Flask, jsonify, request
from flask_cors import CORS


def _normaliza(texto: str) -> str:
    """Remove acentos e converte para minúsculas (pesquisa tolerante)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )

# ── Google Gemini ──────────────────────────────────────────────────────────────
try:
    from google import genai as google_genai
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        _gemini_client = google_genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        _gemini_client = None
        GEMINI_AVAILABLE = False
        print("[AVISO] GEMINI_API_KEY não definida. A moderação de IA está desativada.")
except ImportError:
    _gemini_client = None
    GEMINI_AVAILABLE = False
    print("[AVISO] google-genai não instalado. Corre: pip install google-genai")

# ── Configuração ───────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "guimaraes.db")

app = Flask(__name__)
CORS(app)  # permite pedidos do frontend (localhost com ficheiro aberto)


# ── Utilitário BD ──────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ══════════════════════════════════════════════════════════════════════════════
#  GET /api/places
#  Parâmetros opcionais:
#    q    → pesquisa por título, descrição ou categoria (insensível a acentos)
#    lang → "pt" (default) ou "en"
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/places", methods=["GET"])
def get_places():
    lang = request.args.get("lang", "pt").lower()
    if lang not in ("pt", "en"):
        lang = "pt"

    query = request.args.get("q", "").strip().lower()

    conn = get_db()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT id, category_{lang} AS category, title_{lang} AS title,
               description_{lang} AS description, image_class, link, badge
        FROM places
        ORDER BY id
    """)

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    # Filtro tolerante a acentos e maiúsculas: "paco" encontra "Paço",
    # "santuario" encontra "Santuário" (o LIKE do SQLite não ignora acentos)
    if query:
        q = _normaliza(query)
        rows = [
            r for r in rows
            if q in _normaliza(f"{r['title']} {r['description']} {r['category']}")
        ]

    return jsonify({"results": rows, "total": len(rows), "lang": lang})


# ══════════════════════════════════════════════════════════════════════════════
#  GET /api/places/<id>
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/places/<int:place_id>", methods=["GET"])
def get_place(place_id):
    lang = request.args.get("lang", "pt").lower()
    if lang not in ("pt", "en"):
        lang = "pt"

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, category_{lang} AS category, title_{lang} AS title,
               description_{lang} AS description, image_class, link, badge
        FROM places WHERE id = ?
    """, (place_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Ponto de interesse não encontrado."}), 404

    return jsonify(dict(row))


# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/contact
#  Body JSON: { name, email, subject, message }
#  Resposta:  { ok, classification, reason, message }
#
#  O Gemini classifica a mensagem como:
#    "aprovada"  → conteúdo legítimo, avança normalmente
#    "suspeita"  → possível spam ou conteúdo inadequado
#    "rejeitada" → conteúdo claramente indevido/ofensivo
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    name    = str(data.get("name",    "")).strip()
    email   = str(data.get("email",   "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    # Validação básica dos campos obrigatórios
    if not all([name, email, subject, message]):
        return jsonify({
            "ok": False,
            "classification": "erro",
            "reason": "Todos os campos são obrigatórios.",
            "message": "Por favor preencha todos os campos."
        }), 400

    # Validação simples do email
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({
            "ok": False,
            "classification": "erro",
            "reason": "Endereço de email inválido.",
            "message": "Por favor introduza um email válido."
        }), 400

    # ── Moderação com Gemini ───────────────────────────────────────────────
    classification = "aprovada"
    reason         = "Mensagem válida."

    if GEMINI_AVAILABLE:
        try:
            prompt = f"""És um moderador de conteúdo para o website de turismo de Guimarães, Portugal.
Analisa a seguinte mensagem de contacto e classifica-a numa de três categorias:

- "aprovada"  → mensagem legítima relacionada com turismo, dúvidas, sugestões ou elogios
- "suspeita"  → possível spam, conteúdo ambíguo ou fora de contexto
- "rejeitada" → conteúdo ofensivo, ameaçador, publicitário ou claramente inadequado

Responde APENAS com um objeto JSON com dois campos:
  "classification": "aprovada" | "suspeita" | "rejeitada"
  "reason": uma frase curta a explicar a classificação (em português)

Dados da mensagem:
  Nome: {name}
  Email: {email}
  Assunto: {subject}
  Mensagem: {message}
"""
            response = _gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            raw = response.text.strip()

            # Extrai JSON mesmo que o modelo adicione markdown
            json_match = re.search(r"\{.*?\}", raw, re.DOTALL)
            if json_match:
                import json
                parsed = json.loads(json_match.group())
                classification = parsed.get("classification", "aprovada")
                reason         = parsed.get("reason", "")
            else:
                # Se não conseguir parsear, aprova por defeito
                classification = "aprovada"
                reason = "Não foi possível analisar automaticamente."

        except Exception as e:
            print(f"[Gemini] Erro: {e}")
            classification = "aprovada"
            reason = "Moderação temporariamente indisponível."

    # ── Construção da resposta ─────────────────────────────────────────────
    if classification == "rejeitada":
        return jsonify({
            "ok": False,
            "classification": classification,
            "reason": reason,
            "message": "A sua mensagem não pôde ser enviada por conter conteúdo inadequado."
        }), 422

    # Guarda a mensagem (aprovada ou suspeita) na base de dados
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                email           TEXT    NOT NULL,
                subject         TEXT    NOT NULL,
                message         TEXT    NOT NULL,
                classification  TEXT    NOT NULL DEFAULT 'aprovada',
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute(
            "INSERT INTO contact_messages (name, email, subject, message, classification) VALUES (?,?,?,?,?)",
            (name, email, subject, message, classification)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[contact] Erro ao guardar mensagem na BD: {e}")

    if classification == "suspeita":
        return jsonify({
            "ok": True,
            "classification": classification,
            "reason": reason,
            "message": "Mensagem recebida e em análise. Responderemos em breve."
        })

    # Aprovada
    return jsonify({
        "ok": True,
        "classification": classification,
        "reason": reason,
        "message": "Mensagem enviada com sucesso! Responderemos em breve."
    })


# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/chat
#  Body JSON: { message, lang }
#  Resposta:  { ok, reply }
#
#  Guia turístico virtual com Google Gemini. Se o Gemini não estiver
#  disponível, devolve ok=False e o frontend usa as respostas locais.
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    lang    = str(data.get("lang", "pt")).lower()
    if lang not in ("pt", "en"):
        lang = "pt"

    if not message:
        return jsonify({"ok": False, "reply": "", "message": "Mensagem vazia."}), 400

    if not GEMINI_AVAILABLE:
        return jsonify({"ok": False, "reply": "", "message": "IA indisponível."}), 503

    idioma = "português europeu" if lang == "pt" else "inglês"

    # Histórico recente da conversa (memória para perguntas de seguimento)
    history = data.get("history") or []
    contexto = ""
    if isinstance(history, list) and history:
        linhas = []
        for turno in history[-6:]:
            papel = "Visitante" if turno.get("role") == "user" else "Guigas"
            txt = str(turno.get("text", "")).strip()
            if txt:
                linhas.append(f"{papel}: {txt}")
        if linhas:
            contexto = "Conversa ate agora:\n" + "\n".join(linhas) + "\n\n"

    try:
        prompt = f"""Chamas-te Guigas e és o guia turístico virtual do website "Visitar Guimarães" (Guimarães, Portugal).
Responde à pergunta do visitante de forma simpática, útil e curta (máximo 3 frases),
em {idioma}. Mantém o contexto da conversa para perceberes perguntas de seguimento
(ex.: "e isso fica longe?" refere-se ao tema anterior). Fala apenas sobre Guimarães:
monumentos, história, gastronomia, eventos, alojamento e informação prática. Se a
pergunta não tiver relação com Guimarães ou turismo, diz educadamente que só podes
ajudar com temas sobre a cidade.

{contexto}Pergunta do visitante: {message}
"""
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        reply = (response.text or "").strip()
        if not reply:
            raise ValueError("Resposta vazia do Gemini")
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        print(f"[Gemini chat] Erro: {e}")
        return jsonify({"ok": False, "reply": "", "message": "IA temporariamente indisponível."}), 503


# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/newsletter
#  Body JSON: { email }
#  Resposta:  { ok, duplicate, message }
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/newsletter", methods=["POST"])
def newsletter():
    data  = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({
            "ok": False,
            "duplicate": False,
            "message": "Email inválido."
        }), 400

    conn = get_db()
    cur  = conn.cursor()

    # Garante que a tabela existe (cria se necessário)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS newsletter (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT    NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        cur.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "duplicate": False,
            "message": "Subscrição confirmada!"
        })
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "ok": True,
            "duplicate": True,
            "message": "Este email já está subscrito."
        })



# ══════════════════════════════════════════════════════════════════════════════
#  GET /api/events
#  Eventos extraídos em direto da Agenda Cultural de Guimarães
#  (https://em.guimaraes.pt/), com cache de 30 minutos para não
#  sobrecarregar o site de origem.
# ══════════════════════════════════════════════════════════════════════════════
EM_GUIMARAES_URL = "https://em.guimaraes.pt/"
_events_cache = {"quando": 0.0, "dados": []}

_MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


def _parse_em_events(html_texto):
    """Extrai os eventos dos blocos <li class="wm_link_container"> da agenda."""
    import html as html_mod

    eventos = []
    blocos = re.findall(r'<li class="wm_link_container.*?</li>', html_texto, re.DOTALL)
    for b in blocos:
        titulo = re.search(r'class="title widget_field[^>]*>.*?<h2>(.*?)</h2>', b, re.DOTALL)
        if not titulo:
            continue
        link  = re.search(r'class="linl_overlay"[^>]*href="([^"]+)"', b)
        dia   = re.search(r"<span class=dias>(\d+)", b)
        mes   = re.search(r"<span class=mes_extenso>([A-Za-zçÇãÃ]+)", b)
        hora  = re.search(r'class="timetable.*?<p>(.*?)</p>', b, re.DOTALL)
        local = re.search(r'class="descriptive_location.*?widget_value"><div>(.*?)</div>', b, re.DOTALL)
        cat   = re.search(r'class="primary_category".*?<span[^>]*>([^<]+)</span>', b, re.DOTALL)
        resumo = re.search(r'class="summary widget_field[^>]*>.*?<p>(.*?)</p>', b, re.DOTALL)

        def limpa(m):
            if not m:
                return ""
            texto = re.sub(r"<[^>]+>", " ", m.group(1))
            return html_mod.unescape(texto).strip()

        mes_nome = limpa(mes).lower()
        eventos.append({
            "title":    limpa(titulo).strip('"“”'),
            "day":      int(dia.group(1)) if dia else 0,
            "month":    _MESES_PT.get(mes_nome, 0),
            "month_label": limpa(mes)[:3].capitalize(),
            "time":     limpa(hora),
            "location": limpa(local),
            "category": limpa(cat),
            "summary":  limpa(resumo),
            "link":     EM_GUIMARAES_URL.rstrip("/") + link.group(1) if link else EM_GUIMARAES_URL,
        })
    return eventos


_FALLBACK_EVENTS = [
    {"day": 14, "month": 6,  "month_label": "Jun", "category": "Festas Religiosas",  "title": "Festas Gualterianas",        "summary": "As maiores festas de Guimarães, com cortejo histórico, fogo de artifício e animação na cidade.", "location": "Centro Histórico",     "time": "Todo o dia",      "link": "https://em.guimaraes.pt/"},
    {"day": 22, "month": 7,  "month_label": "Jul", "category": "Música",              "title": "GNRation Festival",          "summary": "Festival de música contemporânea e artes no espaço cultural GNRation.",                          "location": "GNRation",             "time": "21h00",           "link": "https://www.gnration.pt/"},
    {"day":  5, "month": 8,  "month_label": "Ago", "category": "Gastronomia",         "title": "Feira Medieval de Guimarães","summary": "Recriação histórica com mercado medieval, espectáculos e gastronomia típica.",                    "location": "Largo da Oliveira",    "time": "15h00 – 24h00",  "link": "https://em.guimaraes.pt/"},
    {"day": 18, "month": 9,  "month_label": "Set", "category": "Desporto",            "title": "Meia Maratona de Guimarães", "summary": "Corrida histórica pelas ruas e monumentos da cidade, aberta a todos os níveis.",                 "location": "Cidade de Guimarães",  "time": "09h00",           "link": "https://em.guimaraes.pt/"},
    {"day": 25, "month": 7,  "month_label": "Jul", "category": "Festas Religiosas",   "title": "Festas da Cidade",           "summary": "Celebrações anuais com concertos, fogo de artifício e animação de rua no centro histórico.",    "location": "Centro Histórico",     "time": "Todo o dia",      "link": "https://www.cm-guimaraes.pt/"},
    {"day":  1, "month": 12, "month_label": "Dez", "category": "Cultura",             "title": "Mercado de Natal",           "summary": "Mercado natalício com artesanato local, gastronomia típica e animação para toda a família.",    "location": "Praça de Santiago",    "time": "10h00 – 22h00",  "link": "https://em.guimaraes.pt/"},
]

@app.route("/api/events", methods=["GET"])
def get_events():
    import time
    import urllib.request

    # Usa a cache se tiver menos de 30 minutos
    if time.time() - _events_cache["quando"] > 1800 or not _events_cache["dados"]:
        try:
            pedido = urllib.request.Request(
                EM_GUIMARAES_URL, headers={"User-Agent": "Mozilla/5.0 (VisitarGuimaraes)"}
            )
            with urllib.request.urlopen(pedido, timeout=15) as resposta:
                html_texto = resposta.read().decode("utf-8", "replace")
            dados = _parse_em_events(html_texto)
            if dados:
                _events_cache["dados"] = dados
                _events_cache["quando"] = time.time()
        except Exception as erro:
            print(f"[events] Falha ao obter em.guimaraes.pt: {erro}")
            # Fallback garantido: usa os eventos estáticos da BD
            if not _events_cache["dados"]:
                return jsonify({
                    "results": _FALLBACK_EVENTS,
                    "total": len(_FALLBACK_EVENTS),
                    "source": "fallback",
                    "warning": "Agenda Cultural temporariamente indisponível — a mostrar eventos de destaque."
                })

    return jsonify({
        "results": _events_cache["dados"],
        "total": len(_events_cache["dados"]),
        "source": EM_GUIMARAES_URL,
    })



# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/search
#  Pesquisa inteligente ("modo IA") com Google Gemini: recebe a consulta
#  do visitante e devolve uma síntese útil sobre Guimarães.
#  Body JSON: { query, lang }   Resposta: { ok, answer, query }
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/search", methods=["POST"])
def search_ai():
    data  = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    lang  = str(data.get("lang", "pt")).lower()
    if lang not in ("pt", "en"):
        lang = "pt"

    if not query:
        return jsonify({"ok": False, "answer": "", "message": "Consulta vazia."}), 400

    if not GEMINI_AVAILABLE:
        return jsonify({"ok": False, "answer": "", "message": "IA indisponível."}), 503

    idioma = "português europeu" if lang == "pt" else "inglês"
    try:
        prompt = f"""És o motor de pesquisa inteligente do website "Visitar Guimarães" (Guimarães, Portugal).
Responde à pesquisa do visitante com uma síntese clara, útil e directa (máximo 4 frases), em {idioma}.
Foca-te apenas em Guimarães: monumentos, história, gastronomia, eventos, alojamento e informação prática.
Não uses formatação Markdown. Se a pesquisa não tiver relação com Guimarães ou turismo,
diz educadamente que só podes ajudar com temas sobre a cidade.

Pesquisa: {query}
"""
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        answer = (response.text or "").strip()
        if not answer:
            raise ValueError("Resposta vazia do Gemini")
        return jsonify({"ok": True, "answer": answer, "query": query})
    except Exception as e:
        print(f"[search-ai] Erro: {e}")
        return jsonify({"ok": False, "answer": "", "message": "IA temporariamente indisponível."}), 503


# ── Arranque ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("[INFO] Base de dados não encontrada. A criar automaticamente...")
        from database import init_db
        init_db()

    print("\nServidor Visitar Guimaraes a correr em http://localhost:5000\n")
    app.run(debug=True, port=5000)
