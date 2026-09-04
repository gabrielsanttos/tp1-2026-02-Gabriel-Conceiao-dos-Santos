"""Executa as consultas do Dashboard e salva os resultados em CSV."""

import argparse
import csv
import logging
import os
import sys

from db import add_db_args, connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SQL_1 = """WITH produto AS (
    SELECT product_id FROM products WHERE asin = %s
),
top_maiores AS (
    SELECT 
        'Mais Úteis / Maiores Notas' AS tipo_grupo,
        review_id,
        product_id,
        review_date,
        customer_id,
        rating,
        votes,
        helpful
    FROM reviews
    WHERE product_id = (SELECT product_id FROM produto)
    ORDER BY 
        helpful DESC,
        rating DESC
    LIMIT 5
),
top_menores AS (
    SELECT 
        'Mais Úteis / Menores Notas' AS tipo_grupo,
        review_id,
        product_id,
        review_date,
        customer_id,
        rating,
        votes,
        helpful
    FROM reviews
    WHERE product_id = (SELECT product_id FROM produto)
      AND review_id NOT IN (SELECT review_id FROM top_maiores)
    ORDER BY 
        helpful DESC,
        rating ASC
    LIMIT 5
)
SELECT * FROM top_maiores
UNION ALL
SELECT * FROM top_menores;
"""

SQL_2 = """WITH produto AS (
    SELECT product_id, salesrank
    FROM products
    WHERE asin = %s
)
SELECT
    p2.asin AS similar_asin,
    p2.title,
    p2.product_group,
    p2.salesrank
FROM similar_products sp
JOIN produto ON sp.product_id = produto.product_id
JOIN products p2 ON p2.asin = sp.similar_asin
WHERE produto.salesrank IS NOT NULL
  AND p2.salesrank IS NOT NULL
  AND p2.salesrank < produto.salesrank
ORDER BY p2.salesrank ASC; 

"""

SQL_3 = """WITH produto AS (SELECT product_id FROM products WHERE asin = %s),
medias_diarias AS (
        SELECT review_date, COUNT(*) AS total_reviews, AVG(rating) AS media_dia
         FROM reviews
        WHERE product_id = (SELECT product_id FROM produto)
        GROUP BY review_date
        ORDER BY review_date
)
SELECT review_date, total_reviews, media_dia,
        AVG(media_dia) OVER (ORDER BY review_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS media_acumulada
FROM medias_diarias
ORDER BY review_date;  

"""

SQL_4 = """ WITH top_por_grupo AS (
    SELECT product_group,
            product_id,
            asin,
            title,
            salesrank,
            ROW_NUMBER() OVER (PARTITION BY product_group ORDER BY salesrank ASC) AS numero_linha
    FROM products
    WHERE salesrank IS NOT NULL AND salesrank > 0)
        SELECT *
        FROM top_por_grupo
        WHERE numero_linha <=10
        ORDER BY product_group, numero_linha;

"""

# Cada consulta: (arquivo de saída, título, SQL). Use %s para o ASIN quando necessário.
CONSULTAS = [
    ("q1_reviews.csv", "5 comentários mais úteis com maior e menor avaliação", SQL_1),
    ("q2_similares.csv", "Produtos similares com melhor salesrank", SQL_2),
    ("q3_evolucao_avaliacoes.csv", "Evolução diária das médias de avaliação", SQL_3),
    ("q4_top_vendas_grupo.csv", "10 produtos líderes de venda por grupo", SQL_4),
    ("q5_produtos_media_uteis_positivas.csv", "10 produtos com maior média de avaliações úteis positivas", ""),
    ("q6_categorias_media_uteis_positivas.csv", "5 categorias com maior média de avaliações úteis positivas", ""),
    ("q7_clientes_comentarios_grupo.csv", "10 clientes que mais comentaram por grupo", ""),
]


def executar(cur, sql: str, asin: str):
    params = (asin,) * sql.count("%s")
    cur.execute(sql, params)
    return [d.name for d in cur.description], cur.fetchall()


def main() -> int:
    parser = argparse.ArgumentParser(description="Dashboard de consultas SQL")
    add_db_args(parser)
    parser.add_argument("--product-asin", required=True)
    parser.add_argument("--output", default="/app/out")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    with connect(args) as conn, conn.cursor() as cur:
        for arquivo, titulo, sql in CONSULTAS:
            if not sql:
                raise NotImplementedError(f"consulta não implementada: {arquivo}")
            colunas, linhas = executar(cur, sql, args.product_asin)
            print(f"\n== {titulo} ({len(linhas)} linhas)")
            print(" | ".join(colunas))
            for linha in linhas[:10]:
                print(" | ".join(str(v) for v in linha))
            destino = os.path.join(args.output, arquivo)
            with open(destino, "w", newline="", encoding="utf-8") as f:
                escritor = csv.writer(f)
                escritor.writerow(colunas)
                escritor.writerows(linhas)
            logging.info("gravado %s", destino)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logging.exception("falha no dashboard")
        sys.exit(1)
