from chromadb import PersistentClient
from embeddings.modele_embedding import embed
from models.document import Document
from typing import List, Dict
from rerankers.cross_encoder_reranker import CrossEncoderReranker
import numpy as np

class MagasinVecteursChroma:
    """Classe pour gérer le stockage et la recherche vectorielle via ChromaDB."""

    def __init__(self, chemin_index: str = "magasin_chroma", modele_rerank: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # Persistent local client (no deprecated settings)
        self.client = PersistentClient(path=chemin_index)
        # Création ou récupération de la collection
        self.collection = self.client.get_or_create_collection(
            name="chunks",
            metadata={"description": "Index des chunks de documents"}
        )
        self.reranker = CrossEncoderReranker(modele_rerank)

    def ajouter_documents(self, docs: List[Document]) -> None:
        """Indexe une liste de Document (chunks) dans Chroma."""
        texts     = [doc.texte for doc in docs]
        metadatas = [doc.metadonnees for doc in docs]
        ids       = [
            f"{meta['nom_fichier']}_{meta['index_chunk']}"
            for meta in metadatas
        ]
        embeddings = embed(texts)  # np.ndarray
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

    def interroger(self, requete: str, top_k: int = 10, k_rerank: int = 5) -> Dict:
        """Recherche les chunks les plus proches de la requête puis applique un reranking."""
        requete_emb = embed([requete])[0]
        resultats = self.collection.query(
            query_embeddings=[requete_emb.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        documents = resultats["documents"][0]
        metadatas = resultats["metadatas"][0]
        ids       = resultats["ids"][0]
        distances = resultats["distances"][0]

        scores = self.reranker.rerank(requete, documents)
        ordre  = list(np.argsort(scores)[::-1])
        meilleurs = ordre[:k_rerank]

        return {
            "ids": [ids[i] for i in meilleurs],
            "documents": [documents[i] for i in meilleurs],
            "metadatas": [metadatas[i] for i in meilleurs],
            "distances": [distances[i] for i in meilleurs],
            "scores": [scores[i] for i in meilleurs],
        }
