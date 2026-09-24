"""python -m cartera [--anexos]   → recalcula docs/datos/cartera.json y la página."""
from __future__ import annotations

import argparse
import sys

from . import anexos, cartera, web


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cartera", description=__doc__)
    ap.add_argument("--anexos", action="store_true", help="vuelve a leer todos los PDF de cuentas consolidadas")
    args = ap.parse_args(argv)
    if args.anexos:
        anexos.actualizar(forzar=True)
    datos = cartera.construir()
    cartera.escribir(datos)
    web.escribir(datos)
    for c in datos["cotizadas"]:
        r = c["resumen"]
        print(f"  {c['nombre']:<28} {r['sociedades']:>4} soc  {r['instalaciones']:>4} inst  {r['mw']:>9.1f} MW"
              f"  {r['resoluciones']:>3} resol  {r['indicios']:>3} indicios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
