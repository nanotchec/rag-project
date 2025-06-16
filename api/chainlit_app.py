# api/chainlit_app.py
"""
Interface Chainlit pour interagir avec le RAG EasyStrat.

Fonctionnalités :
- Chatbot : l'utilisateur écrit une question => le RAG répond.
- Upload de documents DOCX, PDF, TXT… => ingestion + indexation directe.
- Affichage des sources (titre tronqué + score CE).

Pré-requis :
    pip install chainlit python-docx pymupdf
    (et les dépendances déjà utilisées dans le projet)

Lancement :
    chainlit run api/chainlit_app.py --port 8001

Naviguer ensuite sur http://localhost:8001
"""
import sys
import os
sys.path.insert(0, os.getcwd())

from pathlib import Path
from typing import List
import textwrap

import chainlit as cl

from ingestion.decoupeur_texte import decouper_blocs_en_chunks
from magasin_vecteurs.chroma_magasin import MagasinVecteursChroma
from services.qa_service import answer as rag_answer

# ---- Configuration globale -------------------------------------------------

CHROMA_PATH = "magasin_chroma"

# Collection Chroma partagée
VECTOR_STORE = MagasinVecteursChroma(chemin_index=CHROMA_PATH)

# Taille max pour un extrait affiché dans le chat
MAX_EXCERPT_LEN = 100


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _truncate(text: str, max_len: int = MAX_EXCERPT_LEN) -> str:
    """Tronque le texte pour l'affichage."""
    return textwrap.shorten(text.replace("\n", " "), width=max_len, placeholder="…")


async def _ingest_file(fp: Path) -> int:
    """Ingestion synchrone d'un fichier, retourne le nb de chunks ajoutés."""
    chunks = decouper_blocs_en_chunks(str(fp))
    VECTOR_STORE.ajouter_documents(chunks)
    return len(chunks)


# ---------------------------------------------------------------------------
# Événements Chainlit
# ---------------------------------------------------------------------------

@cl.on_chat_start
async def start_chat():
    await cl.Message(
        content=(
            "👋 Bienvenue ! Je suis l'assistant RAG EasyStrat.\n\n"
            "• Pose-moi une question en langage naturel.\n"
            "• Ou glisse-dépose un document (DOCX/PDF/TXT) pour l'ingérer.\n"
            "\nToutes les réponses seront en français et sourcées."
        )
    ).send()


@cl.on_message
async def handle_message(msg: cl.Message):
    # Gestion des pièces jointes (upload)
    if msg.elements:
        total_chunks = 0
        for elem in msg.elements:
            fp = Path(elem.path)
            # Only ingest .docx, .pdf, .txt files
            if fp.suffix.lower() in (".docx", ".pdf", ".txt"):
                nb = await _ingest_file(fp)
                total_chunks += nb
        if total_chunks > 0:
            await cl.Message(
                content=(
                    f"✅ Fichier(s) ingéré(s) avec succès : {total_chunks} chunks ajoutés.\n"
                    "Pose maintenant ta question !"
                )
            ).send()
            return

    # Si c'est une vraie question → pipeline RAG
    question = msg.content.strip()
    if not question:
        await cl.Message(content="❌ Je n'ai rien reçu à analyser.").send()
        return

    # Appel du RAG
    result = rag_answer(question)

    # Construction de la réponse pour l'utilisateur
    answer_txt = result["answer"]
    sources = result["sources"]

    # Message principal (réponse)
    await cl.Message(answer_txt).send()

    # Message secondaire (sources)
    if sources:
        lines: List[str] = []
        for i, src in enumerate(sources, 1):
            excerpt = _truncate(src["texte"])
            score = src["score_ce"]
            lines.append(f"**[{i}]** {excerpt} — *score {score:.3f}*")
        await cl.Message("\n".join(lines)).send()