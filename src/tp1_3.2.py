"""Cria o esquema no PostgreSQL e carrega os dados do arquivo do SNAP."""

import argparse
import logging
import sys
import time

from db import add_db_args, connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def criar_esquema(conn) -> None:
    """Cria as relações, chaves e restrições. TODO: implementar."""
    raise NotImplementedError


def carregar(conn, caminho: str) -> int:
    """Lê o arquivo de entrada e povoa as relações. Retorna o total de produtos."""
    raise NotImplementedError


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
