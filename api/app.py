from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil

from services.qa_service import answer
from ingestion.decoupeur_texte import decouper_blocs_en_chunks
from magasin_vecteurs.chroma_magasin import MagasinVecteursChroma

app = FastAPI(
    title="RAG EasyStrat API",
    description="Endpoints pour questionner le RAG et ingérer des documents.",
    version="0.1.0",
)

# Client Chroma global
_CHROMA = MagasinVecteursChroma(chemin_index="magasin_chroma")

class QueryRequest(BaseModel):
    question: str
    nom_fichier: Optional[str] = None

# ---------- ENDPOINTS ----------

@app.post("/query")
async def query(req: QueryRequest):
    """
    Pose une question en langage naturel.
    Retourne la réponse générée et les sources.
    """
    try:
        result = answer(req.question, req.nom_fichier)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """
    Upload d'un ou plusieurs fichiers (.docx) pour ingestion puis indexation.
    """
    added_chunks = 0
    for uf in files:
        # Sauvegarde temporaire
        tmp_path = Path("uploads") / uf.filename
        tmp_path.parent.mkdir(exist_ok=True)
        with tmp_path.open("wb") as buffer:
            shutil.copyfileobj(uf.file, buffer)

        # Découpage hiérarchique
        chunks = decouper_blocs_en_chunks(str(tmp_path))
        _CHROMA.ajouter_documents(chunks)
        added_chunks += len(chunks)

        # Nettoyage
        tmp_path.unlink(missing_ok=True)

    return {"status": "ok", "chunks_added": added_chunks}
