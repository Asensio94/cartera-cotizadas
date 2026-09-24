"""Cadena de propiedad vigente de cada sociedad, reconstruida del BORME que ya recoge el grafo de promotores.

Un eslabón es la última declaración de socio único inscrita (incluido el «cambio de identidad del socio único»,
que se inscribe como «Sociedad unipersonal» y es como se registra la venta de una SPV), mientras la sociedad no
pierda después la unipersonalidad. Cada eslabón conserva la inscripción del BORME que lo prueba.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from . import config

sys.path.insert(0, str(config.GRAFO))
from promotores import sociedades as so  # noqa: E402  (misma normalización de nombres que el grafo)

_UNIPERSONAL = {"Sociedad unipersonal", "Declaración de unipersonalidad", "Unipersonalidad"}


@dataclass
class Eslabon:
    hija: str
    madre: str | None  # id de sociedad; None si el socio único es una persona física o se perdió la unipersonalidad
    tipo: str  # "PJ", "PF" o "fin"
    fecha: str
    url: str
    nombre_madre: str = ""


@lru_cache(maxsize=1)
def grafo() -> dict:
    return json.loads(config.GRAFO_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def indice_nombres() -> dict[str, str]:
    """clave normalizada de cualquier denominación conocida → id de la sociedad en el grafo."""
    idx: dict[str, str] = {}
    for sid, s in grafo()["sociedades"].items():
        idx.setdefault(sid, sid)
        for n in s.get("nombres", []):
            k = so.clave(n)
            if k:
                idx.setdefault(k, sid)
    return idx


def resolver(nombre_o_clave: str, es_clave: bool = False) -> str:
    k = nombre_o_clave if es_clave else so.clave(nombre_o_clave)
    return indice_nombres().get(k, k)


def _inscripciones(borme_dir: Path):
    for p in sorted(borme_dir.glob("*.jsonl")):
        with p.open(encoding="utf-8") as fh:
            for linea in fh:
                if linea.strip():
                    yield json.loads(linea)


@lru_cache(maxsize=1)
def socios_vigentes() -> dict[str, Eslabon]:
    """sociedad → último eslabón de propiedad inscrito (en orden de fecha y número de inscripción)."""
    eventos = []
    for ins in _inscripciones(config.BORME_DIR):
        hija = resolver(ins["clave"], es_clave=True)
        url = f"https://www.boe.es/diario_borme/txt.php?id={ins['id']}"
        orden = (ins["fecha"], ins["num"])
        for a in ins["actos"]:
            if a["tipo"] == "Socio único" or (a["tipo"] in _UNIPERSONAL and a.get("sujetos")):
                sujetos = a.get("sujetos", [])
                if len(sujetos) != 1:
                    continue  # una declaración con varios sujetos no es un socio único legible
                s = sujetos[0]
                if s["tipo"] == "PJ":
                    madre = resolver(s["clave"], es_clave=True)
                    if madre == hija:
                        continue
                    eventos.append((orden, Eslabon(hija, madre, "PJ", ins["fecha"], url, s.get("nombre", ""))))
                else:
                    eventos.append((orden, Eslabon(hija, None, "PF", ins["fecha"], url)))
            elif a["tipo"].startswith("Pérdida del car"):
                eventos.append((orden, Eslabon(hija, None, "fin", ins["fecha"], url)))
    vig: dict[str, Eslabon] = {}
    for _, e in sorted(eventos, key=lambda x: x[0]):
        vig[e.hija] = e
    return vig


def cadena(sociedad: str, max_saltos: int = 12) -> list[Eslabon]:
    """Eslabones desde la sociedad hacia arriba, hasta una persona física, una sociedad sin socio único conocido
    o un ciclo (que se corta)."""
    vig = socios_vigentes()
    out: list[Eslabon] = []
    vistos = {sociedad}
    actual = sociedad
    for _ in range(max_saltos):
        e = vig.get(actual)
        if e is None:
            break
        out.append(e)
        if e.madre is None or e.madre in vistos:
            break
        vistos.add(e.madre)
        actual = e.madre
    return out


def cima(sociedad: str) -> str:
    """La sociedad más alta de la cadena (ella misma si no tiene socio único jurídico)."""
    arriba = sociedad
    for e in cadena(sociedad):
        if e.madre:
            arriba = e.madre
    return arriba
