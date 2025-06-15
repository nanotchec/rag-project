# tests/test_ingestion.py
from ingestion.docx_chargeur import charger_document_docx
from ingestion.decoupeur_texte import decouper_en_chunks

def test_docx_et_decoupe():
    doc = charger_document_docx("exemples/mon_doc.docx")
    chunks = decouper_en_chunks(doc)
    assert len(chunks) > 0
    print(f"{len(chunks)} chunks générés depuis {doc.metadonnees['nom_fichier']}")
