from sentence_transformers import CrossEncoder
from typing import List

class CrossEncoderReranker:
    """Utilise un cross-encoder pour réordonner des passages par rapport à une requête."""

    def __init__(self, modele: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.modele = CrossEncoder(modele)

    def rerank(self, requete: str, passages: List[str]) -> List[float]:
        """Renvoie les scores du cross-encoder pour chaque passage."""
        paires = [[requete, passage] for passage in passages]
        scores = self.modele.predict(paires)
        return scores.tolist()
