# models/document.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class Document:
    texte: str
    metadonnees: Dict[str, str]
