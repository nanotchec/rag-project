# embeddings/modele_embedding.py
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# On charge le modèle all-MiniLM-L6-v2 pour les embeddings (rapide et léger)
modele = SentenceTransformer("all-MiniLM-L6-v2")

def embed(textes: List[str], batch_size: int = 8) -> np.ndarray:
    """
    Génère des embeddings pour une liste de textes avec all-MiniLM-L6-v2.
    :param textes: liste de chaînes à encoder
    :param batch_size: taille de batch pour l’inférence
    :return: array NumPy de shape (len(textes), dim_embedding)
    """
    # La méthode encode renvoie déjà un numpy array si on le demande
    return modele.encode(
        textes,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )