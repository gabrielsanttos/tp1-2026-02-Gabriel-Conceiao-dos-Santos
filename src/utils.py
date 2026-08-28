"""Parsing do arquivo do SNAP e validações auxiliares.

Implemente aqui a leitura do amazon-meta.txt. A função abaixo é um ponto de
partida: cada produto no arquivo é um bloco separado por linha em branco.
"""


def iter_produtos(caminho):
    """Gera um bloco de texto por produto do arquivo de entrada."""
    bloco = []
    with open(caminho, encoding="utf-8", errors="replace") as f:
        for linha in f:
            if linha.strip():
                bloco.append(linha)
            elif bloco:
                yield "".join(bloco)
                bloco = []
    if bloco:
        yield "".join(bloco)


def parse_produto(bloco: str) -> dict:
    """Converte um bloco de texto nos campos do produto. TODO: implementar."""
    raise NotImplementedError
