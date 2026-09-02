"""Executa as consultas do Dashboard e salva os resultados em CSV."""

import argparse
import csv
import logging
import os
import sys

from db import add_db_args, connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SQL_1 = """WITH top_maiores AS (
    -- 1. Busca os 5 comentários mais úteis e com MAIOR avaliação
    SELECT 
        'Mais Úteis / Maiores Notas' AS tipo_grupo,
        review_id,
        product_id,
        rating,
        votes,
        helpful
    FROM reviews
    WHERE product_id = %s
    ORDER BY 
        helpful DESC, -- Critério 1: Mais votos úteis primeiro
        rating DESC   -- Critério 2 (Desempate): Maior nota primeiro
    LIMIT 5
),
top_menores AS (
    -- 2. Busca os 5 comentários mais úteis e com MENOR avaliação
    SELECT 
        'Mais Úteis / Menores Notas' AS tipo_grupo,
        review_id,
        product_id,
        rating,
        votes,
        helpful
    FROM reviews
    WHERE product_id = %s
      -- Evita duplicar registros caso o produto tenha menos de 10 reviews no total:
      AND review_id NOT IN (SELECT review_id FROM top_maiores)
    ORDER BY 
        helpful DESC, -- Critério 1: Mais votos úteis primeiro
        rating ASC    -- Critério 2 (Desempate): Menor nota primeiro
    LIMIT 5
)
-- 3. Une os dois resultados em uma única listagem
SELECT * FROM top_maiores
UNION ALL
SELECT * FROM top_menores;



"""

# Cada consulta: (arquivo de saída, título, SQL). Use %s para o ASIN quando necessário.
CONSULTAS = [
    ("q1_reviews.csv", "5 comentários mais úteis com maior e menor avaliação", SQL_1""),
    ("q2_similares.csv", "Produtos similares com melhor salesrank", ""),
    ("q3_evolucao_avaliacoes.csv", "Evolução diária das médias de avaliação", ""),
    ("q4_top_vendas_grupo.csv", "10 produtos líderes de venda por grupo", ""),
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
