"""La página pública: docs/index.html, que lee docs/datos/cartera.json."""
from __future__ import annotations

from pathlib import Path

from . import config
from .logo import LOGO_SVG, favicon_link

PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
__FAVICON__
<title>Cartera de las cotizadas</title>
<meta name="description" content="Qué proyectos energéticos tramita en España cada empresa cotizada, con sus declaraciones de impacto ambiental, su relación con la Red Natura 2000 y sus indicios de fraccionamiento. Cada cifra, con su fuente.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/*__COMMON_CSS__*/
:root{--accent:#0f6b6b;--accent-dark:#5cc4c4}
/* Repo tokens point to the common ones; only meaningful colours (Natura levels, warnings) keep their own values. */
:root{
  --suelo:var(--ground); --hoja:var(--paper); --tinta:var(--ink); --gris:var(--muted); --raya:var(--line); --raya-2:#e9e3de;
  --sello:var(--accent); --sello-suave:#dcefee; --sello-tinta:#ffffff;
  --dentro:#b3401a; --dentro-suave:#f8e3da; --entorno:#95680b; --entorno-suave:#f5ecd6;
  --fuera:#3d7350; --fuera-suave:#e0efe5; --nada:#6d7773; --nada-suave:#e9edeb;
  --aviso:#8a5a00;
  --serif:var(--font-text); --mono:var(--font-data);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --raya-2:#28211d; --sello-suave:#163331; --sello-tinta:var(--ground);
    --dentro:#f08a63; --dentro-suave:#3a2219; --entorno:#e0b54f; --entorno-suave:#352b14;
    --fuera:#79c08f; --fuera-suave:#1a3022; --nada:#98a39f; --nada-suave:#232c29; --aviso:#e0b54f;
  }
}
:root[data-theme="dark"]{
  --raya-2:#28211d; --sello-suave:#163331; --sello-tinta:var(--ground);
  --dentro:#f08a63; --dentro-suave:#3a2219; --entorno:#e0b54f; --entorno-suave:#352b14;
  --fuera:#79c08f; --fuera-suave:#1a3022; --nada:#98a39f; --nada-suave:#232c29; --aviso:#e0b54f;
}
html{-webkit-text-size-adjust:100%}
.mono,.num{font-family:var(--mono)}
.num{font-variant-numeric:tabular-nums}
.marca{font:600 13px/1.2 var(--font-title);letter-spacing:.08em;text-transform:uppercase;color:var(--gris)}
.avisos{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:3px 9px;border:1px solid var(--raya);font-size:13px;background:var(--hoja);color:var(--tinta)}
.chip b{font-weight:600}
.chip.sello{border-color:var(--sello);color:var(--sello)}
main{max-width:1440px;margin:0 auto;padding:22px 16px 40px;display:grid;grid-template-columns:270px minmax(0,1fr);gap:26px;align-items:start}
nav.lista{position:sticky;top:12px;display:grid;gap:10px}
nav.lista h2{font:600 13px/1.2 var(--font-title);letter-spacing:.08em;text-transform:uppercase;color:var(--gris);margin:0}
nav.lista .orden{font-size:12.5px;color:var(--gris);margin:0}
nav.lista ul{list-style:none;margin:0;padding:0;border-top:1px solid var(--raya)}
nav.lista li button{all:unset;box-sizing:border-box;cursor:pointer;display:grid;grid-template-columns:1fr auto;gap:8px;width:100%;padding:8px 8px;border-bottom:1px solid var(--raya-2);font-size:14.5px}
nav.lista li button:hover{background:var(--raya-2)}
nav.lista li button[aria-current="true"]{background:var(--sello);color:var(--sello-tinta)}
nav.lista li button[aria-current="true"] .num{color:var(--sello-tinta)}
nav.lista li button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
nav.lista li .num{font-size:12px;color:var(--gris);align-self:center}
nav.lista li button.vacia{color:var(--gris)}
nav.lista select{display:none}
.hoja{background:var(--hoja);border:1px solid var(--raya);box-shadow:var(--shadow)}
.ficha{padding:22px 22px 8px;display:grid;gap:14px}
.ficha h2{margin:0;font:700 clamp(28px,3.8vw,42px)/1 var(--font-title);text-wrap:balance}
.meta{display:flex;flex-wrap:wrap;gap:8px 16px;color:var(--gris);font-size:13.5px}
.docs{display:grid;gap:4px;font-size:13.5px}
.libro{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));border-top:1px solid var(--raya);margin:4px -22px 0}
.libro button{all:unset;box-sizing:border-box;cursor:pointer;padding:14px 22px 14px;border-right:1px solid var(--raya-2);border-bottom:1px solid var(--raya-2);display:grid;gap:2px}
.libro button:hover{background:var(--raya-2)}
.libro button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.libro .v{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:24px;font-weight:500;line-height:1.1}
.libro .e{font-size:12.5px;color:var(--gris)}
.libro .pend .v{font-size:15px;color:var(--aviso);font-family:var(--serif);font-weight:600}
.pestanas{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--raya);padding:0 12px;background:var(--hoja);position:sticky;top:0;z-index:2}
.pestanas button{all:unset;cursor:pointer;padding:11px 12px;font:600 15px/1.2 var(--font-title);letter-spacing:.04em;text-transform:uppercase;border-bottom:3px solid transparent;color:var(--gris)}
.pestanas button[aria-selected="true"]{color:var(--tinta);border-bottom-color:var(--sello)}
.pestanas button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.panel{padding:16px 22px 26px}
.panel p.intro{margin:0 0 12px;color:var(--gris);max-width:75ch;font-size:14px}
.tabla{overflow-x:auto;border:1px solid var(--raya-2)}
.tabla table{border-collapse:collapse;width:100%;font-size:13.5px}
.tabla th{font:600 13px/1.3 var(--font-title);text-align:left;color:var(--gris);text-transform:uppercase;letter-spacing:.05em;padding:8px 10px;border-bottom:1px solid var(--raya);background:var(--raya-2);position:sticky;top:0}
.tabla td{padding:8px 10px;border-bottom:1px solid var(--raya-2);vertical-align:top}
.tabla td.num,.tabla th.num{text-align:right;white-space:nowrap}
.tabla tr:last-child td{border-bottom:0}
.aviso-nif{font-size:11.5px;color:var(--gris)}
.pill{display:inline-block;padding:1px 7px;border-radius:2px;font-size:12px;font-weight:600;white-space:nowrap}
.n-dentro{background:var(--dentro-suave);color:var(--dentro)}
.n-entorno{background:var(--entorno-suave);color:var(--entorno)}
.n-fuera{background:var(--fuera-suave);color:var(--fuera)}
.n-sin_mencion{background:var(--nada-suave);color:var(--nada)}
.p-anexo{background:var(--sello-suave);color:var(--sello)}
.p-cadena{background:var(--raya-2);color:var(--tinta)}
.p-conflicto{background:var(--dentro-suave);color:var(--dentro)}
.cita{margin:6px 0 0;padding-left:10px;border-left:2px solid var(--raya);color:var(--gris);font-size:13px}
.barra{display:flex;height:10px;border-radius:2px;overflow:hidden;background:var(--raya-2);margin:6px 0 4px;max-width:520px}
.barra span{display:block;height:100%}
.leyenda{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--gris)}
.leyenda i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.filtro{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}
.filtro input,.filtro select{font:inherit;font-size:14px;padding:6px 9px;border:1px solid var(--raya);border-radius:3px;background:var(--hoja);color:var(--tinta);min-width:0;max-width:100%}
.filtro input{flex:1 1 220px}
details.cadena summary{cursor:pointer;color:var(--sello);font-size:12.5px}
details.cadena ol{margin:6px 0 0;padding-left:18px;font-size:12.5px;color:var(--gris)}
.vacio{padding:18px;color:var(--gris);font-size:14px;border:1px dashed var(--raya);border-radius:3px}
.pendiente{display:grid;gap:12px;max-width:75ch}
.pendiente h3{margin:0;font:600 17px/1.2 var(--font-title);text-transform:uppercase;letter-spacing:.05em}
.pendiente p{margin:0;color:var(--gris);font-size:14px}
.method ol.pasos{padding-left:24px}
.method ol.pasos li{margin:0 0 10px}
.method ol.pasos li::marker{font-family:var(--font-data);color:var(--accent)}
.method .params{margin:6px 0 4px}
.mas{font-size:13px;color:var(--gris);margin:10px 0 0}
@media (max-width:860px){
  main{grid-template-columns:minmax(0,1fr)}
  nav.lista{position:static}
  nav.lista ul{display:none}
  nav.lista select{display:block;font:inherit;padding:8px;border:1px solid var(--raya);border-radius:3px;background:var(--hoja);color:var(--tinta);width:100%}
  .ficha{padding:18px 16px 6px}
  .libro{margin:4px -16px 0}
  .libro button{padding:12px 16px}
  .panel{padding:14px 16px 22px}
  .pestanas{padding:0 4px}
  .pestanas button{padding:10px 8px}
}
@media (max-width:640px){
  table.params th{white-space:normal}
}
@media (prefers-reduced-motion:no-preference){.libro button,nav.lista li button{transition:background .12s}}
</style>
</head>
<body>
<header class="site-header">
  <div class="marca">Registro público · BOE · BORME · cuentas consolidadas</div>
  <h1>__LOGO__Cartera de las <span>cotizadas</span></h1>
  <p class="lede">Qué proyectos energéticos tramita en España cada empresa cotizada, qué le exigieron sus declaraciones de impacto ambiental y qué dicen esas declaraciones de la Red Natura 2000, con los anuncios del BOE desde 2018, el BORME y los anexos de sus cuentas consolidadas.</p>
  <div class="figures">
