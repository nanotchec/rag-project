# ingestion/docx_chargeur.py
from pathlib import Path
from typing import List, Dict
from docx import Document as DocxDocument
import re

# Regex simple pour détecter les titres : tout en majuscules ou commençant par Chapitre/Section
_RE_TITRE = re.compile(r"^(\d+(?:\.\d+)*\.?\s+.+|[A-Z][A-Z0-9\s\.\-:]+$)")
def _est_titre(texte: str) -> bool:
    """
    Retourne True si le texte correspond à un titre (majuscules ou motif Chapitre/Section).
    """
    return bool(_RE_TITRE.match(texte.strip()))

def charger_blocs_docx(chemin_fichier: str) -> List[Dict]:
    """
    Lit un .docx et renvoie une liste de blocs hiérarchiques :
    - Chaque bloc est un dict avec keys 'type', 'texte' et 'is_titre'.
    - Le premier bloc (type='intro') contient les 2-3 premiers paragraphes.
    - Chaque titre détecté est regroupé avec le paragraphe suivant.
    """
    chemin = Path(chemin_fichier)
    docx_obj = DocxDocument(chemin)
    paragraphes = [p.text.strip() for p in docx_obj.paragraphs if p.text.strip()]

    blocs: List[Dict] = []
    i = 0
    # Bloc d'introduction avec 2-3 premiers paragraphes
    intro_parags = []
    while i < len(paragraphes) and len(intro_parags) < 3:
        intro_parags.append(paragraphes[i])
        i += 1
    if intro_parags:
        blocs.append({
            "type": "intro",
            "texte": "\n".join(intro_parags),
            "is_titre": False
        })

    # Autres blocs hiérarchiques
    while i < len(paragraphes):
        p = paragraphes[i]
        if _est_titre(p):
            titre = p
            parag_suivant = paragraphes[i + 1] if i + 1 < len(paragraphes) else ""
            blocs.append({
                "type": "bloc",
                "texte": titre + "\n" + parag_suivant,
                "is_titre": True
            })
            i += 2
        else:
            blocs.append({
                "type": "bloc",
                "texte": p,
                "is_titre": False
            })
            i += 1
    return blocs
