from ingestion.decoupeur_texte import decouper_blocs_en_chunks

chemin = "exemples/mon_doc.docx"  # ton doc d'exemple
chunks = decouper_blocs_en_chunks(chemin)
print(f"{len(chunks)} chunks générés")
# Affiche les premiers chunks pour inspection
for c in chunks[:5]:
    print("——")
    print("section:", c.metadonnees["section"],
          "titre:", c.metadonnees["is_titre"])
    print(c.texte[:120], "…")