<!--__FIGURES__-->
  </div>
  <div class="avisos">
    <span class="chip sello"><b>No es asesoramiento de inversión</b></span>
    <span class="chip">Sin puntuaciones ni clasificaciones</span>
    <span class="chip">Cada cifra enlaza a su fuente</span>
    <a class="chip" href="https://github.com/Asensio94/cartera-cotizadas/issues/new?template=replica.yml">Derecho de réplica</a>
  </div>
</header>
<main>
  <nav class="lista" aria-label="Cotizadas">
    <h2>Cotizadas</h2>
    <p class="orden">En orden alfabético. La cifra es la potencia en el BOE, no una clasificación.</p>
    <ul id="lista"></ul>
    <select id="lista-movil" aria-label="Elegir cotizada"></select>
  </nav>
  <div id="ficha" class="hoja" aria-live="polite"><div class="ficha"><p>Cargando…</p></div></div>
</main>
<section class="method" id="metodo">
  <h2>Cómo se calcula</h2>
  <p>Una sociedad solo se asigna a una cotizada cuando la propia cotizada la declara en el anexo de sus cuentas consolidadas, o cuando su socio único inscrito en el BORME lleva hasta una que sí figura.</p>
  <ol class="pasos">
    <li><b>Quién es de quién.</b> La prueba principal es el anexo de sociedades dependientes, asociadas y negocios conjuntos de las cuentas anuales consolidadas de cada cotizada, formuladas por sus administradores, auditadas y depositadas en la CNMV. Se leen solo las páginas con forma de tabla de sociedades y se busca la denominación exacta, sin la forma jurídica: en el Registro Mercantil una denominación no se repite. Por eso solo cuentan las formas jurídicas españolas («Enel Green Power S.p.A.» no es «Enel Green Power, S.L.») y nunca un trozo de denominación que no identifica a nadie («Energía, S.L.»).</li>
    <li><b>Cuando no se puede descargar.</b> Cuando la web de la cotizada no deja descargar el documento a un programa o pide resolver un CAPTCHA, se usa el informe financiero anual que la empresa deposita en la CNMV en formato electrónico ESEF. De ese formato solo se leen las celdas de tabla, y la prueba cita el folio impreso, que es lo que se busca al abrir el documento.</li>
    <li><b>El BORME, eslabón a eslabón.</b> La segunda prueba es el BORME: la última declaración de socio único inscrita, incluido el cambio de socio único con el que se inscribe la venta de una sociedad vehículo, mientras la sociedad no pierda después la unipersonalidad. Se sube eslabón a eslabón hasta una sociedad que figure en un anexo.</li>
    <li><b>Lo que no se hace.</b> No se asigna nada por parecido de nombre. Una sociedad que lleva a dos cotizadas que no son matriz y filial entre sí aparece «en conflicto», con las dos pruebas. Cuando una cotizada y su matriz cotizada declaran la misma sociedad (Endesa y Enel, EDP Renováveis y EDP), se asigna a la más cercana.</li>
    <li><b>Instalaciones y potencia.</b> Una instalación cuenta para una cotizada si alguna de sus sociedades figura como titular en algún anuncio del BOE desde 2018, según el <a href="https://asensio94.github.io/grafo-promotores/">grafo de promotores</a>. La potencia es la de la instalación completa, aunque la cotizada solo tenga una parte.</li>
    <li><b>Evaluación ambiental.</b> Se toman las declaraciones e informes de impacto ambiental del <a href="https://asensio94.github.io/observatorio-alegaciones/condicionado.html">condicionado del observatorio</a> cuyo promotor es una sociedad probada, con sus condiciones, el seguimiento de mortalidad y la fecha en que caducan.</li>
    <li><b>Red Natura 2000.</b> No hay cruce cartográfico: se lee lo que declara la propia resolución del BOE y se enseña la frase. «Dentro o atraviesa» cuando dice que el proyecto o una de sus partes está dentro, atraviesa, ocupa o afecta directamente a un espacio; «en el entorno» cuando colinda, da una distancia o habla de afección indirecta; «declara que no coincide» cuando lo niega expresamente. Una frase con negación nunca cuenta como afección, y las que hablan de alternativas descartadas bajan a «entorno».</li>
    <li><b>Fraccionamiento.</b> Se recogen los indicios del grafo de promotores en los que figura alguna sociedad probada: conjuntos de instalaciones que por separado quedan por debajo de 50 MW y juntas lo superan.</li>
    <li><b>Las cifras de arriba.</b> Suman todas las cotizadas de la página y cuentan cada instalación, resolución y sociedad una sola vez, aunque aparezca en dos cotizadas.</li>
  </ol>
  <h3>Parámetros</h3>
  <table class="params">
    <tbody>
      <tr><th scope="row">Denominación</th><td>Coincidencia exacta, sin la forma jurídica</td></tr>
      <tr><th scope="row">Formas jurídicas</th><td>Solo españolas: S.A., S.L., S.A.U., S.L.U., A.I.E.</td></tr>
      <tr><th scope="row">Anuncios del BOE</th><td>Desde 2018</td></tr>
      <tr><th scope="row">«En el entorno»</th><td>Colinda, a 5 km o menos, o afección indirecta</td></tr>
      <tr><th scope="row">«Declara que no coincide»</th><td>Lo niega expresamente, o el espacio más próximo está a más de 5 km</td></tr>
      <tr><th scope="row">Fraccionamiento</th><td>Por separado, por debajo de 50 MW (competencia autonómica); juntas, por encima</td></tr>
      <tr><th scope="row">Caducidad próxima</th><td>La DIA caduca en los próximos 12 meses</td></tr>
    </tbody>
  </table>
  <h3>Validación</h3>
  <p>Pendiente. Cada cifra enlaza al documento que la prueba. ¿Una cifra está mal? Abre una <a href="https://github.com/Asensio94/cartera-cotizadas/issues/new?template=replica.yml">réplica</a> con el documento que lo prueba: se corrige y se deja constancia.</p>
  <h3>Límites</h3>
  <p>Faltan los proyectos autonómicos (menos de 50 MW, salvo los que el grafo recoge del BOE), los litigios y el cumplimiento del condicionado: no hay fuentes abiertas y estructuradas. Los anexos son del cierre del ejercicio; una venta posterior se ve en el BORME y queda en conflicto. Los datos de base son el <a href="https://asensio94.github.io/grafo-promotores/">grafo de promotores</a> y el <a href="https://asensio94.github.io/observatorio-alegaciones/condicionado.html">condicionado del observatorio</a>.</p>
