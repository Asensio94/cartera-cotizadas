# Cartera de las cotizadas

Qué proyectos energéticos tramita en España cada empresa cotizada, qué le exigieron sus declaraciones de
impacto ambiental, qué dicen esas declaraciones de la Red Natura 2000 y en qué indicios de fraccionamiento
aparecen sus sociedades. Cada cifra enlaza a su fuente.

**Web:** https://asensio94.github.io/cartera-cotizadas/

No es asesoramiento de inversión. No hay puntuaciones ni clasificaciones: las cotizadas se ordenan
alfabéticamente y cada dato se enseña con el documento que lo prueba.

## Cómo funciona

1. **Sociedades de cada cotizada.** Se lee el anexo de sociedades dependientes, asociadas y negocios conjuntos
   de sus cuentas anuales consolidadas (`data/cotizadas.json`) y se busca la coincidencia exacta de
   denominación social, sin forma jurídica, en las páginas con forma de tabla. Solo cuentan las formas
   jurídicas españolas (S.A., S.L., S.A.U., S.L.U., A.I.E.): la denominación es única dentro del Registro
   Mercantil, no entre países, y «Enel Green Power S.p.A.» no es «Enel Green Power, S.L.».
2. **Cuando el documento no se deja descargar.** Cuando la web de la cotizada no deja descargar el documento a
   un programa (Iberdrola) o pide resolver un CAPTCHA (Audax), se usa el informe financiero anual que la propia
   empresa deposita en la [CNMV](https://www.cnmv.es/portal/consultas/ifa/listadoifa?id=0&lang=es) en formato
   electrónico ESEF (XHTML). De ese formato solo se leen las celdas de tabla, así que una sociedad citada en la
   prosa de una nota nunca cuenta, y la prueba cita el folio impreso además de la página del XHTML.
3. **Cadena de propiedad.** Si una sociedad no figura en un anexo, se mira en el BORME su última declaración de
   socio único vigente (incluido el cambio de socio único con que se inscribe la venta de una SPV) y se sube
   eslabón a eslabón hasta una sociedad que figure en un anexo.
4. **Nunca por parecido de nombre.** Nunca se asigna una sociedad por parecido de nombre. Una sociedad que lleva
   a dos cotizadas que no son matriz y filial entre sí queda «en conflicto» y se enseñan las dos pruebas.
5. **Instalaciones, resoluciones e indicios.** Con las sociedades probadas se recogen sus instalaciones en el
   BOE, sus declaraciones de impacto ambiental y sus indicios de fraccionamiento (tabla de abajo).
6. **Red Natura 2000.** Cada resolución se clasifica por lo que declara su propio texto, con la frase citada
   (niveles abajo).

### De dónde sale cada cosa

| Dato | Fuente | Cómo se usa |
|---|---|---|
| Sociedades de cada cotizada | Anexo de sociedades dependientes, asociadas y negocios conjuntos de sus cuentas anuales consolidadas (`data/cotizadas.json`) | Coincidencia exacta de denominación social, sin forma jurídica, en las páginas con forma de tabla |
| Cadena de propiedad | BORME: última declaración de socio único vigente (incluido el cambio de socio único con que se inscribe la venta de una SPV) | Se sube eslabón a eslabón hasta una sociedad que figure en un anexo |
| Instalaciones y potencia | [Grafo de promotores](https://github.com/Asensio94/grafo-promotores): anuncios del BOE desde 2018 | Cuenta si una sociedad probada figura como titular en algún anuncio; la potencia es la de la instalación completa |
| Declaraciones de impacto ambiental | [Condicionado del observatorio](https://asensio94.github.io/observatorio-alegaciones/condicionado.html) | Por el promotor de la resolución |
| Red Natura 2000 | Texto de cada resolución en el BOE (`cartera/natura.py`) | Lo que declara la propia resolución, con la frase citada |
| Indicios de fraccionamiento | Grafo de promotores | Los indicios en los que figura alguna sociedad probada |

### Red Natura 2000: niveles

- **Dentro o atraviesa**: la resolución dice que el proyecto o una de sus partes está dentro, atraviesa, ocupa
  o afecta directamente a un espacio.
- **En el entorno**: colinda, está a 5 km o menos, o la resolución habla de afección indirecta.
- **Declara que no coincide**: lo niega expresamente, o el espacio más próximo está a más de 5 km.
- **Sin mención**.

Una frase con negación nunca cuenta como afección; las que hablan de alternativas descartadas o de espacios
propuestos bajan a «en el entorno». Si se cambian las reglas hay que subir `natura.VERSION` para que se
reclasifique todo.

## Contraste / validación

Pendiente.

### Derecho de réplica

Cualquier dato mal probado se corrige. Abre una
[réplica](https://github.com/Asensio94/cartera-cotizadas/issues/new?template=replica.yml) con el documento
público que lo demuestra; la respuesta queda en el mismo hilo.

## Límites

- No hay cruce cartográfico con la Red Natura 2000: se lee lo que declara cada resolución.
- La potencia es la de la instalación completa, aunque la cotizada solo tenga una parte.
- Los anexos son del cierre del ejercicio; una venta posterior se ve en el BORME y queda en conflicto.

## Pendiente

Quedan como **pendiente de datos**, a propósito: litigios, cumplimiento del condicionado y proyectos
autonómicos de menos de 50 MW que el BOE no recoge.

## Uso

```bash
pip install -r requirements.txt
python -m cartera            # recalcula docs/datos/cartera.json y docs/index.html
python -m cartera --anexos   # vuelve a leer todos los PDF de cuentas consolidadas
```

Por defecto busca `grafo-promotores` y `observatorio-alegaciones` en la carpeta de al lado; se pueden
indicar con `CARTERA_GRAFO` y `CARTERA_OBSERVATORIO`. En GitHub Actions el flujo `diario` hace checkout de
los dos repositorios, recalcula y publica en Pages.

Para añadir una cotizada, o el ejercicio siguiente, basta con añadir el PDF a `data/cotizadas.json`: la tabla
de sociedades leída se guarda en `data/anexos/` y el PDF no se vuelve a descargar mientras no cambie.

La página la genera `cartera/web.py`, que incrusta `cartera/common.css` (la hoja común de los proyectos
hermanos, copiada literal) y pone las cifras de la cabecera.

## Datos que se guardan

| Fichero | Contenido |
|---|---|
| `data/cotizadas.json` | Las cotizadas y los documentos de sus cuentas consolidadas |
| `data/anexos/<id>.json` | La tabla de sociedades leída del anexo de cada cotizada |
| `data/natura_dia.json` | El nivel de Red Natura 2000 de cada resolución, con la frase que lo prueba |
| `data/cache/` | PDF descargados (no se versiona) |
| `docs/datos/cartera.json` | Lo que enseña la web: por cotizada, sus sociedades, instalaciones, resoluciones e indicios |
| `docs/index.html` | La página |

## Fuentes y licencias

Código MIT. Los datos derivan de fuentes públicas (BOE, BORME, cuentas depositadas en la CNMV) y se publican
con enlace a cada una. Las instalaciones y los indicios vienen del
[grafo de promotores](https://github.com/Asensio94/grafo-promotores) y las declaraciones de impacto ambiental
del [condicionado del observatorio](https://asensio94.github.io/observatorio-alegaciones/condicionado.html).

Forma parte de un conjunto de proyectos hermanos: [Observatorio de alegaciones](https://asensio94.github.io/observatorio-alegaciones/) · [Vigía de incendios](https://asensio94.github.io/vigia-incendios/) · [Centinela Natura](https://asensio94.github.io/centinela-natura/) · [Vigilancia de humedales](https://asensio94.github.io/vigilancia-humedales/) · [Sub Nocte](https://asensio94.github.io/sub-nocte/) · [Riesgo de tendidos para aves](https://asensio94.github.io/riesgo-tendidos-aves/) · [Grafo de promotores](https://asensio94.github.io/grafo-promotores/) · [Cuaderno de campo](https://asensio94.github.io/cuaderno-campo/).
