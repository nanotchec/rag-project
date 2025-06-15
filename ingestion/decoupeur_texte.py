# ingestion/decoupeur_texte.py
from typing import List
from models.document import Document

TAILLE_CHUNK_PAR_DEFAUT = 300   # nombre approx. de tokens (ou mots ici)
CHEVAUCHEMENT_PAR_DEFAUT = 50

def decouper_en_chunks(
    doc: Document,
    taille_chunk: int = TAILLE_CHUNK_PAR_DEFAUT,
    chevauchement: int = CHEVAUCHEMENT_PAR_DEFAUT,
) -> List[Document]:
    """Découpe le texte d’un Document en chunks qui se chevauchent."""
    mots = doc.texte.split()
    pas = taille_chunk - chevauchement
    sous_docs: List[Document] = []

    for i in range(0, len(mots), pas):
        segment = mots[i : i + taille_chunk]
        if not segment:
            break
        texte_chunk = " ".join(segment)
        meta_chunk = {
            **doc.metadonnees,             # hérite des métadonnées d’origine
            "index_chunk": len(sous_docs), # numéro de chunk
            "debut_mot": i,
            "fin_mot": i + len(segment),
        }
        sous_docs.append(Document(texte=texte_chunk, metadonnees=meta_chunk))
    return sous_docs