</section>
<footer class="site-footer">
  <p class="principle">Datos públicos, reglas a la vista y cada cifra enlazada a su fuente. Indicios, no veredictos.</p>
  <p id="pie"></p>
  <p>Código MIT. Los datos derivan de fuentes públicas (BOE, BORME, cuentas depositadas en la CNMV) y se publican con enlace a cada una.</p>
  <nav aria-label="Proyectos hermanos"><ul class="siblings">
    <li><a href="https://asensio94.github.io/observatorio-alegaciones/">Observatorio de alegaciones</a></li>
    <li><a href="https://asensio94.github.io/vigia-incendios/">Vigía de incendios</a></li>
    <li><a href="https://asensio94.github.io/centinela-natura/">Centinela Natura</a></li>
    <li><a href="https://asensio94.github.io/vigilancia-humedales/">Vigilancia de humedales</a></li>
    <li><a href="https://asensio94.github.io/sub-nocte/">Sub Nocte</a></li>
    <li><a href="https://asensio94.github.io/riesgo-tendidos-aves/">Riesgo de tendidos para aves</a></li>
    <li><a href="https://asensio94.github.io/grafo-promotores/">Grafo de promotores</a></li>
    <li aria-current="page"><a href="https://asensio94.github.io/cartera-cotizadas/">Cartera de las cotizadas</a></li>
    <li><a href="https://asensio94.github.io/cuaderno-campo/">Cuaderno de campo</a></li>
  </ul></nav>
