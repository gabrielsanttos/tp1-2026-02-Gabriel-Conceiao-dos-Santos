# TP1 — Bancos de Dados I (2026/02)

Repositório base para o Trabalho Prático I. A especificação completa está
[neste documento](https://docs.google.com/document/d/1ZfYetiJ1xYwUc8NU1HZ_7lR-3_IGBPdy-QqnMiCZCXo/edit).

O trabalho é **individual**. Crie seu repositório a partir deste template
(botão *Use this template*), mantenha-o **privado**, adicione o professor
(`altigran`) como colaborador e marque a versão final com a tag `v1.0`.

## Estrutura

```
tp1/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── src/
│   ├── tp1_3.2.py        # criação do esquema + carga (ETL)
│   ├── tp1_3.3.py        # consultas do Dashboard (SQL)
│   ├── db.py             # utilitários de conexão SQL (opcional, sem ORM)
│   └── utils.py          # parsing/validações (opcional)
├── sql/
│   └── schema.sql        # opcional: DDL em SQL puro, se preferir separar
├── data/
│   └── snap_amazon.txt   # arquivo de entrada (baixar, ver data/README.md)
├── docs/
│   ├── tp1_3.1.pdf       # documentação (diagrama + dicionário de dados)
│   └── esquema.png       # imagem do diagrama (se referenciada no PDF)
├── Makefile              # opcional (atalhos docker)
└── README.md
```

## Arquivo de entrada

Baixe o `amazon-meta.txt` do SNAP e salve como `data/snap_amazon.txt`:

```bash
curl -L https://snap.stanford.edu/data/bigdata/amazon/amazon-meta.txt.gz \
  | gunzip > data/snap_amazon.txt
```

O arquivo **não** deve ser versionado (já está no `.gitignore`).

## Como executar

```bash
# 1) Construir e subir os serviços
docker compose up -d --build

# 2) (Opcional) conferir saúde do PostgreSQL
docker compose ps

# 3) Criar esquema e carregar dados
docker compose run --rm app python src/tp1_3.2.py \
  --db-host db --db-port 5432 --db-name ecommerce --db-user postgres --db-pass postgres \
  --input /data/snap_amazon.txt

# 4) Executar o Dashboard (todas as consultas)
docker compose run --rm app python src/tp1_3.3.py \
  --db-host db --db-port 5432 --db-name ecommerce --db-user postgres --db-pass postgres \
  --product-asin <ASIN> \
  --output /app/out
```

Para recomeçar do zero: `docker compose down -v`.

## Saídas esperadas

`tp1_3.3.py` imprime as consultas no terminal e grava em `/app/out`:

- `q1_reviews.csv`
- `q2_similares.csv`
- `q3_evolucao_avaliacoes.csv`
- `q4_top_vendas_grupo.csv`
- `q5_produtos_media_uteis_positivas.csv`
- `q6_categorias_media_uteis_positivas.csv`
- `q7_clientes_comentarios_grupo.csv`

## Regras

- Todas as consultas em **SQL puro**, sem ORM.
- Ambos os scripts devem sair com código `0` em sucesso e `!= 0` em erro.
- Nada pode depender do ambiente local além de Docker e Docker Compose.
