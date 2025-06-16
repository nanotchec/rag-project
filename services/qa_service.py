# services/qa_service.py
"""
Orchestrateur Q/R : interroge ChromaDB, construit le prompt,
appelle le LLM local (LM Studio) et renvoie réponse + sources.
"""

from typing import Dict, List
import requests
import textwrap

from magasin_vecteurs.chroma_magasin import MagasinVecteursChroma

# Seuil minimal de similarité CE : si aucune source n’atteint ce score, on renvoie un fallback
SCORE_THRESHOLD = 0.4

# ---------- Paramètres ----------
LMSTUDIO_URL = "http://localhost:1234/v1/completions"
MODEL_NAME   = "Magistral-Small"

TOP_K_INITIAL = 10      # Chroma top_k
TOP_K_FINAL   = 5       # après rerank

# Client Chroma global
_MAGASIN = MagasinVecteursChroma()

# ---------- Helpers ----------
def _call_lmstudio(prompt: str, max_tokens: int = 512) -> str:
    """Envoie le prompt à LM Studio et renvoie la réponse brute."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    resp = requests.post(LMSTUDIO_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["text"].strip()


def _build_prompt(question: str, passages: List[str]) -> str:
    """Construit le prompt final (style RAG) avec citations [Source n]."""
    context_blocks = [
        f"[Source {i+1}] {p}"
        for i, p in enumerate(passages[:TOP_K_FINAL])
    ]
    context = "\n".join(context_blocks)
    system_msg = (
        "Tu es un assistant IA expert des systèmes d'information hérités. "
        "Tu DOIS répondre strictement en français, sans aucun mot en anglais. "
        "Si la question demande plusieurs éléments, fournis-les sous forme de liste numérotée. "
        "Cite toujours tes sources entre crochets, par exemple [Source 1]."
    )
    prompt = (
        f"{system_msg}\n\n"
        f"CONTEXTE :\n{context}\n\n"
        f"QUESTION : {question}\n"
        "RÉPONSE :"
    )
    return prompt


# ---------- API principale ----------
def answer(question: str, nom_fichier: str = None) -> Dict:
    """
    Exécute le pipeline complet et renvoie dict :
    { 'answer': str, 'sources': List[dict] }
    """
    # 1) Retrieval + rerank
    res = _MAGASIN.interroger(question, TOP_K_INITIAL, TOP_K_FINAL, nom_fichier)

    # 1.1) Vérifier le score de similarité CE
    max_score = max(res["score_ce"]) if res["score_ce"] else 0.0
    if max_score < SCORE_THRESHOLD:
        return {
            "answer": "Désolé, je n'ai pas trouvé d'informations pertinentes pour votre requête.",
            "sources": []
        }

    # 2) Construction du prompt
    prompt = _build_prompt(question, res["documents"])

    # 3) Appel LLM
    reponse = _call_lmstudio(prompt)

    # 4) Sortie
    return {
        "answer": reponse,
        "sources": [
            {
                "texte": doc,
                "meta": meta,
                "score_ce": score,
                "dist_vec": dist,
            }
            for doc, meta, score, dist in zip(
                res["documents"],
                res["metadonnees"],
                res["score_ce"],
                res["distance_vdb"],
            )
        ],
    }


if __name__ == "__main__":
    # Test rapide
    q = "Quelle est la problématique des systèmes hérités ?"
    out = answer(q)
    print("Réponse :\n", out["answer"])
    print("\nSources :")
    for i, src in enumerate(out["sources"], 1):
        print(f"[{i}] {src['texte'][:120]}…")

# tests/test_qa_service.py
from services.qa_service import answer

def test_answer_french_and_numbered_list():
    # Test que la réponse est en français et liste numérotée
    out = answer("Quels sont les obstacles majeurs liés à l'accès aux données des systèmes existants ?")
    answer_text = out["answer"]
    # Doit commencer par un chiffre suivi d'un point
    assert any(line.strip().startswith(("1.", "1 .")) for line in answer_text.splitlines()), "La réponse doit commencer par '1.' pour la liste."
    # Doit contenir au moins un mot français clé
    assert "difficultés" in answer_text or "obstacles" in answer_text