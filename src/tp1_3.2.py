"""Cria o esquema no PostgreSQL e carrega os dados do arquivo do SNAP."""

import argparse
import logging
import sys
import time
from pathlib import Path

from db import add_db_args, connect
from utils import iter_produtos, parse_produto

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
BATCH_SIZE = 2500


def criar_esquema(conn) -> None:
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def carregar(conn, caminho: str) -> int:
    """Lê o arquivo de entrada e povoa as relações. Retorna o total de produtos."""
    sql_products = """
        INSERT INTO products (product_id, asin, title, product_group, salesrank, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            asin = EXCLUDED.asin,
            title = EXCLUDED.title,
            product_group = EXCLUDED.product_group,
            salesrank = EXCLUDED.salesrank,
            status = EXCLUDED.status
    """

    sql_categories = """
        INSERT INTO categories (category_id, category_name)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """

    sql_product_category = """
        INSERT INTO product_category (product_id, category_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """

    sql_category_hierarchy = """
        INSERT INTO category_hierarchy (category_id, parent_category_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """

    sql_similar = """
        INSERT INTO similar_products (product_id, similar_asin)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """

    sql_reviews = """
        INSERT INTO reviews (product_id, review_date, customer_id, rating, votes, helpful)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    total_produtos = 0
    lote_produtos = []
    lote_categorias = []
    lote_hierarquias = []
    lote_product_categories = []
    lote_similares = []
    lote_reviews = []

    def gravar_lote(cur):
        if not lote_produtos:
            return
        cur.executemany(sql_products, lote_produtos)
        cur.executemany(sql_categories, lote_categorias)
        cur.executemany(sql_category_hierarchy, lote_hierarquias)
        cur.executemany(sql_product_category, lote_product_categories)
        cur.executemany(sql_similar, lote_similares)
        cur.executemany(sql_reviews, lote_reviews)
        conn.commit()
        lote_produtos.clear()
        lote_categorias.clear()
        lote_hierarquias.clear()
        lote_product_categories.clear()
        lote_similares.clear()
        lote_reviews.clear()

    with conn.cursor() as cur:
        for bloco in iter_produtos(caminho):
            produto = parse_produto(bloco)
            product_id = produto.get("id")
            if product_id is None:
                continue

            lote_produtos.append(
                (
                    product_id,
                    produto.get("asin"),
                    produto.get("title"),
                    produto.get("group"),
                    produto.get("salesrank"),
                    produto.get("status", "active"),
                )
            )

            for caminho_categoria in produto.get("categorias_detalhe") or []:
                for nome, categoria_id in caminho_categoria:
                    lote_categorias.append((categoria_id, nome))

                for (_, pai_id), (_, filho_id) in zip(caminho_categoria, caminho_categoria[1:]):
                    lote_hierarquias.append((filho_id, pai_id))

                for _, categoria_id in caminho_categoria:
                    lote_product_categories.append((product_id, categoria_id))

            for similar_asin in produto.get("lista_similares", []):
                lote_similares.append((product_id, similar_asin))

            for review in produto.get("reviews", []):
                review_date = review.get("date")
                if review_date is not None:
                    lote_reviews.append(
                        (
                            product_id,
                            review_date,
                            review.get("customer"),
                            review.get("rating"),
                            review.get("votes", 0),
                            review.get("helpful", 0),
                        )
                    )

            total_produtos += 1
            if total_produtos % BATCH_SIZE == 0:
                gravar_lote(cur)
                logging.info("%d produtos processados", total_produtos)

        gravar_lote(cur)

    return total_produtos


def main() -> int:
    parser = argparse.ArgumentParser(description="Criação do esquema e carga dos dados")
    add_db_args(parser)
    parser.add_argument("--input", required=True, help="arquivo SNAP dentro do contêiner")
    args = parser.parse_args()

    inicio = time.time()
    with connect(args) as conn:
        logging.info("criando esquema")
        criar_esquema(conn)
        logging.info("carregando %s", args.input)
        total = carregar(conn, args.input)
        conn.commit()
    logging.info("carga concluída: %d produtos em %.1fs", total, time.time() - inicio)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logging.exception("falha na carga")
        sys.exit(1)
