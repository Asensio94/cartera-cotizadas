"""A qué cotizada pertenece cada sociedad, y con qué prueba.

Solo hay dos caminos, y los dos terminan en un documento:

- «anexo»: la denominación de la sociedad figura en el anexo de sociedades de las cuentas consolidadas de la
  cotizada.
- «cadena»: su socio único inscrito en el BORME (o el socio único de este, y así hacia arriba) figura en ese anexo.
  La prueba es cada inscripción del BORME más la fila del anexo.

Nunca se atribuye por parecido de nombre. Si una sociedad lleva a dos cotizadas que no son matriz y filial entre sí
(una SPV vendida después del cierre del ejercicio, una sociedad conjunta), queda «en conflicto» y se enseñan las
dos pruebas.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import propiedad as pr


@dataclass
class Atribucion:
    sociedad: str
    cotizada: str
    via: str  # "anexo" o "cadena"
    fila: dict  # fila del anexo que lo prueba (de la propia sociedad o de su antecesora)
    eslabones: list = field(default_factory=list)  # inscripciones del BORME hasta la antecesora del anexo
    otras: list = field(default_factory=list)  # [(cotizada, via)] en conflicto
    participada: bool = False  # el anexo da una participación inferior al 50 %

    @property
    def estado(self) -> str:
        return "conflicto" if self.otras else self.via


def _ancestros(cotizadas: list[dict]) -> dict[str, set[str]]:
    matriz = {c["id"]: c.get("matriz") for c in cotizadas}
    out: dict[str, set[str]] = {}
    for cid in matriz:
        vistos, m = set(), matriz.get(cid)
        while m and m not in vistos:
            vistos.add(m)
            m = matriz.get(m)
        out[cid] = vistos
    return out


def _mas_especificas(cids: set[str], anc: dict[str, set[str]]) -> set[str]:
    """Quita las matrices cuando también aparece su filial cotizada (Enel si ya está Endesa)."""
    return {c for c in cids if not any(c in anc.get(o, set()) for o in cids if o != c)}


class Atribuidor:
    def __init__(self, indice_anexos: dict[str, list[tuple[str, dict]]], cotizadas: list[dict]):
        self.idx = indice_anexos
        self.anc = _ancestros(cotizadas)
        self._memo: dict[str, Atribucion | None] = {}

    def _directa(self, clave: str) -> dict[str, dict]:
        filas = {}
        for cid, fila in self.idx.get(clave, []):
            filas.setdefault(cid, fila)
        keep = _mas_especificas(set(filas), self.anc)
        return {c: filas[c] for c in keep}

    def atribuir(self, sociedad: str) -> Atribucion | None:
        if sociedad in self._memo:
            return self._memo[sociedad]
        candidatas: list[tuple[str, str, dict, list]] = []  # (cotizada, via, fila, eslabones)
        for cid, fila in self._directa(sociedad).items():
            candidatas.append((cid, "anexo", fila, []))
        subida: list = []
        for e in pr.cadena(sociedad):
            subida.append(e)
            if not e.madre:
                break
            hits = self._directa(e.madre)
            if hits:
                for cid, fila in hits.items():
                    candidatas.append((cid, "cadena", fila, list(subida)))
                break
        if not candidatas:
            self._memo[sociedad] = None
            return None
        # la prueba directa manda sobre la cadena; entre cotizadas emparentadas, la más específica
        cids = _mas_especificas({c[0] for c in candidatas}, self.anc)
        candidatas = [c for c in candidatas if c[0] in cids]
        candidatas.sort(key=lambda c: (c[1] != "anexo", c[0]))
        cid, via, fila, esl = candidatas[0]
        otras = sorted({(c[0], c[1]) for c in candidatas[1:] if c[0] != cid})
        pct = fila.get("pct")
        a = Atribucion(sociedad, cid, via, fila, esl, otras, participada=pct is not None and pct < 50)
        self._memo[sociedad] = a
        return a
