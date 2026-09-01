"""Parsing do arquivo do SNAP e validações auxiliares.

Implemente aqui a leitura do amazon-meta.txt. A função abaixo é um ponto de
partida: cada produto no arquivo é um bloco separado por linha em branco.
"""
import re

RE_CATEGORY_TOKEN = re.compile(r"\|?([^|\[\]]+)\[(\d+)\]")

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
    produto = {
         "id": None,
        "asin": None,
        "title": None,
        "group": None,
        "salesrank": None,
        "status": "active",
        "similar": [],
        "categories": [],
        "reviews": [],
    }
    produto["status"] = "active" #padrão, só muda se achar a linha de discontinued

    linhas = bloco.splitlines()
    i=0
    while i < len(linhas):
        linha = linhas[i]
        if linha.startswith("Id:"):
            produto["Id"] = int(linha.split(":",1)[1].strip())
        elif linha.startswith("ASIN:"):
            produto["ASIN"] = linha.split(":", 1)[1].strip()
        elif linha.startswith("  title:"):
            produto["title"] = linha.split(":", 1)[1].strip()
        elif linha.startswith("  group:"):
            produto["group"] = linha.split(":", 1)[1].strip()
        elif linha.startswith("  salesrank:"):
            val = int(linha.split(":", 1)[1].strip())
            produto["salesrank"] = 0 if val == -1 else val
        elif linha.startswith("  similar:"):
            partes = linha.split()
            produto["similar"] = int(partes[1])
            produto["similares"] = partes[2:]
        elif linha.startswith("  categories:"):
            n_categorias = int(linha.split(":", 1)[1].strip())
            categorias = []
            for j in range(1, n_categorias + 1):
                caminho = linhas[i + j].strip()
                tokens = RE_CATEGORY_TOKEN.findall(caminho)
                categorias.append([(nome.strip(), int(cid)) for nome, cid in tokens])
            produto["categorias_detalhe"] = categorias
            i +=n_categorias
        elif linha.startswith("  reviews:"):
            partes = linha.split()
            produto["total_reviews"] = int(partes[2])
            produto["downloaded_reviews"] = int(partes[4])
            produto["avg_rating"] = float(partes[7])

            padrao_review = re.compile(r'\s*([\d-]+)\s+cutomer:\s*(\S+)\s+rating:\s*(\d+)\s+votes:\s*(\d+)\s+helpful:\s*(\d+)')

            reviews = []
            j = 1
            while (i + j) < len(linhas):
                linha_review = linhas[i + j]
                m = padrao_review.match(linha_review)
                if not m:
                    break  # não é mais uma linha de review, para de consumir
                data, cliente, rating, votos, util = m.groups()
                reviews.append({
                    "date": data,
                    "customer": cliente,
                    "rating": int(rating),
                    "votes": int(votos),
                    "helpful": int(util)
                })
                j += 1

            produto["reviews"] = reviews
            i += (j - 1)  # pula só as linhas que realmente foram consumidas



        elif "discontinued product" in linha:
            produto["status"] = "discontinued"

        i += 1

    return produto