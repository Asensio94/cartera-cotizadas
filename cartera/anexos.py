"""Las sociedades que cada cotizada declara como suyas en el anexo de sus cuentas anuales consolidadas.

El anexo de sociedades dependientes, asociadas y negocios conjuntos es la prueba documental: lo formulan los
administradores, lo revisa el auditor y se deposita en la CNMV. Aquí se lee el PDF y se buscan, página a página,
las denominaciones sociales que aparecen en el BOE, el BORME y las DIA. La denominación social es única en el
Registro Mercantil, así que una coincidencia exacta de denominación (sin la forma jurídica) identifica la sociedad.

Solo se leen páginas con aspecto de tabla de sociedades (muchas formas jurídicas y cifras de participación), para
no confundir una dependiente con una sociedad que se menciona en una nota porque se vendió o se compró.

La tabla leída va a data/anexos/<id>.json y se versiona: el PDF solo se descarga cuando cambia el documento.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import requests

from . import config
from .propiedad import so

_FORMA = re.compile(
    r"\b(?:S\.?\s?L\.?\s?U\.?|S\.?\s?A\.?\s?U\.?|S\.?\s?L\.?|S\.?\s?A\.?|S\.?\s?R\.?\s?L\.?|SLU|SAU|SL|SA|"
    r"SOCIEDAD LIMITADA|SOCIEDAD AN[OÓ]NIMA|S\.?A\.?S\.?|GMBH|B\.?V\.?|LTD|LIMITED|SRL|S\.?P\.?A\.?|LDA|AG|SE|"
    r"A\.?I\.?E\.?|U\.?T\.?E\.?)(?=[\s,.;)]|$)",
    re.I,
)
_PCT = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{1,4})?)\s?%")


def cotizadas() -> list[dict]:
    return json.loads((config.DATA / "cotizadas.json").read_text(encoding="utf-8"))["cotizadas"]


def _descargar(url: str) -> Path:
    """El documento en la caché local. Vale un PDF o un XHTML de formato ESEF (el que deposita la CNMV)."""
    destino = config.CACHE / "pdf" / hashlib.sha1(url.encode()).hexdigest()[:16]
    if destino.exists() and destino.stat().st_size > 10_000:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    # varias webs de inversores rechazan un agente que no parezca un navegador
    r = requests.get(url, timeout=300, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0 Safari/537.36",
        "Accept": "application/pdf,application/xhtml+xml,*/*"})
    r.raise_for_status()
    if not (r.content.startswith(b"%PDF") or _es_xhtml(r.content[:400])):
        raise ValueError(f"{url} no devuelve un PDF ni un XHTML")
    destino.write_bytes(r.content)
    return destino


def _es_xhtml(cabecera: bytes) -> bool:
    return cabecera.lstrip().startswith((b"<?xml", b"<html"))


def _paginas_xhtml(ruta: Path):
    """Texto de cada página de un XHTML de Workiva (un div «pageView» por página impresa), una celda por línea."""
    import html

    xhtml = ruta.read_bytes().decode("utf-8", "replace")
    trozos = re.split(r'<div[^>]*class="pageView"[^>]*>', xhtml)[1:]
    for trozo in trozos:
        # Solo las celdas de tabla: el anexo es una tabla, y así una sociedad citada en la prosa de una nota (porque
        # se vendió, se compró o es un cliente) no entra nunca. Cada celda, una línea, aunque el nombre se parta.
        celdas = [html.unescape(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<td\b[^>]*>(.*?)</td>", trozo, re.S)]
        texto = "\n".join(" ".join(c.split()) for c in celdas if c.strip())
        # el folio impreso es lo que se busca al abrir el documento: «| 233» al pie o un número solo al principio
        todo = html.unescape(re.sub(r"<[^>]+>", "\n", trozo))
        lineas = [l.strip() for l in todo.splitlines() if l.strip()]
        m = next((re.fullmatch(r"\|\s*(\d{1,4})", l) for l in lineas if re.fullmatch(r"\|\s*(\d{1,4})", l)), None)
        if not m and lineas:
            m = re.fullmatch(r"(\d{1,4})", lineas[0])
        yield texto, int(m.group(1)) if m else None


def _paginas(ruta: Path):
    if _es_xhtml(ruta.read_bytes()[:400]):
        yield from _paginas_xhtml(ruta)
        return
    import fitz

    with fitz.open(ruta) as pdf:
        for pagina in pdf:
            yield pagina.get_text("text"), None


def _es_tabla(texto: str) -> bool:
    return len(_FORMA.findall(texto)) >= 8 and bool(re.search(r"\d{1,3}[.,]\d{2}|%", texto))


_FORMA_ES = re.compile(
    r"\b(?:S\.?\s?L\.?\s?U\.?|S\.?\s?A\.?\s?U\.?|S\.?\s?L\.?|S\.?\s?A\.?|SOCIEDAD LIMITADA|SOCIEDAD AN[OÓ]NIMA|"
    r"A\.?\s?I\.?\s?E\.?)(?:\s?UNIPERSONAL)?(?=[\s,.;)]|$)",
    re.I,
)


def _candidatas(linea: str) -> set[str]:
    """Claves posibles de una línea de tabla: el tramo hasta cada forma jurídica española.

    Solo las españolas: la denominación es única en el Registro Mercantil, no entre países («Enel Green Power
    SpA» no es «Enel Green Power, S.L.»)."""
    out = set()
    for m in _FORMA_ES.finditer(linea):
        previo = linea[: m.start()]
        out.add(so.clave(previo + " " + m.group(0)))
        # si la fila anterior deja importes delante («– 1,614 Explotaciones Eólicas…»), también sin ellos
        # (solo importes con decimales, % o guion: «Bonito 3 Energia Renovável» es un nombre entero)
        cola = re.split(r"(?:^|\s)(?:[–—-]\s?[\d.,]+%?|\d+[.,]\d+%?|\d+%)\s(?=[A-ZÁÉÍÓÚÑ])", previo)[-1]
        if cola != previo and len(cola.split()) >= 2:
            out.add(so.clave(cola + " " + m.group(0)))
    return {k for k in out if len(k) >= 5}


def leer(doc: dict) -> list[dict]:
    """Todas las líneas con forma jurídica de las páginas de tabla del documento, con sus claves posibles.

    Se guarda la tabla entera (no solo lo que hoy coincide con el BOE) para poder cruzarla otra vez cuando el grafo
    crezca sin volver a descargar el PDF."""
    filas: list[dict] = []
    for i, (texto, folio) in enumerate(_paginas(_descargar(doc["url"])), start=1):
        if not _es_tabla(texto):
            continue
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        for j, l in enumerate(lineas):
            if not _FORMA.search(l) and not (j + 1 < len(lineas) and _FORMA.search(lineas[j + 1])):
                continue
            # una denominación larga puede partirse en dos líneas: se prueba también unida a la siguiente
            claves = _candidatas(l)
            if j + 1 < len(lineas):
                claves |= _candidatas(l + " " + lineas[j + 1])
            if not claves:
                continue
            contexto = " · ".join(lineas[j: j + 5])
            m = _PCT.search(contexto)
            filas.append({
                "texto": l[:160],
                "claves": sorted(claves),
                "pagina": i,
                **({"folio": folio} if folio else {}),
                "contexto": contexto[:240],
                "pct": float(m.group(1).replace(",", ".")) if m else None,
            })
    return filas


def actualizar(forzar: bool = False, aviso=print) -> dict[str, dict]:
    """Lee (o reutiliza) los anexos de cada cotizada. Devuelve id → {urls, filas}. El PDF solo se descarga cuando
    cambia la lista de documentos de data/cotizadas.json."""
    out: dict[str, dict] = {}
    carpeta = config.DATA / "anexos"
    carpeta.mkdir(parents=True, exist_ok=True)
    for c in cotizadas():
        ruta = carpeta / f"{c['id']}.json"
        previo = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
        urls = [d["url"] for d in c.get("documentos", [])]
        if not forzar and previo.get("urls") == urls:
            out[c["id"]] = previo
            continue
        filas: list[dict] = []
        leidas: list[str] = []
        for d in c.get("documentos", []):
            try:
                for f in leer(d):
                    f["documento"] = d["url"]
                    filas.append(f)
                leidas.append(d["url"])
            except (requests.RequestException, ValueError, RuntimeError) as e:
                aviso(f"  anexos: {c['id']}: no se pudo leer {d['url']} ({e})")
        if leidas != urls and previo:
            out[c["id"]] = previo  # mejor la tabla anterior que una incompleta
            continue
        res = {"id": c["id"], "urls": urls, "filas": filas}
        ruta.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        aviso(f"  anexos: {c['id']}: {len(filas)} filas de sociedades en {len(leidas)} documento(s)")
        out[c["id"]] = res
    return out


_GENERICAS = set(
    "ENERGIA ENERGIAS ELECTRICIDAD ELECTRICA ELECTRICAS SOLAR SOLARES EOLICA EOLICAS EOLICO EOLICOS RENOVABLE "
    "RENOVABLES GENERACION TRANSPORTE DISTRIBUCION DESARROLLO DESARROLLOS PROYECTO PROYECTOS INVERSIONES PARQUE "
    "PARQUES PLANTA PLANTAS HOLDING HOLDINGS GRUPO GAS REDES RED SERVICIOS GESTION FOTOVOLTAICA FOTOVOLTAICAS "
    "POTENCIA SOCIEDAD SOCIEDADES DE DEL LA LAS LOS EL Y E EN".split()
)


def generica(clave: str) -> bool:
    """«Energía, S.L.» o «Solares, S.L.U.»: un trozo de denominación que no identifica a nadie. Suele salir de una
    denominación partida en dos líneas, en el anexo o en el promotor de una DIA, y nunca vale como prueba."""
    # «FV100» identifica («Planta FV100, S.L.»); un número suelto o una palabra del sector, no. Con tres o más
    # palabras con contenido ya es una denominación entera («Desarrollos Renovables Eólicos y Solares»).
    utiles = [p for p in clave.split() if len(p) > 2 and not p.isdigit() and p not in {"DEL", "LAS", "LOS"}]
    if not any(c.isalpha() for c in clave):
        return True
    return len(utiles) <= 2 and all(p in _GENERICAS for p in utiles)


def indice(anexos: dict[str, dict]) -> dict[str, list[tuple[str, dict]]]:
    """clave de sociedad → [(id de cotizada, fila del anexo)]."""
    idx: dict[str, list[tuple[str, dict]]] = {}
    for cid, a in anexos.items():
        vistas: set[str] = set()
        for f in a.get("filas", []):
            for k in f["claves"]:
                if k not in vistas and not generica(k):
                    vistas.add(k)
                    idx.setdefault(k, []).append((cid, f))
    return idx
