"""Qué dice cada declaración de impacto ambiental sobre la Red Natura 2000, con la frase del BOE que lo prueba.

No hay cruce geográfico: se lee lo que la propia resolución declara. Se clasifica en cuatro niveles, de forma
conservadora (una frase que niega algo nunca cuenta como afección, y una mención genérica, como el título de un
apartado, no cuenta para nada):

- «dentro»: la resolución dice que el proyecto o alguno de sus elementos está dentro, atraviesa, ocupa o afecta
  directamente a un espacio de la Red Natura 2000.
- «entorno»: dice que colinda, está a 5 km o menos o puede afectar indirectamente a un espacio.
- «fuera»: declara expresamente que no coincide con ningún espacio, o que el más próximo está a más de 5 km.
- «sin_mencion»: no dice nada que permita situarlo.

El resultado se guarda en data/natura_dia.json y solo se leen del BOE las resoluciones nuevas.
"""
from __future__ import annotations

import json
import re

import requests

from . import config

NIVELES = ("dentro", "entorno", "fuera", "sin_mencion")
ETIQUETA = {
    "dentro": "Dentro o atraviesa Red Natura",
    "entorno": "En el entorno de Red Natura",
    "fuera": "Declara que no coincide",
    "sin_mencion": "Sin mención a Red Natura",
}
VERSION = 2  # subir al cambiar las reglas, para que se reclasifique todo

_ESPACIO = (
    r"(?:Red Natura(?: 2000)?|Natura 2000|RN ?2000|ZEPA|ZEPIM|\bZEC\b|\bLIC\b|zona de especial protecci[oó]n para las aves"
    r"|zona especial de conservaci[oó]n|lugar(?:es)? de importancia comunitaria)"
)
_RE_ESPACIO = re.compile(_ESPACIO, re.I)
_NEGACION = re.compile(
    r"\b(?:no|ning[uú]n[oa]?|ni)\b|fuera de|sin (?:afectar|ocupar|atravesar|cruzar|invadir)|evit(?:ar|ando|a)\b"
    r"|exterior(?:es)? (?:a|al|de)", re.I)
# Frases sobre alternativas descartadas o espacios aún no declarados: no sitúan el proyecto elegido.
_AJENA = re.compile(r"alternativa|descart|propuest[oa]s? (?:como|de)|futur[oa]s? (?:ZEPA|ZEC)", re.I)
_RELATIVA = re.compile(
    _ESPACIO + r"[^.;]{0,60}\b(?:sobre|en|dentro de) (?:el|la|los|las) que se (?:emplaza|ubica|sit[uú]a|localiza|"
    r"desarrolla|asienta|proyecta)n?\b", re.I)
_FINALIDAD = re.compile(r"\b(?:para que|a fin de que|con el fin de que|de modo que|de forma que|siempre que)\b", re.I)
_CONTRASTE = re.compile(r",?\s(?:si bien|aunque|no obstante|sin embargo|pero)\b,?", re.I)
_DENTRO = [
    re.compile(p, re.I)
    for p in (
        r"dentro (?:de|del)[^.;]{0,60}" + _ESPACIO,
        r"en el interior (?:de|del)[^.;]{0,60}" + _ESPACIO,
        r"(?:atraviesa|atravesar[aá]|atravesando|cruza|cruzar[aá]|cruzando|transcurre|discurre|discurrir[aá])"
        r"[^.;]{0,80}" + _ESPACIO,
        r"(?:ubicad|situad|localizad|incluid|emplazad|integrad)[oa]s?,? (?:parcial|[ií]ntegra|total)?(?:mente)?,? "
        r"(?:en|dentro de)[^.;]{0,20}" + _ESPACIO,
        r"se (?:ubica|ubican|sit[uú]a|sit[uú]an|localiza|localizan|emplaza|emplazan|encuentra|encuentran|incluye|incluyen)"
        r" (?:parcial|[ií]ntegra|total)?(?:mente)? ?(?:en|dentro de)[^.;]{0,20}" + _ESPACIO,
        r"(?:ocupa|ocupar[aá]|ocupan|ocupar[aá]n|ocupaci[oó]n de)[^.;]{0,80}" + _ESPACIO,
        r"(?:solapa|solapan|solape|coincide|coinciden)[^.;]{0,40}" + _ESPACIO,
        r"afecta(?:r[aá]|n|r[aá]n)? (?:directamente )?(?:a )?(?:la|el|los|las)?[^.;]{0,15}" + _ESPACIO,
        r"afecci[oó]n directa[^.;]{0,60}" + _ESPACIO,
    )
]
_ENTORNO = [
    re.compile(p, re.I)
    for p in (
        r"(?:limita|limitan|linda|lindan|colinda|colindan|colindante|lindante|lim[ií]trofe)[^.;]{0,60}" + _ESPACIO,
        r"(?:pr[oó]xim|cercan|inmediaciones|entorno (?:de|del))[^.;]{0,60}" + _ESPACIO,
        r"\ba (?:unos |aproximadamente |una distancia de |menos de |m[aá]s de )?[\d.,]+ ?(?:km|kil[oó]metros|m|metros)"
        r"[^.;]{0,50}" + _ESPACIO,
        r"(?:puede|podr[ií]a|pueden|podr[ií]an) afectar[^.;]{0,80}" + _ESPACIO,
        r"afecci[oó]n indirecta[^.;]{0,80}" + _ESPACIO,
        _ESPACIO + r"[^.;]{0,80}(?:[aá]reas? de campeo|a (?:unos |aproximadamente )?[\d.,]+ ?(?:km|kil[oó]metros|metros))",
        r"perjuicio a la integridad[^.;]{0,80}" + _ESPACIO,
    )
]
_FUERA = [
    re.compile(p, re.I)
    for p in (
        r"\bno\b[^.;]{0,40}(?:afect|coincid|ubic|encuentr|sit[uú]|intercept|incluid|dentro|"
        r"ocup|solap|atravies|cruz)[^.;]{0,120}" + _ESPACIO,
        r"ning[uú]n(?:a)? (?:espacio|zona|lugar)[^.;]{0,60}" + _ESPACIO,
        r"(?:encuentra|ubica|sit[uú]a|queda|ubicad|situad|localizad|emplazad|proyect)[a-z]*[^.;]{0,30}"
        r"fuera (?:de|del)[^.;]{0,60}" + _ESPACIO,
    )
]


