"""Attention causale à une tête : même résultat avec/sans KV cache.

Exemple pédagogique déterministe, pas un modèle Mistral entraîné.
Le cache conserve K et V ; il ne conserve ni réponses ni embeddings RAG.
"""

import math


def attention(q, keys, values):
    logits = [sum(a * b for a, b in zip(q, k)) / math.sqrt(len(q)) for k in keys]
    weights = [math.exp(score - max(logits)) for score in logits]
    total = sum(weights)
    return [sum(w * v[d] for w, v in zip(weights, values)) / total for d in range(len(q))]


def project(token):
    # Petites projections fixes pour rendre le mécanisme visible.
    x, y = token
    return [x, y], [x + y, x - y], [x * 0.5, y * 2]


def run_demo():
    tokens = [[1, 0], [0, 1], [1, 1], [2, 1]]
    keys, values = [], []
    full_projections = cached_projections = 0
    for step, token in enumerate(tokens, 1):
        full = [project(t) for t in tokens[:step]]
        full_projections += step
        expected = attention(full[-1][0], [p[1] for p in full], [p[2] for p in full])
        q, k, v = project(token)
        keys.append(k)
        values.append(v)
        cached_projections += 1
        actual = attention(q, keys, values)
        assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(expected, actual))
        print(f"Token {step} : sortie identique, cache = {len(keys)} paires K/V")
    print(f"Tokens projetés : sans cache={full_projections}, avec cache={cached_projections}")
    return full_projections, cached_projections


if __name__ == "__main__":
    run_demo()
