"""Conexão com o PostgreSQL e argumentos de linha de comando comuns aos scripts."""

import argparse

import psycopg


def add_db_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db-host", required=True)
    parser.add_argument("--db-port", default="5432")
    parser.add_argument("--db-name", required=True)
    parser.add_argument("--db-user", required=True)
    parser.add_argument("--db-pass", required=True)


def connect(args: argparse.Namespace) -> psycopg.Connection:
    return psycopg.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_pass,
    )
