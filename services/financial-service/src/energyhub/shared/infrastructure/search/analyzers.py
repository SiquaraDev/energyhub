"""Analisadores de texto do Elasticsearch (Fase 11).

`portuguese_analyzer` é um analisador **customizado** para os campos `Text` (razão/nome fantasia):
tokenizer padrão + `lowercase` + remoção de _stopwords_ do português + _stemming_ leve. Ao ser
referenciado num campo, o `Document.init()` o registra nas **settings do índice** automaticamente.
"""

from __future__ import annotations

from elasticsearch_dsl import analyzer, token_filter

portuguese_analyzer = analyzer(
    "portuguese_analyzer",
    tokenizer="standard",
    filter=[
        "lowercase",
        token_filter("portuguese_stop", type="stop", stopwords="_portuguese_"),
        token_filter("portuguese_stemmer", type="stemmer", language="light_portuguese"),
    ],
)
