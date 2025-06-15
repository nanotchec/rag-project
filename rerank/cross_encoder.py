# rerank/cross_encoder.py
from typing import List
import numpy as np
from embeddings.modele_embedding import embed

def rerank(query: str, passages: List[str]) -> np.ndarray:
    """
    Reranking simple par similarité vectorielle : on encode la requête et les passages
    avec le même modèle d'embeddings, puis on calcule le produit scalaire.
    :param query: la question de l'utilisateur
    :param passages: liste de textes (chunks) à réordonner
    :return: array numpy de shape (len(passages),) avec les scores (plus élevé = plus pertinent)
    """
    # 1) Embeddings de la requête et des passages
    query_emb = embed([query])[0]               # vecteur unique
    passage_embs = embed(passages)              # matrice (n_passages, dim)

    # 2) Calcul des similarités (produit scalaire)
    scores = np.dot(passage_embs, query_emb)

    # 3) Normalisation optionnelle (commenter si inutile)
    # scores = scores / np.linalg.norm(query_emb)

    return scores