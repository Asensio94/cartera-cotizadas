"""Reúne, por cotizada, sus sociedades, sus instalaciones en el BOE, sus DIA con su condicionado y sus indicios de
fraccionamiento, y escribe docs/datos/cartera.json. Cada cifra conserva los identificadores que permiten comprobarla.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta

from . import anexos, config, natura
from . import propiedad as pr
from .atribucion import Atribucion, Atribuidor

BORME = "https://www.boe.es/diario_borme/txt.php?id={}"
CONDICIONADO_WEB = "https://asensio94.github.io/observatorio-alegaciones/condicionado.html"
GRAFO_WEB = "https://asensio94.github.io/grafo-promotores/"


def _promotores(texto: str) -> list[str]:
    """«Elawan Fotovoltaica Escuderos 1, SL, y Elawan Fotovoltaica Escuderos 4, SL» → dos sociedades."""
    texto = re.sub(r",?\s+y\s+(?=[A-ZÁÉÍÓÚÑ])", ", ", texto or "")
    partes = pr.so.partir_denominaciones(texto) or [texto]
    return [p for p in partes if p.strip()]


# prefijos de tecnología con que un mismo proyecto aparece unas veces sí y otras no («PSF Aura» y «Aura»)
_PREFIJO = re.compile(
    r"^(?:PROYECTO\s+)?(?:PSFV|PSF|PFV|PFOT|PF|P\s?F|FV|ISF|HSF|PE|PEOL|PARQUE\s+EOLICO|PARQUE\s+FOTOVOLTAICO|"
    r"PLANTA\s+FOTOVOLTAICA|PLANTA\s+SOLAR\s+FOTOVOLTAICA|INSTALACION\s+SOLAR\s+FOTOVOLTAICA)\s+"
)


def _sin_duplicados(inst: list[dict]) -> list[dict]:
    """Une las instalaciones que son la misma con y sin prefijo de tecnología: misma clave sin el prefijo y misma
    potencia. Dos plantas gemelas del mismo titular (mismos MW, otro nombre) se quedan separadas: eso es justo lo
    que miran los indicios de fraccionamiento."""
    vistas: dict[tuple, dict] = {}
    out = []
    for i in inst:
        k = (_PREFIJO.sub("", i["id"]).strip(), round(i["mw"] or 0, 2))
        if k[1] and k in vistas:
            j = vistas[k]
            j.setdefault("tambien", []).append(i["nombre"])
            j["titulares"] = sorted(set(j["titulares"]) | set(i["titulares"]))
            j["actos"] = sorted({a["id"]: a for a in j["actos"] + i["actos"]}.values(), key=lambda a: a["fecha"])[-3:]
            continue
        vistas[k] = i
        out.append(i)
    return out


def _nombre(sid: str, soc: dict, a: Atribucion | None = None) -> str:
    """La denominación probada: la que coincide con la clave, aunque el grafo conozca otras de la misma sociedad."""
    nombres = (soc.get(sid) or {}).get("nombres") or []
    for n in nombres:
        if pr.so.clave(n) == sid:
            return n
    if nombres:
        return nombres[0]
    if a and a.fila and a.via == "anexo" and pr.so.clave(a.fila["texto"]) == sid:
        return a.fila["texto"]
    return sid.title()


def _evidencia(a: Atribucion, docs: dict[str, dict]) -> dict:
    d = docs.get(a.fila.get("documento"), {})
    return {
        "via": a.via,
        "estado": a.estado,
        "anexo": {
            "documento": a.fila.get("documento"),
            "titulo": d.get("titulo", ""),
            "pagina": a.fila.get("pagina"),
            "folio": a.fila.get("folio"),
            "fila": a.fila.get("contexto") or a.fila.get("texto"),
        },
        "borme": [
            {"hija": e.hija, "madre": e.madre, "nombre_madre": e.nombre_madre, "fecha": e.fecha, "url": e.url}
            for e in a.eslabones
        ],
        "otras": [{"cotizada": c, "via": v} for c, v in a.otras],
    }


def construir(aviso=print) -> dict:
    cot = anexos.cotizadas()
    meta = {c["id"]: c for c in cot}
    docs = {d["url"]: d for c in cot for d in c.get("documentos", [])}
    anx = anexos.actualizar(aviso=aviso)
    atr = Atribuidor(anexos.indice(anx), cot)

    g = pr.grafo()
    soc = g["sociedades"]
    fichas = json.loads((config.CONDICIONADO / "indice.json").read_text(encoding="utf-8"))["fichas"]
    nat = natura.actualizar(fichas, aviso=aviso)

    por: dict[str, dict] = {c["id"]: {"sociedades": {}, "instalaciones": [], "dia": [], "indicios": []} for c in cot}

    def apuntar(sid: str) -> Atribucion | None:
        a = atr.atribuir(sid)
        if a:
            por[a.cotizada]["sociedades"].setdefault(sid, {
                "id": sid, "nombre": _nombre(sid, soc, a), **_evidencia(a, docs),
                # el grafo reúne varios NIF bajo esta denominación: se avisa, porque un NIF no cambia nunca
                "nifs_en_grafo": len((soc.get(sid) or {}).get("nifs") or [])})
        return a

    # instalaciones: una sociedad de la cotizada figura como titular en algún anuncio del BOE
    for inst in g["instalaciones"].values():
        tit = [pr.resolver(t) for t in inst.get("titulares", [])]
        hits = {}
        for sid in tit:
            a = apuntar(sid)
            if a:
                hits.setdefault(a.cotizada, []).append(sid)
        for cid, sids in hits.items():
            por[cid]["instalaciones"].append({
                "id": inst["id"],
                "nombre": (inst.get("nombres") or [inst["id"]])[0],
                "mw": inst.get("mw") or 0,
                "tecnologias": inst.get("tecnologias", []),
                "provincias": inst.get("provincias", []),
                "municipios": inst.get("municipios", [])[:4],
                "titulares": sorted(set(sids)),
                "compartida": sorted(set(hits) - {cid}),
                "primera": inst.get("primera"),
                "ultima": inst.get("ultima"),
                "actos": [{"id": x["id"], "fecha": x["fecha"], "acto": x["acto"], "url": x["url"]}
                          for x in inst.get("actos", [])][-3:],
            })

    # declaraciones de impacto ambiental cuyo promotor es una sociedad de la cotizada
    hoy = date.today()
    for f in fichas:
        cids = {}
        for p in _promotores(f.get("promotor", "")):
            sid = pr.resolver(p)
            a = apuntar(sid)
            if a:
                cids.setdefault(a.cotizada, sid)
        n = nat.get(f["identificador"], {"nivel": "sin_mencion", "cita": ""})
        for cid, sid in cids.items():
            vence = f.get("vigencia_hasta")
            por[cid]["dia"].append({
                "id": f["identificador"],
                "tipo": f.get("tipo"),
                "fecha": f.get("fecha_publicacion"),
                "proyecto": f.get("proyecto"),
                "promotor": f.get("promotor"),
                "sociedad": sid,
                "categoria": f.get("categoria"),
                "provincias": f.get("provincias", []),
                "sentido": f.get("sentido"),
                "sentido_etiqueta": f.get("sentido_etiqueta"),
                "condiciones": f.get("n_condiciones", 0),
                "entregables": f.get("n_entregables", 0),
                "mortalidad": bool(f.get("seguimiento_mortalidad")),
                "temas": f.get("temas", []),
                "vigencia_hasta": vence,
                "vence_pronto": bool(vence and hoy.isoformat() <= vence <= (hoy + timedelta(days=365)).isoformat()),
                "natura": n["nivel"],
                "natura_cita": n["cita"],
                "url": f.get("url_html"),
                "anulada": bool(f.get("anulada")),
            })

    # indicios de fraccionamiento del grafo en los que participa alguna sociedad de la cotizada
    for ind in g["indicios"]:
        cids = {}
        for t in ind.get("titulares", []):
            a = apuntar(pr.resolver(t))
            if a:
                cids.setdefault(a.cotizada, []).append(t)
        for cid, tits in cids.items():
            por[cid]["indicios"].append({
                "id": ind["id"], "peso": ind.get("peso"), "suma_mw": ind.get("suma_mw"),
                "instalaciones": ind.get("instalaciones", []), "provincias": ind.get("provincias", []),
                "desde": ind.get("desde"), "hasta": ind.get("hasta"),
                "senales": [s["texto"] for s in ind.get("senales", [])], "titulares": tits,
                "otras_cotizadas": sorted(set(cids) - {cid}),
            })

    for p in por.values():
        p["instalaciones"] = _sin_duplicados(p["instalaciones"])

    salida = []
    for c in cot:
        p = por[c["id"]]
        inst, dia = p["instalaciones"], p["dia"]
        tec = Counter()
        for i in inst:
            for t in i["tecnologias"] or ["sin_dato"]:
                tec[t] += i["mw"] / max(1, len(i["tecnologias"] or [1]))
        socs = sorted(p["sociedades"].values(), key=lambda s: (s["via"] != "anexo", s["nombre"]))
        dias = [d for d in dia if d["tipo"] == "dia"]
        salida.append({
            "id": c["id"],
            "nombre": c["nombre"],
            "mercado": c.get("mercado"),
            "matriz": c.get("matriz"),
            "nota": c.get("nota", ""),
            "documentos": c.get("documentos", []),
            "filas_anexo": len(anx.get(c["id"], {}).get("filas", [])),
            "resumen": {
                "sociedades": len(socs),
                "por_anexo": sum(s["via"] == "anexo" for s in socs),
                "por_cadena": sum(s["via"] == "cadena" for s in socs),
                "en_conflicto": sum(s["estado"] == "conflicto" for s in socs),
                "instalaciones": len(inst),
                "mw": round(sum(i["mw"] for i in inst), 1),
                "mw_por_tecnologia": {k: round(v, 1) for k, v in tec.most_common()},
                "resoluciones": len(dia),
                "dia": len(dias),
                "dia_desfavorables": sum(d["sentido"] == "desfavorable" for d in dias),
                "condiciones": sum(d["condiciones"] for d in dia),
                "con_mortalidad": sum(d["mortalidad"] for d in dia),
                "con_parada": sum("parada" in d["temas"] for d in dia),
                "con_compensatoria": sum("compensatoria" in d["temas"] for d in dia),
                "vencen_12_meses": sum(d["vence_pronto"] for d in dia),
                "natura": dict(Counter(d["natura"] for d in dia)),
                "indicios": len(p["indicios"]),
                "mw_en_indicios": round(sum(i["suma_mw"] or 0 for i in p["indicios"]), 1),
            },
            "sociedades": socs,
            "instalaciones": sorted(inst, key=lambda i: -i["mw"]),
            "dia": sorted(dia, key=lambda d: d["fecha"] or "", reverse=True),
            "indicios": sorted(p["indicios"], key=lambda i: -(i["peso"] or 0)),
            "litigios": None,  # pendiente de datos: no hay fuente abierta y estructurada
            "cumplimiento": None,  # pendiente de datos: los informes de seguimiento no se publican de forma abierta
        })
    total_mw = sum(i.get("mw") or 0 for i in g["instalaciones"].values())
    return {
        "generado": date.today().isoformat(),
        "fuentes": {
            "grafo": g.get("generado"),
            "condicionado": json.loads((config.CONDICIONADO / "indice.json").read_text(encoding="utf-8")).get("generado"),
            "instalaciones_boe": len(g["instalaciones"]),
            "mw_boe": round(total_mw, 1),
            "resoluciones": len(fichas),
        },
        "natura_etiquetas": natura.ETIQUETA,
        "cotizadas": sorted(salida, key=lambda c: c["nombre"]),
    }


def escribir(datos: dict) -> None:
    ruta = config.DOCS / "datos" / "cartera.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
