from chromadb import PersistentClient
from embeddings.modele_embedding import embed
from models.document import Document
from typing import List, Dict
from rerank.cross_encoder import rerank

class MagasinVecteursChroma:
    """Classe pour gérer le stockage et la recherche vectorielle via ChromaDB."""

    def __init__(self, chemin_index: str = "magasin_chroma"):
        # Persistent local client (no deprecated settings)
        self.client = PersistentClient(path=chemin_index)
        # Création ou récupération de la collection
        self.collection = self.client.get_or_create_collection(
            name="chunks",
            metadata={"description": "Index des chunks de documents"}
        )

    def ajouter_documents(self, docs: List[Document]) -> None:
        """
        Indexe une liste de Document (chunks) dans Chroma.
        Chaque Document contient texte et métadonnées.
        """
        # Préparation des données
        texts      = [doc.texte for doc in docs]
        metadatas  = [doc.metadonnees for doc in docs]
        ids        = [
            f"{meta['nom_fichier']}_{meta['index_chunk']}"
            for meta in metadatas
        ]
        # Calcul des embeddings
        embeddings = embed(texts)  # renvoie np.ndarray
        # Ajout à la collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

    def interroger(self, requete: str, top_k: int = 10, top_final: int = 5) -> Dict:
        # 1) Recherche vectorielle initiale
        requete_emb = embed([requete])[0]
        results = self.collection.query(
            query_embeddings=[requete_emb.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        ids        = results["ids"][0]
        texts      = results["documents"][0]
        metas      = results["metadatas"][0]
        distances  = results["distances"][0]

        # 2) Reranking avec cross-encoder
        ce_scores = rerank(requete, texts)  # numpy array of scores
        order = ce_scores.argsort()[::-1][:top_final]

        # 3) Retour des top_final résultats triés
        return {
            "ids":            [ids[i] for i in order],
            "documents":      [texts[i] for i in order],
            "metadatas":      [metas[i] for i in order],
            "distance_vdb":   [distances[i] for i in order],
            "score_ce":       [float(ce_scores[i]) for i in order],
        }