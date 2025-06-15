# embeddings/modele_embedding.py
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# On charge le modèle E5-Mistral, sans code custom
modele = SentenceTransformer("intfloat/e5-mistral-7b-instruct")

def embed(textes: List[str], batch_size: int = 8) -> np.ndarray:
    """
    Génère des embeddings pour une liste de textes avec intfloat/e5-mistral-7b-instruct.
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