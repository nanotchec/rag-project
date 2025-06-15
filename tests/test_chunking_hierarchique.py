import os
import sys
import pytest

# Ajouter la racine du projet au path pour les imports locaux
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.decoupeur_texte import decouper_blocs_en_chunks

def test_decoupage_blocs_en_chunks_structure():
    """
    Vérifie que decouper_blocs_en_chunks renvoie des chunks non vides
    et que chaque metadata contient 'section' et 'is_titre'.
    """
    chemin = os.path.join('exemples', 'mon_doc.docx')
    chunks = decouper_blocs_en_chunks(chemin)
    # Au moins un chunk généré
    assert len(chunks) > 0, "Aucun chunk n'a été généré."
    # Vérifier les clés dans les métadonnées du premier chunk
    first_meta = chunks[0].metadonnees
    assert 'section' in first_meta, "La metadata 'section' doit être présente."
    assert 'is_titre' in first_meta, "La metadata 'is_titre' doit être présente."
    # 'section' doit valoir 'intro' ou 'bloc'
    assert first_meta['section'] in ('intro', 'bloc'), "La valeur de 'section' doit être 'intro' ou 'bloc'."
    # 'is_titre' doit être un booléen
    assert isinstance(first_meta['is_titre'], bool), "'is_titre' doit être un booléen."