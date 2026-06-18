


# Visitar Guimarães — Portal de Turismo Inteligente

Portal turístico dedicado à cidade de **Guimarães**, o Berço de Portugal e Património Mundial da UNESCO. O projeto combina um **frontend estático responsivo** com um **backend Flask**, integrando pesquisa inteligente com **Google Gemini**, agenda cultural em tempo real, chatbot turístico, newsletter e formulários de contacto.

Esta versão inclui uma interface visual renovada, com identidade gráfica mais consistente, componentes interativos, estados de carregamento, animações suaves e melhor adaptação a dispositivos móveis. Sim, finalmente um README que não parece ter sido escrito às 3 da manhã por alguém a lutar contra o `git push`.

---

## Índice

- [Visão geral](#visão-geral)
- [Principais funcionalidades](#principais-funcionalidades)
- [Novidades desta versão](#novidades-desta-versão)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Requisitos](#requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Design e interface](#design-e-interface)
- [Responsividade](#responsividade)
- [Modo offline e fallback](#modo-offline-e-fallback)
- [Resolução de problemas](#resolução-de-problemas)
- [Melhorias futuras](#melhorias-futuras)
- [Autor](#autor)

---

## Visão geral

O **Visitar Guimarães** é uma aplicação web criada para apoiar turistas, visitantes e interessados na cidade de Guimarães. A plataforma apresenta pontos turísticos, atividades, gastronomia, alojamento, eventos culturais, mapa, ligações úteis, formulário de contacto e um chatbot inteligente chamado **Guigas**.

O projeto foi desenvolvido com foco em:

- navegação simples e elegante;
- conteúdo turístico organizado por secções;
- pesquisa inteligente com IA;
- integração com eventos reais da agenda cultural;
- experiência bilingue em português e inglês;
- layout responsivo para computador, tablet e telemóvel;
- funcionamento parcial mesmo sem backend ativo.

---

## Principais funcionalidades

### Pontos de interesse dinâmicos

Os pontos turísticos são carregados através do endpoint `/api/places`, com pesquisa tolerante a acentos e suporte a dados locais de reserva quando o servidor não está disponível.

### Pesquisa inteligente com IA

O campo de pesquisa permite enviar consultas ao backend, que utiliza o **Google Gemini** para gerar respostas contextualizadas sobre Guimarães através do endpoint `/api/search`.

### Agenda cultural em tempo real

A aplicação obtém eventos da Agenda Cultural oficial de Guimarães através do endpoint `/api/events`, com cache para evitar pedidos excessivos. A pesquisa por data destaca automaticamente eventos correspondentes.

### Chatbot turístico “Guigas”

O chatbot funciona como guia turístico virtual, respondendo a perguntas sobre locais, eventos, gastronomia, alojamento e sugestões de visita. Quando a IA não está disponível, pode recorrer a respostas locais de reserva.

### Formulário de contacto

Inclui validação visual, indicação de campos obrigatórios e integração com moderação por IA através do endpoint `/api/contact`.

### Newsletter

Permite recolher subscrições de visitantes e guardar os dados em SQLite através do endpoint `/api/newsletter`.

### Interface bilingue

O site suporta português e inglês, com alternador de idioma e persistência da escolha do utilizador.

---

## Novidades desta versão

Esta versão do código introduz uma camada visual mais completa e profissional no `style.css`, incluindo:

- novo sistema de variáveis CSS para cores, sombras, raios e transições;
- hero visual com imagem de fundo, sobreposição escura e pesquisa integrada;
- painel de sugestões na pesquisa principal;
- componente visual para respostas da IA;
- cartões com efeitos de hover e destaque visual;
- secções para história, galeria, gastronomia, alojamento e atividades;
- lightbox para visualização de imagens;
- chatbot com sugestões rápidas, animação de escrita e efeito especial no botão do Guigas;
- destaque visual para eventos pesquisados por data;
- formulário de contacto com validação e mensagens de sucesso;
- notas de privacidade e estados de integração da API;
- footer com redes sociais e efeitos de hover;
- botão “voltar ao topo”;
- animações de entrada e microinterações;
- regras responsivas para ecrãs médios, tablets e telemóveis.

---

## Tecnologias utilizadas

### Frontend

- HTML5
- CSS3
- JavaScript
- Google Fonts
- Layout responsivo com CSS Grid e Flexbox
- Animações CSS
- Componentes interativos no navegador

### Backend

- Python 3.10+
- Flask
- SQLite
- Google Gemini API
- Integração com a Agenda Cultural oficial de Guimarães

### Dados e integrações

- Base de dados local SQLite
- Dados locais de fallback
- API própria em Flask
- Chave Gemini configurada por variável de ambiente

---

## Requisitos

Antes de executar o projeto, garante que tens instalado:

- Python 3.10 ou superior;
- `pip`;
- navegador moderno;
- ficheiro `requirements.txt` com as dependências do backend;
- chave da API Google Gemini, se quiseres usar as funcionalidades de IA.

---

## Instalação e execução

### 1. Clonar ou abrir o projeto

```bash
git clone <url-do-repositorio>
cd <nome-da-pasta-do-projeto>
```

Se já tens o projeto localmente, basta abrir a pasta no terminal.

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar a chave Gemini

Cria um ficheiro `.env` na raiz do projeto:

```env
GEMINI_API_KEY=<a-tua-chave-da-api>
```

A chave pode ser obtida no Google AI Studio.

### 4. Criar a base de dados

Executa este comando apenas na primeira utilização ou quando precisares recriar a base de dados:

```bash
python database.py
```

### 5. Iniciar o backend Flask

```bash
python app.py
```

Por defeito, o backend fica disponível em:

```text
http://localhost:5000
```

### 6. Servir o frontend

Noutro terminal, executa:

```bash
python -m http.server 3333
```

Depois abre no navegador:

```text
http://localhost:3333
```

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---:|---|
| `GEMINI_API_KEY` | Sim, para IA | Chave usada para ativar pesquisa inteligente, chatbot com IA e moderação. |

Exemplo de ficheiro `.env`:

```env
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Endpoints da API

| Método | Endpoint | Finalidade |
|---|---|---|
| `GET` | `/api/places` | Devolve pontos de interesse turísticos. |
| `GET` / `POST` | `/api/search` | Envia uma pesquisa para o modo IA. |
| `GET` | `/api/events` | Obtém eventos culturais atualizados. |
| `POST` | `/api/chat` | Envia mensagens para o chatbot Guigas. |
| `POST` | `/api/contact` | Processa e modera mensagens do formulário de contacto. |
| `POST` | `/api/newsletter` | Guarda subscrições da newsletter em SQLite. |

> A disponibilidade exata dos métodos depende da implementação no ficheiro `app.py`.

---

## Estrutura do projeto

```text
.
├── index.html              # Página principal com todas as secções do portal
├── style.css               # Estilos globais, layout, responsividade e animações
├── script.js               # Lógica do frontend, i18n, API, pesquisa, chatbot e formulários
├── app.py                  # Servidor Flask e endpoints da aplicação
├── database.py             # Criação e inicialização da base de dados SQLite
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente locais
├── images/                 # Imagens gerais do site
└── img_pontos/             # Imagens dos pontos turísticos
```

---

## Design e interface

O `style.css` foi estruturado em blocos para facilitar manutenção e evolução do projeto.

### Sistema visual

A interface usa variáveis CSS globais para manter consistência:

```css
:root {
  --primary: #8B4513;
  --accent: #C9A84C;
  --dark: #1A1A2E;
  --light: #F7F4EF;
  --radius: 12px;
}
```

### Componentes principais

- Navbar fixa com comportamento ao fazer scroll;
- menu mobile com botão hambúrguer;
- hero fullscreen com pesquisa;
- painel de sugestões;
- cartões de pontos turísticos;
- grelha de atividades;
- banner CTA;
- secção de gastronomia;
- lista de eventos;
- cartões de hotéis;
- mapa e informações úteis;
- galeria com lightbox;
- formulário de contacto;
- newsletter;
- footer com redes sociais;
- chatbot flutuante.

### Microinterações

Foram adicionados efeitos visuais para melhorar a perceção de qualidade:

- hover em cartões;
- animações de entrada;
- botões com transições suaves;
- indicador de escrita no chatbot;
- destaque animado para eventos;
- tooltip no botão do Guigas;
- efeito de escala em imagens;
- botão de voltar ao topo.

---

## Responsividade

O layout adapta-se automaticamente a diferentes tamanhos de ecrã.

### Breakpoints principais

| Largura | Comportamento |
|---:|---|
| até `1024px` | Grelhas reduzem colunas e reorganizam cartões grandes. |
| até `768px` | Menu mobile, pesquisa vertical, grelhas em coluna única e formulário adaptado. |
| até `480px` | Títulos e elementos principais são ajustados para telemóveis pequenos. |

---

## Modo offline e fallback

O portal continua parcialmente funcional mesmo quando o backend não está ativo:

- pontos de interesse podem usar dados locais;
- eventos podem recorrer a dados de reserva;
- chatbot pode devolver respostas locais;
- interface, navegação e secções estáticas continuam disponíveis.

As funcionalidades que dependem diretamente do backend ou da API Gemini podem ficar indisponíveis:

- pesquisa inteligente com IA;
- chatbot com respostas geradas por Gemini;
- moderação automática do formulário;
- newsletter ligada à base de dados.

---

## Resolução de problemas

### O frontend abre, mas a IA não responde

Confirma se:

- o backend Flask está ativo em `http://localhost:5000`;
- o ficheiro `.env` existe;
- `GEMINI_API_KEY` está corretamente configurada;
- as dependências foram instaladas com `pip install -r requirements.txt`.

### A base de dados não existe

Executa:

```bash
python database.py
```

### O navegador mostra erros de CORS ou API

Verifica se o frontend e o backend estão a correr nas portas esperadas:

```text
Frontend: http://localhost:3333
Backend:  http://localhost:5000
```

### As imagens não aparecem

Confirma se as pastas `images/` e `img_pontos/` existem e se os caminhos usados no HTML e no JavaScript estão corretos.

---

## Melhorias futuras

Sugestões para próximas versões:

- painel administrativo para gerir pontos turísticos e eventos;
- autenticação para equipa de gestão;
- integração com mapas interativos mais avançados;
- sistema de favoritos para visitantes;
- exportação de roteiros turísticos em PDF;
- histórico de conversas com o Guigas;
- testes automatizados para API e frontend;
- deploy em ambiente cloud;
- otimização avançada de imagens;
- melhoria de acessibilidade com foco em leitores de ecrã.

---

## Autores

20241781 Nelson Moreira
20241964 João Vieira
20241204 Rafael Resende
20241323 Iaia Baldé


Projeto académico/desenvolvimento web: **Visitar Guimarães — Portal de Turismo Inteligente**.

Desenvolvido com foco em turismo digital, experiência do utilizador, integração com IA e apresentação moderna de conteúdo cultural.

---

