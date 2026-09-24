"""Rutas a los proyectos hermanos. En local son carpetas vecinas; en Actions, checkouts del mismo nombre."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
DOCS = RAIZ / "docs"
CACHE = DATA / "cache"

GRAFO = Path(os.environ.get("CARTERA_GRAFO", RAIZ.parent / "grafo-promotores"))
OBSERVATORIO = Path(os.environ.get("CARTERA_OBSERVATORIO", RAIZ.parent / "observatorio-alegaciones"))

GRAFO_JSON = GRAFO / "data" / "grafo.json"
BORME_DIR = GRAFO / "data" / "borme"
CONDICIONADO = OBSERVATORIO / "docs" / "datos" / "condicionado"

UA = "cartera-cotizadas/0.1 (+https://github.com/Asensio94/cartera-cotizadas)"