</footer>
<script>
const $ = (s, el=document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt = (n, d=0) => Number(n||0).toLocaleString("es-ES", {minimumFractionDigits:d, maximumFractionDigits:d});
const fecha = iso => iso ? new Date(iso+"T12:00:00").toLocaleDateString("es-ES",{day:"numeric",month:"short",year:"numeric"}) : "—";
const TEC = {eolica:"Eólica", fotovoltaica:"Fotovoltaica", hibridacion:"Hibridación", almacenamiento:"Almacenamiento", termosolar:"Termosolar", hidraulica:"Hidráulica", biomasa:"Biomasa", hidrogeno:"Hidrógeno", sin_dato:"Sin dato"};
const NIV = ["dentro","entorno","fuera","sin_mencion"];
let D, actual, pestana = "instalaciones";

function leerHash(){
  const p = new URLSearchParams(location.hash.slice(1));
  return {c: p.get("c"), t: p.get("t")};
}
function ponerHash(){ history.replaceState(null, "", "#c="+actual.id+"&t="+pestana); }

function lista(){
  const ul = $("#lista"), sel = $("#lista-movil");
  ul.innerHTML = D.cotizadas.map(c => `<li><button type="button" data-id="${c.id}" class="${c.resumen.instalaciones||c.resumen.resoluciones?"":"vacia"}"><span>${esc(c.nombre)}</span><span class="num">${fmt(c.resumen.mw)} MW</span></button></li>`).join("");
  sel.innerHTML = D.cotizadas.map(c => `<option value="${c.id}">${esc(c.nombre)} · ${fmt(c.resumen.mw)} MW</option>`).join("");
  ul.addEventListener("click", e => { const b = e.target.closest("button"); if (b) elegir(b.dataset.id); });
  sel.addEventListener("change", () => elegir(sel.value));
}

function elegir(id, t){
  actual = D.cotizadas.find(c => c.id === id) || D.cotizadas[0];
  if (t) pestana = t;
  document.querySelectorAll("#lista button").forEach(b => b.setAttribute("aria-current", b.dataset.id === actual.id));
  $("#lista-movil").value = actual.id;
  ficha(); ponerHash();
}

function barraNatura(n){
  const tot = NIV.reduce((a,k)=>a+(n[k]||0),0);
  if (!tot) return "";
  const col = {dentro:"var(--dentro)",entorno:"var(--entorno)",fuera:"var(--fuera)",sin_mencion:"var(--nada)"};
  return `<div class="barra" role="img" aria-label="Reparto de resoluciones por su relación con la Red Natura 2000">${NIV.map(k => n[k] ? `<span style="width:${100*n[k]/tot}%;background:${col[k]}"></span>`:"").join("")}</div>
  <div class="leyenda">${NIV.map(k => `<span><i style="background:${col[k]}"></i>${esc(D.natura_etiquetas[k])}: <b class="num">${n[k]||0}</b></span>`).join("")}</div>`;
}

function filiales(c){
  const f = D.cotizadas.filter(x => x.matriz === c.id);
  return f.length ? ` Sus sociedades en España que también declara ${f.length>1?"una filial cotizada":"su filial cotizada"} se cuentan allí: ${f.map(x => `<a href="#c=${x.id}" data-ir="${x.id}">${esc(x.nombre)}</a>`).join(", ")}.` : "";
}

function ficha(){
  const c = actual, r = c.resumen;
  const docs = (c.documentos||[]).map(d => `<div>Anexo de sociedades: <a href="${esc(d.url)}" rel="noopener">${esc(d.titulo)}</a>${d.paginas?` <span class="mono">(págs. ${esc(d.paginas)})</span>`:""}</div>`).join("") || `<div>Sin documento de perímetro todavía: no se asigna ninguna sociedad.</div>`;
  const celdas = [
    ["instalaciones", fmt(r.mw), "MW en el BOE desde 2018"],
    ["instalaciones", fmt(r.instalaciones), "instalaciones"],
    ["resoluciones", fmt(r.resoluciones), "resoluciones de evaluación ambiental"],
    ["resoluciones", fmt(r.condiciones), "condiciones impuestas"],
    ["resoluciones", fmt(r.con_mortalidad), "con seguimiento de mortalidad"],
    ["resoluciones", fmt(r.natura.dentro||0), "declaran Red Natura dentro"],
    ["resoluciones", fmt(r.vencen_12_meses), "DIA que caducan en 12 meses"],
    ["indicios", fmt(r.indicios), "indicios de fraccionamiento"],
    ["sociedades", fmt(r.sociedades), `sociedades (${fmt(r.por_anexo)} por anexo, ${fmt(r.por_cadena)} por BORME)`],
  ];
  $("#ficha").innerHTML = `
  <div class="ficha">
    <div class="marca">${esc(c.mercado||"")}${c.matriz?` · filial cotizada de ${esc((D.cotizadas.find(x=>x.id===c.matriz)||{}).nombre||c.matriz)}`:""}</div>
    <h2>${esc(c.nombre)}</h2>
    ${c.nota?`<div class="meta">${esc(c.nota)}</div>`:""}
    ${filiales(c)?`<div class="meta">${filiales(c).trim()}</div>`:""}
    <div class="docs">${docs}</div>
    <div class="libro">
      ${celdas.map(([t,v,e]) => `<button type="button" data-t="${t}"><span class="v">${v}</span><span class="e">${e}</span></button>`).join("")}
      <button type="button" data-t="pendiente" class="pend"><span class="v">Pendiente de datos</span><span class="e">litigios y cumplimiento</span></button>
    </div>
  </div>
  <div class="pestanas" role="tablist">
    ${[["instalaciones","Instalaciones"],["resoluciones","Evaluación ambiental"],["indicios","Fraccionamiento"],["sociedades","Pruebas de propiedad"],["pendiente","Pendiente"]].map(([k,t]) => `<button type="button" role="tab" data-t="${k}" aria-selected="${k===pestana}">${t}</button>`).join("")}
  </div>
  <div class="panel" id="panel"></div>`;
  $("#ficha").querySelectorAll("[data-t]").forEach(b => b.addEventListener("click", () => { pestana = b.dataset.t; ficha(); ponerHash(); if (b.closest(".libro")) $(".pestanas").scrollIntoView({block:"start"}); }));
  panel();
}

function tablaFiltrable(filas, cab, fila, filtros, ayuda){
  const el = $("#panel");
  el.innerHTML = `${ayuda}<div class="filtro">${filtros}</div><div class="tabla"><table><thead><tr>${cab}</tr></thead><tbody></tbody></table></div><p class="mas" id="cuenta"></p>`;
  const tb = el.querySelector("tbody");
  const pinta = () => {
    const q = (el.querySelector("input")?.value||"").toLowerCase();
    const sels = [...el.querySelectorAll(".filtro select")].map(s => [s.dataset.k, s.value]);
    const vis = filas.filter(f => (!q || JSON.stringify(f).toLowerCase().includes(q)) && sels.every(([k,v]) => !v || (Array.isArray(f[k]) ? f[k].includes(v) : String(f[k])===v)));
    tb.innerHTML = vis.slice(0, 400).map(fila).join("") || `<tr><td colspan="9" class="vacio">Nada con ese filtro.</td></tr>`;
    $("#cuenta").textContent = vis.length > 400 ? `Se muestran 400 de ${fmt(vis.length)}. Afina el filtro.` : `${fmt(vis.length)} filas.`;
  };
  el.querySelectorAll("input,select").forEach(i => i.addEventListener("input", pinta));
  pinta();
}

function opciones(k, valores, nombre, etiqueta=x=>x){
  const u = [...new Set(valores)].filter(Boolean).sort();
  return `<select data-k="${k}" aria-label="${nombre}"><option value="">${nombre}</option>${u.map(v => `<option value="${esc(v)}">${esc(etiqueta(v))}</option>`).join("")}</select>`;
}

function panel(){
  const c = actual, el = $("#panel");
  if (pestana === "instalaciones"){
    if (!c.instalaciones.length){ el.innerHTML = `<div class="vacio">Ninguna instalación del BOE tiene como titular una sociedad probada de ${esc(c.nombre)}.</div>`; return; }
    const tec = Object.entries(c.resumen.mw_por_tecnologia).map(([k,v]) => `${TEC[k]||k} <b class="num">${fmt(v)} MW</b>`).join(" · ");
    tablaFiltrable(c.instalaciones,
      `<th>Instalación</th><th class="num">MW</th><th>Tecnología</th><th>Provincia</th><th>Titular</th><th>Último anuncio</th>`,
      i => `<tr><td>${esc(i.nombre)}${i.tambien?`<br><span class="aviso-nif">También anunciada como ${esc(i.tambien.join(", "))}</span>`:""}${i.compartida.length?` <span class="pill p-conflicto">también ${esc(i.compartida.join(", "))}</span>`:""}</td><td class="num">${fmt(i.mw,1)}</td><td>${esc(i.tecnologias.map(t=>TEC[t]||t).join(", "))}</td><td>${esc(i.provincias.join(", ")||i.municipios.join(", "))}</td><td class="mono" style="font-size:12px">${esc(i.titulares.join(", "))}</td><td>${i.actos.length?i.actos.slice(-1).map(a=>`<a href="${esc(a.url)}">${esc(a.id)}</a><br><span class="mono" style="font-size:12px">${fecha(a.fecha)}</span>`).join(""):"—"}</td></tr>`,
      `<input type="search" placeholder="Buscar instalación, municipio, titular…" aria-label="Buscar">${opciones("tecnologias", c.instalaciones.flatMap(i=>i.tecnologias), "Todas las tecnologías", t=>TEC[t]||t)}${opciones("provincias", c.instalaciones.flatMap(i=>i.provincias), "Todas las provincias")}`,
      `<p class="intro">Por tecnología: ${tec}. La potencia es la de la instalación completa. Cada instalación enlaza a su último anuncio en el BOE.</p>`);
  } else if (pestana === "resoluciones"){
    if (!c.dia.length){ el.innerHTML = `<div class="vacio">Ninguna resolución de evaluación ambiental del BOE tiene como promotor una sociedad probada de ${esc(c.nombre)}.</div>`; return; }
    const S = {favorable:"Favorable", condicionada:"Con condiciones", desfavorable:"Desfavorable"};
    tablaFiltrable(c.dia,
      `<th>Resolución</th><th>Proyecto</th><th class="num">Condiciones</th><th>Red Natura 2000 según la resolución</th><th>Caduca</th>`,
      d => `<tr><td><a href="${esc(d.url)}">${esc(d.id)}</a><br><span class="mono" style="font-size:12px">${fecha(d.fecha)} · ${esc(d.tipo==="dia"?"DIA":d.tipo==="iia"?"IIA":d.tipo)}</span><br>${esc(d.sentido_etiqueta||S[d.sentido]||d.sentido||"")}</td><td>${esc(d.proyecto)}<br><span style="color:var(--gris);font-size:12.5px">${esc(d.promotor)}</span>${d.mortalidad?` <span class="pill p-cadena">seguimiento de mortalidad</span>`:""}${d.temas.includes("parada")?` <span class="pill p-cadena">parada</span>`:""}${d.temas.includes("compensatoria")?` <span class="pill p-cadena">compensatoria</span>`:""}</td><td class="num">${fmt(d.condiciones)}</td><td><span class="pill n-${d.natura}">${esc(D.natura_etiquetas[d.natura])}</span>${d.natura_cita?`<p class="cita">«${esc(d.natura_cita)}»</p>`:""}</td><td class="mono" style="font-size:12.5px;white-space:nowrap">${d.vigencia_hasta?fecha(d.vigencia_hasta):"—"}${d.vence_pronto?`<br><span class="pill n-entorno">en 12 meses</span>`:""}</td></tr>`,
      `<input type="search" placeholder="Buscar proyecto, provincia, frase…" aria-label="Buscar">${opciones("natura", c.dia.map(d=>d.natura), "Toda relación con Red Natura", k=>D.natura_etiquetas[k])}${opciones("categoria", c.dia.map(d=>d.categoria), "Todas las categorías")}`,
      `<p class="intro">Declaraciones e informes de impacto ambiental publicados en el BOE cuyo promotor es una sociedad probada de ${esc(c.nombre)}. La frase entre comillas es de la propia resolución. El condicionado completo está en el <a href="${"https://asensio94.github.io/observatorio-alegaciones/condicionado.html"}">observatorio</a>.</p>${barraNatura(c.resumen.natura)}<p></p>`);
  } else if (pestana === "indicios"){
    if (!c.indicios.length){ el.innerHTML = `<div class="vacio">El grafo de promotores no encuentra indicios de fraccionamiento con sociedades probadas de ${esc(c.nombre)}.</div>`; return; }
    el.innerHTML = `<p class="intro">Conjuntos de instalaciones que, por separado, quedan por debajo de 50 MW (competencia autonómica) y juntas lo superan, con las señales que da el <a href="https://asensio94.github.io/grafo-promotores/">grafo de promotores</a>. Un indicio no es una infracción: es un motivo para pedir que se evalúen juntas.</p>
    <div class="tabla"><table><thead><tr><th>Conjunto</th><th class="num">MW juntos</th><th>Señales</th><th>Periodo</th></tr></thead><tbody>${c.indicios.map(i => `<tr><td>${esc(i.instalaciones.slice(0,6).join(", "))}${i.instalaciones.length>6?` y ${i.instalaciones.length-6} más`:""}<br><span style="color:var(--gris);font-size:12.5px">${esc(i.provincias.join(", "))}${i.otras_cotizadas.length?` · con ${esc(i.otras_cotizadas.join(", "))}`:""}</span></td><td class="num">${fmt(i.suma_mw,1)}</td><td style="font-size:12.5px">${i.senales.map(esc).join("<br>")}</td><td class="mono" style="font-size:12px;white-space:nowrap">${fecha(i.desde)}<br>${fecha(i.hasta)}</td></tr>`).join("")}</tbody></table></div>`;
  } else if (pestana === "sociedades"){
    if (!c.sociedades.length){ el.innerHTML = `<div class="vacio">Todavía no hay ninguna sociedad del BOE o del BORME probada para ${esc(c.nombre)}.${filiales(c)}</div>`; return; }
    tablaFiltrable(c.sociedades,
      `<th>Sociedad</th><th>Prueba</th><th>Detalle</th>`,
      s => `<tr><td>${esc(s.nombre)}${s.nifs_en_grafo>1?`<br><span class="aviso-nif">El grafo reúne ${s.nifs_en_grafo} NIF bajo este nombre: sus instalaciones pueden ser de más de una sociedad</span>`:""}</td><td><span class="pill p-${s.estado}">${s.estado==="anexo"?"En su anexo":s.estado==="cadena"?"BORME hasta su anexo":"En conflicto"}</span></td><td style="font-size:12.5px"><a href="${esc(s.anexo.documento)}">${esc(s.anexo.titulo||"Anexo")}</a>, ${s.anexo.folio?`folio impreso <span class="mono">${esc(s.anexo.folio)}</span> (pág. <span class="mono">${esc(s.anexo.pagina)}</span> del XHTML)`:`pág. <span class="mono">${esc(s.anexo.pagina)}</span>`}<br><span class="mono" style="color:var(--gris);font-size:11.5px">${esc(s.anexo.fila)}</span>${s.borme.length?`<details class="cadena"><summary>${s.borme.length} inscripción${s.borme.length>1?"es":""} del BORME</summary><ol>${s.borme.map(e=>`<li>socio único: ${esc(e.nombre_madre||e.madre)} — <a href="${esc(e.url)}">BORME ${fecha(e.fecha)}</a></li>`).join("")}</ol></details>`:""}${s.otras.length?`<br><b>También lleva a:</b> ${esc(s.otras.map(o=>o.cotizada+" ("+o.via+")").join(", "))}`:""}</td></tr>`,
      `<input type="search" placeholder="Buscar sociedad…" aria-label="Buscar">${opciones("estado", c.sociedades.map(s=>s.estado), "Toda prueba", k=>({anexo:"En su anexo",cadena:"BORME hasta su anexo",conflicto:"En conflicto"}[k]))}`,
      `<p class="intro">Cada sociedad asignada a ${esc(c.nombre)} con el documento que lo prueba: la página del anexo de sus cuentas consolidadas y, si hace falta, las inscripciones del BORME que llevan hasta una sociedad de ese anexo.</p>`);
  } else {
    el.innerHTML = `<div class="pendiente">
      <div><h3>Litigios</h3><p>No hay una fuente abierta y estructurada de recursos contencioso-administrativos contra autorizaciones o DIA por promotor. El CENDOJ publica sentencias, no recursos en curso, y sin cruzar con el titular. Se deja vacío a propósito en lugar de rellenarlo con prensa.</p></div>
      <div><h3>Cumplimiento del condicionado</h3><p>Los informes de seguimiento que exigen las DIA (mortalidad de aves, medidas compensatorias) se entregan al órgano sustantivo y casi nunca se publican. Se pueden pedir con la Ley 27/2006: el <a href="https://asensio94.github.io/observatorio-alegaciones/condicionado.html">observatorio</a> genera la solicitud para cada resolución.</p></div>
      <div><h3>Proyectos autonómicos</h3><p>Las instalaciones de hasta 50 MW se tramitan en las comunidades autónomas y solo aparecen aquí si el BOE las recoge. Los boletines autonómicos están pendientes.</p></div>
    </div>`;
  }
}

fetch("datos/cartera.json").then(r => r.json()).then(d => {
  D = d;
  lista();
  const h = leerHash();
  elegir(h.c || (D.cotizadas.find(c => c.resumen.instalaciones) || D.cotizadas[0]).id, h.t);
  // each installation counted once, even when two listed companies share it (same rule as the header figures)
  const f = D.fuentes, mwById = new Map(D.cotizadas.flatMap(c => c.instalaciones.map(i => [i.id, i.mw||0])));
  const asig = [...mwById.values()].reduce((a,v)=>a+v,0);
  $("#pie").innerHTML = `Datos del ${fecha(D.generado)}. Grafo de promotores del ${fecha(f.grafo)} (${fmt(f.instalaciones_boe)} instalaciones, ${fmt(f.mw_boe)} MW en el BOE desde 2018) y condicionado del ${fecha((f.condicionado||"").slice(0,10))} (${fmt(f.resoluciones)} resoluciones). Las cotizadas de esta página suman ${fmt(asig)} MW probados; el resto son promotores no cotizados o sin prueba documental. Código y datos: <a href="https://github.com/Asensio94/cartera-cotizadas">github.com/Asensio94/cartera-cotizadas</a>.`;
}).catch(e => { $("#ficha").innerHTML = `<div class="ficha"><p>No se pudieron cargar los datos (${esc(e.message)}). Recarga la página.</p></div>`; });
addEventListener("hashchange", () => { const h = leerHash(); if (D && h.c && (!actual || h.c !== actual.id || h.t !== pestana)) elegir(h.c, h.t); });
</script>
</body>
</html>
"""


COMMON_CSS = Path(__file__).with_name("common.css")


def _fmt_es(n: float, decimals: int = 0) -> str:
    """Spanish number format: dot for thousands, comma for decimals."""
    s = f"{n:,.{decimals}f}"
    return s.replace(",", "\0").replace(".", ",").replace("\0", ".")


def _figures(datos: dict) -> str:
    """Header figures over all listed companies, counting each installation, resolution and company once."""
    mw_by_installation: dict[str, float] = {}
    resolutions, companies = set(), set()
    for c in datos["cotizadas"]:
        for i in c["instalaciones"]:
            mw_by_installation[i["id"]] = i.get("mw") or 0
        resolutions.update(d["id"] for d in c["dia"])
        companies.update(s["id"] for s in c["sociedades"])
    figures = [
        (_fmt_es(len(datos["cotizadas"])), "cotizadas"),
        (_fmt_es(sum(mw_by_installation.values())), "MW probados en el BOE"),
        (_fmt_es(len(mw_by_installation)), "instalaciones"),
        (_fmt_es(len(resolutions)), "resoluciones ambientales"),
        (_fmt_es(len(companies)), "sociedades probadas"),
    ]
    return "\n".join(f"    <div><b>{v}</b><span>{label}</span></div>" for v, label in figures)


def render(datos: dict) -> str:
    html = (PLANTILLA
            .replace("__LOGO__", LOGO_SVG)
            .replace("__FAVICON__", favicon_link("#0f6b6b", "#5cc4c4"))
            .replace("/*__COMMON_CSS__*/", COMMON_CSS.read_text(encoding="utf-8").strip())
            .replace("<!--__FIGURES__-->", _figures(datos)))
    left = [m for m in ("__COMMON_CSS__", "__FIGURES__") if m in html]
    if left:
        raise ValueError(f"unreplaced placeholders in the page: {left}")
    return html


def escribir(datos: dict) -> None:
    config.DOCS.mkdir(parents=True, exist_ok=True)
    (config.DOCS / "index.html").write_text(render(datos), encoding="utf-8")
    (config.DOCS / ".nojekyll").write_text("", encoding="utf-8")
