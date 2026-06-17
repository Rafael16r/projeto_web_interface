# Visitar Guimarães — Portal de Turismo

Página web de turismo da cidade de Guimarães (Berço de Portugal, Património
Mundial da UNESCO), com frontend estático e um backend Flask que integra a
API Google Gemini e a Agenda Cultural oficial de [em.guimaraes.pt](https://em.guimaraes.pt/).

## Funcionalidades

- **Pontos de interesse dinâmicos** — servidos pela API (`/api/places`), com
  pesquisa tolerante a acentos e fallback local quando o servidor está offline.
- **Pesquisa inteligente (modo IA)** — o campo de pesquisa envia a consulta ao
  Google Gemini e devolve uma síntese sobre Guimarães (`/api/search`).
- **Agenda de eventos em tempo real** — extraída da Agenda Cultural oficial
  (em.guimaraes.pt) com cache de 30 minutos (`/api/events`). A pesquisa por data
  destaca os eventos do dia escolhido.
- **Chatbot "Guigas"** — guia turístico com IA (Gemini) e respostas locais de
  reserva (`/api/chat`).
- **Formulário de contacto** com moderação por IA (`/api/contact`).
- **Newsletter** guardada em SQLite (`/api/newsletter`).
- **Bilingue PT/EN** com alternador que persiste a escolha.

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Como correr

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Definir a chave da API Gemini (ficheiro .env na raiz)
#    GEMINI_API_KEY=<a-tua-chave>   (obtém em https://aistudio.google.com/apikey)

# 3. Criar a base de dados (apenas na primeira vez)
python database.py

# 4. Arrancar o servidor backend (porta 5000)
python app.py

# 5. Servir o frontend (noutro terminal, porta 3333)
python -m http.server 3333
```

Depois abre **http://localhost:3333** no browser.

> Sem o backend a página continua a funcionar com dados locais de reserva
> (pontos de interesse, eventos e respostas do chatbot), mas a pesquisa por IA
> e o chatbot com Gemini ficam indisponíveis.

## Estrutura

| Ficheiro/pasta   | Descrição |
|------------------|-----------|
| `index.html`     | Página única com todas as secções |
| `style.css`      | Estilos (tema, layout, responsividade) |
| `script.js`      | Lógica do frontend (i18n, API, formulários, chatbot) |
| `app.py`         | Servidor Flask com todos os endpoints |
| `database.py`    | Cria e popula a base de dados SQLite |
| `images/`, `img_pontos/` | Imagens (otimizadas para a web) |
