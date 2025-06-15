# ingestion/decoupeur_texte.py
from typing import List
from models.document import Document
from ingestion.docx_chargeur import charger_blocs_docx

TAILLE_CHUNK = 300  # nombre approximatif de mots par chunk
CHEVAUCHEMENT = 50  # nombre de mots en chevauchement

def _split_long_texte(texte: str, taille_chunk: int, chevauchement: int) -> List[str]:
    """
    Découpe un texte long en sous-chaînes de taille 'taille_chunk' mots
    avec 'chevauchement' mots en commun entre chaque segment.
    """
    mots = texte.split()
    pas = taille_chunk - chevauchement
    segments = []
    for i in range(0, len(mots), pas):
        segment = mots[i : i + taille_chunk]
        segments.append(" ".join(segment))
        if i + taille_chunk >= len(mots):
            break
    return segments

def decouper_blocs_en_chunks(chemin_docx: str) -> List[Document]:
    """
    Renvoie la liste de Document (chunks) pour un fichier .docx,
    en respectant les blocs hiérarchiques fournis par charger_blocs_docx.
    """
    blocs = charger_blocs_docx(chemin_docx)
    chunks: List[Document] = []

    for idx_bloc, bloc in enumerate(blocs):
        texte = bloc["texte"]
        # Si le bloc est court, on le garde tel quel ; sinon on le découpe
        segments = (
            [texte]
            if len(texte.split()) <= TAILLE_CHUNK
            else _split_long_texte(texte, TAILLE_CHUNK, CHEVAUCHEMENT)
        )
        for idx_seg, seg in enumerate(segments):
            metadonnees = {
                **bloc,                      # type, is_titre, texte (optionnel)
                "index_chunk": len(chunks),
                "index_bloc": idx_bloc,
                "segment": idx_seg,
            }
            chunks.append(Document(texte=seg, metadonnees=metadonnees))
    return chunks