UMBRAL_KM = 5  # a más distancia que esta, «el espacio más próximo está a X km» sitúa el proyecto fuera
_DIST = re.compile(r"(\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?)\s?(km|kil[oó]metros|m|metros)\b", re.I)


def _km(f: str) -> float | None:
    """La menor distancia expresada en la frase, en km."""
    out = []
    for n, u in _DIST.findall(f):
        v = float(n.replace(".", "").replace(",", "."))
        out.append(v if u.lower().startswith("k") else v / 1000)
    return min(out) if out else None


def frases(texto: str) -> list[str]:
    out = []
    texto = re.sub(r"[   ]", " ", texto)
    for parrafo in texto.split("\n"):
        for f in re.split(r"(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÑ¿(])", parrafo):
            f = f.strip()
            if f and _RE_ESPACIO.search(f):
                out.append(f)
    return out


def _cita(f: str, n: int = 320) -> str:
    f = re.sub(r"\s+", " ", f).strip()
    if len(f) <= n:
        return f
    m = _RE_ESPACIO.search(f)
    ini = max(0, (m.start() if m else 0) - n // 2)
    trozo = f[ini:ini + n]
    return ("…" if ini else "") + trozo.strip() + "…"


def clasificar(texto: str) -> dict:
    """{nivel, cita} con la primera frase que prueba el nivel más alto."""
    mejor: dict[str, str] = {}
    for f in frases(texto):
        if len(f) < 40:
            continue  # títulos de apartado («Espacios naturales protegidos y Red Natura 2000.»)
        negada = bool(_NEGACION.search(f))
        ajena = bool(_AJENA.search(f))
        if _RELATIVA.search(f):
            # «los lugares de la Red Natura 2000 sobre los que se emplaza la actuación»: sitúa aunque la frase niegue
            # otra cosa
            mejor.setdefault("dentro", f)
            continue
        if negada and _FINALIDAD.search(f):
            continue  # «para que el proyecto no afecte a la ZEC…» es una medida, no una declaración de ubicación
        if negada:
            # «no afecta directamente a ningún espacio, si bien se encuentra próximo a varios»: cuenta lo que sigue
            partes = _CONTRASTE.split(f, maxsplit=1)
            if len(partes) == 2 and not _NEGACION.search(partes[1]) and any(p.search(partes[1]) for p in _ENTORNO):
                d = _km(partes[1])
                mejor.setdefault("fuera" if d is not None and d > UMBRAL_KM else "entorno", f)
                continue
        if not negada and not ajena and any(p.search(f) for p in _DENTRO):
            mejor.setdefault("dentro", f)
        elif not negada and (any(p.search(f) for p in _ENTORNO) or (ajena and any(p.search(f) for p in _DENTRO))):
            d = _km(f)
            mejor.setdefault("fuera" if d is not None and d > UMBRAL_KM else "entorno", f)
        elif negada and any(p.search(f) for p in _FUERA):
            mejor.setdefault("fuera", f)
    for nivel in NIVELES[:3]:
        if nivel in mejor:
            return {"nivel": nivel, "cita": _cita(mejor[nivel])}
    return {"nivel": "sin_mencion", "cita": ""}


def texto_boe(identificador: str, sesion: requests.Session) -> str:
    """Texto de la resolución: primero la caché del observatorio (si está en este equipo), si no el XML del BOE."""
    local = config.OBSERVATORIO / "data" / "cache" / "boe" / f"{identificador}.txt"
    if local.exists():
        return local.read_text(encoding="utf-8")
    from lxml import etree

    r = sesion.get(f"https://www.boe.es/diario_boe/xml.php?id={identificador}", timeout=90,
                   headers={"Accept": "application/xml"})
    r.raise_for_status()
    el = etree.fromstring(r.content).find("texto")
    if el is None:
        return ""
    return re.sub(r"[ \t]+", " ", "\n".join(t.strip() for t in el.itertext() if t.strip()))


def actualizar(fichas: list[dict], aviso=print) -> dict[str, dict]:
    ruta = config.DATA / "natura_dia.json"
    previo = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    if previo.get("version") != VERSION:
        previo = {}
    res: dict[str, dict] = previo.get("dia", {})
    sesion = requests.Session()
    sesion.headers["User-Agent"] = config.UA
    nuevas = 0
    for f in fichas:
        i = f["identificador"]
        if i in res:
            continue
        try:
            res[i] = clasificar(texto_boe(i, sesion))
            nuevas += 1
        except requests.RequestException as e:
            aviso(f"  natura: {i} no se pudo leer ({e})")
    ruta.write_text(json.dumps({"version": VERSION, "dia": dict(sorted(res.items()))}, ensure_ascii=False, indent=0),
                    encoding="utf-8")
    aviso(f"  natura: {nuevas} resoluciones nuevas clasificadas, {len(res)} en total")
    return res
