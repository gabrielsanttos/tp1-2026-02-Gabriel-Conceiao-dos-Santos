# Arquivo de entrada

Baixe o *Amazon product co-purchasing network metadata* (SNAP) e salve como
`snap_amazon.txt` nesta pasta:

```bash
curl -L https://snap.stanford.edu/data/bigdata/amazon/amazon-meta.txt.gz \
  | gunzip > data/snap_amazon.txt
```

O arquivo tem cerca de 1 GB descompactado e **não deve ser versionado**.
Dentro do contêiner ele fica disponível em `/data/snap_amazon.txt`.
