# test_embed.py
from embeddings.modele_embedding import embed

def main():
    textes = ["Bonjour le monde", "Test d'embedding"]
    vecteurs = embed(textes)
    print("Forme des embeddings :", vecteurs.shape)

if __name__ == "__main__":
    main()