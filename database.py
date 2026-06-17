"""
database.py — Cria e popula a base de dados SQLite para o projeto Visitar Guimarães.
Executa este script uma vez antes de iniciar o servidor: python database.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "guimaraes.db")


# Os 12 pontos de interesse (textos em PT e EN) carregados para a tabela "places"
PLACES = [
    {
        "category_pt": "Palácios",
        "category_en": "Palaces",
        "title_pt": "Paço dos Duques de Bragança",
        "title_en": "Palace of the Dukes of Braganza",
        "description_pt": "Construído no século XV pelo 1.º Duque de Bragança, é um dos palácios medievais mais marcantes de Portugal.",
        "description_en": "Built in the 15th century by the 1st Duke of Braganza, it is one of Portugal's most striking medieval palaces.",
        "image_class": "image-paco-duques",
        "link": "https://pacodosduques.gov.pt/",
        "badge": "Imperdível",
    },
    {
        "category_pt": "Monumentos",
        "category_en": "Monuments",
        "title_pt": "Castelo de Guimarães",
        "title_en": "Guimarães Castle",
        "description_pt": "Símbolo da fundação de Portugal e um dos monumentos mais icónicos da cidade.",
        "description_en": "A symbol of Portugal's foundation and one of the city's most iconic monuments.",
        "image_class": "image-castelo-guimaraes",
        "link": "https://pacodosduques.gov.pt/monumentos/castelo-de-guimaraes/",
        "badge": None,
    },
    {
        "category_pt": "Centro Histórico",
        "category_en": "Historic Centre",
        "title_pt": "Centro Histórico",
        "title_en": "Historic Centre",
        "description_pt": "Ruas medievais, praças animadas e um ambiente único que convida a explorar a pé.",
        "description_en": "Medieval streets, lively squares and a unique atmosphere that invites you to explore on foot.",
        "image_class": "image-centro-historico",
        "link": "https://unescoportugal.mne.gov.pt/pt/temas/proteger-o-nosso-patrimonio-e-promover-a-criatividade/patrimonio-mundial-em-portugal/centro-historico-de-guimaraes",
        "badge": "UNESCO",
    },
    {
        "category_pt": "Igrejas",
        "category_en": "Churches",
        "title_pt": "Igreja da Oliveira",
        "title_en": "Oliveira Church",
        "description_pt": "Um dos marcos religiosos e históricos mais importantes do coração da cidade.",
        "description_en": "One of the most important religious and historical landmarks in the heart of the city.",
        "image_class": "image-igreja-oliveira",
        "link": "https://pt.wikipedia.org/wiki/Categoria:Igrejas_em_Guimar%C3%A3es",
        "badge": None,
    },
    {
        "category_pt": "Museus",
        "category_en": "Museums",
        "title_pt": "Museu Martins Sarmento",
        "title_en": "Martins Sarmento Museum",
        "description_pt": "Coleção arqueológica de referência para conhecer melhor a herança castreja e romana da região.",
        "description_en": "A landmark archaeological collection to better understand the region's Celtic and Roman heritage.",
        "image_class": "image-museu-martins",
        "link": "https://www.museusemonumentos.pt/pt/museus-e-monumentos",
        "badge": None,
    },
    {
        "category_pt": "Natureza",
        "category_en": "Nature",
        "title_pt": "Serra da Penha",
        "title_en": "Penha Mountain",
        "description_pt": "Suba de teleférico ou a pé e descubra uma das melhores vistas panorâmicas sobre Guimarães.",
        "description_en": "Go up by cable car or on foot and enjoy one of the best panoramic views over Guimarães.",
        "image_class": "image-serra-penha",
        "link": "https://www.penhaguimaraes.com/pt/",
        "badge": None,
    },
    {
        "category_pt": "Museus",
        "category_en": "Museums",
        "title_pt": "Museu Alberto Sampaio",
        "title_en": "Alberto Sampaio Museum",
        "description_pt": "Instalado no antigo convento da Colegiada, alberga peças de ourivesaria, escultura e têxteis medievais.",
        "description_en": "Housed in the former collegiate convent, it holds outstanding medieval goldwork, sculpture and textiles.",
        "image_class": "image-museu-alberto",
        "link": "https://www.museusemonumentos.pt/pt/museus-e-monumentos",
        "badge": None,
    },
    {
        "category_pt": "Museus",
        "category_en": "Museums",
        "title_pt": "Centro Internacional das Artes José de Guimarães",
        "title_en": "José de Guimarães International Arts Centre",
        "description_pt": "Inaugurado em 2012 na Plataforma das Artes e da Criatividade, dedica-se à arte contemporânea e à coleção do artista José de Guimarães.",
        "description_en": "Opened in 2012 at the Platform of Arts and Creativity, it is devoted to contemporary art and the collection of the artist José de Guimarães.",
        "image_class": "image-ciajg",
        "link": "https://www.ciajg.pt/sobre/",
        "badge": None,
    },
    {
        "category_pt": "Monumentos",
        "category_en": "Monuments",
        "title_pt": "Muralhas Medievais",
        "title_en": "Medieval Walls",
        "description_pt": "Troços das antigas muralhas que cercavam a cidade medieval, testemunhas silenciosas de séculos de história.",
        "description_en": "Remaining sections of the walls that once enclosed the medieval city, silent witnesses to centuries of history.",
        "image_class": "image-muralhas",
        "link": "http://www.monumentos.gov.pt/site/app_pagesuser/SIPA.aspx?id=1048",
        "badge": None,
    },
    {
        "category_pt": "Igrejas",
        "category_en": "Churches",
        "title_pt": "Santuário da Penha",
        "title_en": "Penha Sanctuary",
        "description_pt": "Imponente santuário em granito no alto da Penha, lugar de peregrinação com vistas magníficas sobre a cidade.",
        "description_en": "An imposing granite sanctuary at the top of Penha hill, a pilgrimage site with magnificent views over the city.",
        "image_class": "image-santuario-penha",
        "link": "https://pt.wikipedia.org/wiki/Santu%C3%A1rio_da_Penha",
        "badge": None,
    },
    {
        "category_pt": "Monumentos",
        "category_en": "Monuments",
        "title_pt": "Padrão do Salado",
        "title_en": "Salado Monument",
        "description_pt": "Monumento gótico do século XIV no Largo da Oliveira, que comemora a vitória cristã na Batalha do Salado.",
        "description_en": "A 14th-century Gothic monument in Largo da Oliveira commemorating the Christian victory at the Battle of Salado.",
        "image_class": "image-padrao-salado",
        "link": "https://blog.araduca.pt/search/label/Monumentos",
        "badge": None,
    },
    {
        "category_pt": "Praças",
        "category_en": "Squares",
        "title_pt": "Campo da Feira",
        "title_en": "Campo da Feira",
        "description_pt": "Hoje Largo República do Brasil, o antigo campo de feiras da cidade encanta com os seus jardins floridos e a vista para a Igreja dos Santos Passos.",
        "description_en": "Now Largo República do Brasil, the city's old fairground charms visitors with flower-filled gardens and views of the Santos Passos Church.",
        "image_class": "image-campo-feira",
        "link": "https://blog.araduca.pt/2016/05/guimaraes-e-o-seu-campo-da-feira-em-1864.html?m=1",
        "badge": None,
    },
    {
        "category_pt": "Praças",
        "category_en": "Squares",
        "title_pt": "Largo da Oliveira",
        "title_en": "Largo da Oliveira",
        "description_pt": "O coração pulsante de Guimarães: esplanadas, o Padrão do Salado e a fachada da Igreja da Oliveira criam um cenário medieval único.",
        "description_en": "The beating heart of Guimarães: terraces, the Salado Monument and the façade of Oliveira Church create a unique medieval setting.",
        "image_class": "image-largo-oliveira",
        "link": "https://www.visitguimaraes.travel/descobrir-guimaraes/centro-urbano/centro-historico-patrimonio-mundial/conheca-o-centro-historico-de-guimaraes/geo_artigo/largo-da-oliveira",
        "badge": None,
    },
    {
        "category_pt": "Praças",
        "category_en": "Squares",
        "title_pt": "Praça de Santiago",
        "title_en": "Santiago Square",
        "description_pt": "Rodeada de casas medievais, esta praça animada é o centro da vida noturna e gastronómica do centro histórico de Guimarães.",
        "description_en": "Surrounded by medieval houses, this lively square is the hub of nightlife and gastronomy in Guimarães's historic centre.",
        "image_class": "image-praca-santiago",
        "link": "https://www.visitguimaraes.travel/descobrir-guimaraes/centro-urbano/centro-historico-patrimonio-mundial/conheca-o-centro-historico-de-guimaraes",
        "badge": None,
    },
]


# Cria (ou recria) a base de dados SQLite e insere os pontos de interesse
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS places")

    cur.execute("""
        CREATE TABLE places (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category_pt TEXT    NOT NULL,
            category_en TEXT    NOT NULL,
            title_pt    TEXT    NOT NULL,
            title_en    TEXT    NOT NULL,
            description_pt TEXT NOT NULL,
            description_en TEXT NOT NULL,
            image_class TEXT    NOT NULL,
            link        TEXT,
            badge       TEXT
        )
    """)

    # Tabela para guardar mensagens de contacto moderadas pela IA
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

    cur.executemany("""
        INSERT INTO places
            (category_pt, category_en, title_pt, title_en,
             description_pt, description_en, image_class, link, badge)
        VALUES
            (:category_pt, :category_en, :title_pt, :title_en,
             :description_pt, :description_en, :image_class, :link, :badge)
    """, PLACES)

    conn.commit()
    conn.close()
    print(f"Base de dados criada em '{DB_PATH}' com {len(PLACES)} pontos de interesse.")


if __name__ == "__main__":
    init_db()
