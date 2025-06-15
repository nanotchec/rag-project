from chromadb import PersistentClient
from embeddings.modele_embedding import embed
from models.document import Document
from typing import List, Dict

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

    def interroger(self, requete: str, top_k: int = 5) -> Dict:
        """
        Recherche les chunks les plus proches de la requête.
        Retourne un dict contenant 'ids', 'distances', 'documents', 'metadatas'.
        """
        # Embedding de la requête
        requete_emb = embed([requete])[0]
        # Query vectorielle
        resultats = self.collection.query(
            query_embeddings=[requete_emb.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        # Le dict resultats a la forme :
        # { 'ids': [[...]], 'documents': [[...]], 'metadatas': [[...]], 'distances': [[...]] }
        # On renvoie le premier (seule requête)
        return {
            "ids"       : resultats["ids"][0],
            "documents" : resultats["documents"][0],
            "metadatas" : resultats["metadatas"][0],
            "distances" : resultats["distances"][0]
        }