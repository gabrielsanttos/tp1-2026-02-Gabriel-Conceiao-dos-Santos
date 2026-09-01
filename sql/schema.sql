-- =====================================================================
-- TP1 - Bancos de Dados I - UFAM
-- Esquema relacional para o "Amazon product co-purchasing network
-- metadata" (SNAP).
--
-- Projeto bottom-up: partimos dos atributos do arquivo de entrada,
-- identificamos as dependências funcionais (DFs) e decompomos até que
-- cada relação esteja em BCNF (ou 3FN quando aceitar uma dependência
-- transitiva controlada é preferível à perda da FK correspondente).
--
-- Resumo das DFs identificadas e da decomposição (documentar com mais
-- detalhe no PDF tp1_3.1.pdf):
--
-- 1) products
--    product_id -> asin, title, product_group, salesrank, status
--    asin       -> product_id, title, product_group, salesrank, status
--    Duas chaves candidatas (product_id e asin); nenhuma DF parcial ou
--    transitiva sobrando -> BCNF.
--
-- 2) categories
--    category_id -> category_name
--    Chave = category_id. BCNF.
--    (No arquivo original, o mesmo par nome/id é repetido em milhares
--    de produtos; extraí-lo para uma relação própria elimina essa
--    redundância, que era a violação de 3FN presente em "guardar a
--    categoria como texto dentro do produto".)
--
-- 3) category_hierarchy
--    Relação apenas de chaves (category_id, parent_category_id), sem
--    atributos não-chave -> trivialmente BCNF. É N:N porque, no
--    dataset, um mesmo category_id ocasionalmente aparece sob mais de
--    um "pai" em caminhos diferentes (a hierarquia não é uma árvore
--    estrita).
--
-- 4) product_category
--    Relação de associação produto x categoria (chave composta),
--    sem atributos não-chave -> trivialmente BCNF. Um produto é
--    ligado a TODOS os nós do(s) caminho(s) de categoria em que
--    aparece (não só a folha), pois ele de fato pertence a cada
--    categoria ancestral também.
--
-- 5) similar_products
--    Relação de associação (product_id, similar_asin), sem atributos
--    não-chave -> BCNF. Guardamos o ASIN (não o product_id) porque é
--    assim que o arquivo referencia produtos similares, e alguns
--    ASINs citados não aparecem como produto completo no arquivo;
--    por isso NÃO há FK para products aqui (constraint fraca, tratada
--    na aplicação/consultas).
--
-- 6) reviews
--    review_id -> product_id, review_date, customer_id, rating,
--                 votes, helpful
--    review_id é uma chave substituta (surrogate): o candidato natural
--    (product_id, customer_id, review_date) não é garantidamente
--    único no arquivo (o mesmo cliente pode comentar o mesmo produto
--    mais de uma vez no mesmo dia) então preferimos a chave sintética
--    para não impor uma restrição indevida aos dados de entrada.
--    Nenhuma DF transitiva: BCNF.
-- =====================================================================

DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS similar_products CASCADE;
DROP TABLE IF EXISTS product_category CASCADE;
DROP TABLE IF EXISTS category_hierarchy CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    product_id     INTEGER PRIMARY KEY,        -- campo "Id" do arquivo
    asin           VARCHAR(20) UNIQUE NOT NULL,
    title          TEXT,
    product_group  VARCHAR(50),                 -- Book, Music, DVD, Video...
    salesrank      INTEGER,                      -- menor = mais vendido; -1/NULL = sem ranking
    status         VARCHAR(20) NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active', 'discontinued'))
);

CREATE TABLE categories (
    category_id    INTEGER PRIMARY KEY,          -- id entre colchetes, ex: Books[283155]
    category_name  TEXT NOT NULL
);

CREATE TABLE category_hierarchy (
    category_id         INTEGER NOT NULL REFERENCES categories(category_id),
    parent_category_id  INTEGER NOT NULL REFERENCES categories(category_id),
    PRIMARY KEY (category_id, parent_category_id)
);

CREATE TABLE product_category (
    product_id   INTEGER NOT NULL REFERENCES products(product_id),
    category_id  INTEGER NOT NULL REFERENCES categories(category_id),
    PRIMARY KEY (product_id, category_id)
);

CREATE TABLE similar_products (
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    similar_asin  VARCHAR(20) NOT NULL,
    PRIMARY KEY (product_id, similar_asin)
);

CREATE TABLE reviews (
    review_id     BIGSERIAL PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    review_date   DATE NOT NULL,
    customer_id   VARCHAR(20) NOT NULL,
    rating        SMALLINT NOT NULL CHECK (rating BETWEEN 0 AND 5),
    votes         INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
    helpful       INTEGER NOT NULL DEFAULT 0 CHECK (helpful >= 0)
);

-- Índices para as consultas do Dashboard (Seção 3 do enunciado)
CREATE INDEX idx_products_asin        ON products(asin);
CREATE INDEX idx_products_group_rank  ON products(product_group, salesrank);
CREATE INDEX idx_product_category_cat ON product_category(category_id);
CREATE INDEX idx_similar_asin         ON similar_products(similar_asin);
CREATE INDEX idx_reviews_product      ON reviews(product_id, helpful DESC, rating);
CREATE INDEX idx_reviews_date         ON reviews(product_id, review_date);
CREATE INDEX idx_reviews_customer     ON reviews(customer_id);
