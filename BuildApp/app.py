#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silence.eco — Dealer Finder
Lance un serveur local et ouvre l'interface dans le navigateur.
Aucune installation requise — uniquement Python standard.
"""

import sys, os, json, re, time, threading, webbrowser, urllib.request
import urllib.parse, http.server, socketserver, html as html_mod
from datetime import datetime

PORT = 8742

# ─────────────────────────────────────────────────────────────────────────────
# HTML / CSS / JS de l'application (tout en un seul fichier)
# ─────────────────────────────────────────────────────────────────────────────
APP_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Silence.eco — Dealer Finder</title>
<style>
:root{
  --red:#D01A20;--red-d:#A01015;--red-lt:#FAE8E8;
  --dark:#1C1C1E;--dg:#2C2C2E;--gray:#F2F2F2;
  --border:#E0E0E0;--white:#fff;--muted:#8A8A8E;--text:#1C1C1E;
}
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#f5f5f5;min-height:100vh;display:flex;flex-direction:column}

/* HEADER */
.hdr{background:var(--dark);padding:12px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.logo{display:flex;align-items:center;gap:10px}
.logo-mark{width:34px;height:34px;background:var(--red);border-radius:8px;display:flex;align-items:center;justify-content:center}
.logo-mark svg{width:20px;height:20px}
.brand{display:flex;flex-direction:column}
.brand-name{font-size:15px;font-weight:700;letter-spacing:2px;color:#fff;text-transform:uppercase}
.brand-sub{font-size:8px;color:var(--red);letter-spacing:3px;font-weight:600}
.hdr-right{display:flex;align-items:center;gap:12px}
.status-dot{width:8px;height:8px;border-radius:50%;background:#444}
.status-dot.ok{background:#22c55e}
.status-dot.running{background:var(--red);animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
#status-txt{font-size:12px;color:#888}
.lang-btns{display:flex;gap:4px}
.lang-btn{background:var(--dg);color:#ccc;border:none;border-radius:5px;padding:4px 10px;font-size:11px;font-weight:600;cursor:pointer;transition:.15s}
.lang-btn.active,.lang-btn:hover{background:var(--red);color:#fff}

/* TABS */
.tabs{background:#fff;border-bottom:1px solid var(--border);display:flex;padding:0 24px;position:sticky;top:58px;z-index:99}
.tab{padding:12px 18px;font-size:13px;font-weight:500;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;transition:.15s;white-space:nowrap}
.tab.active{color:var(--red);border-bottom-color:var(--red)}
.tab:hover:not(.active){color:var(--text)}
.tab-badge{background:var(--red);color:#fff;font-size:10px;padding:2px 6px;border-radius:10px;margin-left:5px}

/* PANELS */
.panel{display:none;padding:24px;max-width:1100px;margin:0 auto;width:100%}
.panel.active{display:block}

/* CARDS */
.card{background:#fff;border-radius:12px;border:1px solid var(--border);padding:20px 24px;margin-bottom:16px}
.field-label{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.url-row{display:flex;gap:10px}
.url-input{flex:1;padding:11px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:13px;color:var(--text);outline:none;transition:.15s}
.url-input:focus{border-color:var(--red)}
.btn-red{background:var(--red);color:#fff;border:none;border-radius:8px;padding:11px 22px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;transition:.15s;display:flex;align-items:center;gap:7px}
.btn-red:hover{background:var(--red-d)}
.btn-red:disabled{background:#ccc;cursor:not-allowed}
.btn-out{background:#fff;color:var(--text);border:1.5px solid var(--border);border-radius:8px;padding:10px 16px;font-size:13px;font-weight:500;cursor:pointer;transition:.15s}
.btn-out:hover{background:var(--gray)}

/* OPTIONS */
.opts{display:flex;gap:20px;flex-wrap:wrap;margin-top:12px}
.opt{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--text);cursor:pointer}
.opt input{accent-color:var(--red);width:15px;height:15px}

/* BANNER */
.banner{background:var(--red-lt);border-left:3px solid var(--red);border-radius:0 8px 8px 0;padding:11px 16px;font-size:12px;color:#7a0a0a;line-height:1.6;margin-bottom:16px}

/* PROGRESS */
.prog-card{background:#fff;border-radius:12px;border:1px solid var(--border);padding:18px 24px;margin-bottom:16px;display:none}
.prog-card.show{display:block}
.prog-top{display:flex;justify-content:space-between;margin-bottom:8px}
.prog-label{font-size:13px;font-weight:600;color:var(--text)}
.prog-pct{font-size:13px;font-weight:600;color:var(--red)}
.prog-track{height:6px;background:var(--border);border-radius:10px;overflow:hidden;margin-bottom:10px}
.prog-fill{height:100%;background:var(--red);border-radius:10px;width:0%;transition:width .4s ease}
.prog-log{font-size:11px;color:var(--muted);font-family:monospace;max-height:80px;overflow-y:auto;display:flex;flex-direction:column;gap:2px;background:var(--gray);border-radius:6px;padding:8px 10px}

/* STATS */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
.stat{background:var(--gray);border-radius:10px;padding:14px 16px}
.stat-lbl{font-size:11px;color:var(--muted);margin-bottom:4px}
.stat-val{font-size:26px;font-weight:600;color:var(--text)}
.stat-val.red{color:var(--red)}

/* TABLE */
.tbl-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px}
.tbl-meta{font-size:13px;color:var(--muted)}
.tbl-actions{display:flex;gap:8px}
.tbl-wrap{overflow-x:auto;border-radius:10px;border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:700px}
thead{background:var(--gray)}
th{padding:10px 13px;text-align:left;font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid var(--border);white-space:nowrap}
td{padding:9px 13px;border-bottom:.5px solid var(--border);color:var(--text);vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--red-lt)}
.badge{display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:600;padding:3px 8px;border-radius:20px;white-space:nowrap}
.b-page{background:#E8F0FE;color:#1a56c4}
.b-web{background:#FFF3E0;color:#b45309}
.b-miss{background:#FEE2E2;color:#991b1b}
.dot{width:5px;height:5px;border-radius:50%;background:currentColor;flex-shrink:0}
.email-val{color:#A01015;font-weight:600}
.no-val{color:#ccc;font-style:italic}
tr.miss td{background:#FFF5F5}

/* EMPTY */
.empty{text-align:center;padding:60px 20px;color:var(--muted)}
.empty-icon{font-size:40px;margin-bottom:12px}
.empty-title{font-size:16px;font-weight:600;color:var(--text);margin-bottom:6px}
.empty-sub{font-size:13px}

/* SETTINGS */
.set-card{background:#fff;border-radius:12px;border:1px solid var(--border);padding:20px 24px;margin-bottom:16px}
.set-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.set-desc{font-size:12px;color:var(--muted);margin-bottom:10px}
.set-textarea{width:100%;padding:10px 12px;border:1.5px solid var(--border);border-radius:8px;font-family:monospace;font-size:12px;resize:vertical;outline:none;color:var(--text)}
.set-textarea:focus{border-color:var(--red)}
.tog-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:.5px solid var(--border)}
.tog-row:last-child{border-bottom:none}
.tog-lbl{font-size:13px;color:var(--text)}
.toggle{position:relative;width:38px;height:21px;flex-shrink:0}
.toggle input{opacity:0;width:0;height:0}
.tog-sl{position:absolute;inset:0;background:#ddd;border-radius:21px;cursor:pointer;transition:.2s}
.tog-sl:before{content:'';position:absolute;width:17px;height:17px;left:2px;bottom:2px;background:#fff;border-radius:50%;transition:.2s}
.toggle input:checked+.tog-sl{background:var(--red)}
.toggle input:checked+.tog-sl:before{transform:translateX(17px)}

/* SPINNER */
.spin{width:15px;height:15px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* NOTIFICATION */
.notif{position:fixed;bottom:24px;right:24px;background:var(--dark);color:#fff;padding:12px 20px;border-radius:10px;font-size:13px;font-weight:500;transform:translateY(80px);opacity:0;transition:.3s;z-index:999;max-width:320px}
.notif.show{transform:translateY(0);opacity:1}
.notif.ok{border-left:3px solid #22c55e}
.notif.err{border-left:3px solid var(--red)}

@media(max-width:600px){.stats{grid-template-columns:1fr 1fr}.hdr{padding:10px 14px}.panel{padding:14px}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="logo">
    <div class="logo-mark">
      <svg viewBox="0 0 20 20" fill="none" stroke="white" stroke-width="1.5">
        <polygon points="10,2 17,6 17,14 10,18 3,14 3,6"/>
        <circle cx="10" cy="10" r="3" fill="white" stroke="none"/>
      </svg>
    </div>
    <div class="brand">
      <div class="brand-name">Silence</div>
      <div class="brand-sub">ECO · DEALER FINDER</div>
    </div>
  </div>
  <div class="hdr-right">
    <div class="status-dot" id="sdot"></div>
    <span id="status-txt" data-key="ready"></span>
    <div class="lang-btns">
      <button class="lang-btn active" onclick="setLang('FR')">FR</button>
      <button class="lang-btn" onclick="setLang('ES')">ES</button>
      <button class="lang-btn" onclick="setLang('EN')">EN</button>
    </div>
  </div>
</div>

<!-- TABS -->
<div class="tabs">
  <div class="tab active" onclick="goTab('extract')" data-key="tab_extract"></div>
  <div class="tab" onclick="goTab('results')" id="tab-results" data-key="tab_results"></div>
  <div class="tab" onclick="goTab('settings')" data-key="tab_settings"></div>
</div>

<!-- ═══ PANEL: EXTRACTION ═══ -->
<div class="panel active" id="panel-extract">
  <div class="card">
    <div class="field-label" data-key="lbl_url"></div>
    <div class="url-row">
      <input class="url-input" id="url-input" type="url"
        value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france"/>
      <button class="btn-red" id="btn-go" onclick="startExtraction()">
        <span id="btn-txt" data-key="btn_extract"></span>
      </button>
    </div>
    <div class="opts">
      <label class="opt"><input type="checkbox" id="opt-web" checked><span data-key="opt_web"></span></label>
      <label class="opt"><input type="checkbox" id="opt-dedup" checked><span data-key="opt_dedup"></span></label>
      <label class="opt"><input type="checkbox" id="opt-excl" checked><span data-key="opt_excl"></span></label>
    </div>
  </div>

  <div class="banner" data-key="info_banner"></div>

  <div class="prog-card" id="prog-card">
    <div class="prog-top">
      <span class="prog-label" id="prog-label"></span>
      <span class="prog-pct" id="prog-pct">0%</span>
    </div>
    <div class="prog-track"><div class="prog-fill" id="prog-fill"></div></div>
    <div class="prog-log" id="prog-log"></div>
  </div>

  <div class="stats" id="stats" style="display:none">
    <div class="stat"><div class="stat-lbl" data-key="stat_total"></div><div class="stat-val" id="s-total">0</div></div>
    <div class="stat"><div class="stat-lbl" data-key="stat_emails"></div><div class="stat-val red" id="s-emails">0</div></div>
    <div class="stat"><div class="stat-lbl" data-key="stat_web"></div><div class="stat-val" id="s-web">0</div></div>
    <div class="stat"><div class="stat-lbl" data-key="stat_addr"></div><div class="stat-val" id="s-addr">0</div></div>
  </div>
</div>

<!-- ═══ PANEL: RESULTS ═══ -->
<div class="panel" id="panel-results">
  <div class="tbl-bar">
    <div class="tbl-meta" id="tbl-meta"></div>
    <div class="tbl-actions">
      <button class="btn-out" onclick="copyEmails()" data-key="btn_copy"></button>
      <button class="btn-red" onclick="exportCSV()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <span data-key="btn_csv"></span>
      </button>
    </div>
  </div>
  <div id="empty-state" class="empty">
    <div class="empty-icon">📋</div>
    <div class="empty-title" data-key="empty_title"></div>
    <div class="empty-sub" data-key="empty_sub"></div>
  </div>
  <div class="tbl-wrap" id="tbl-wrap" style="display:none">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th data-key="col_name"></th>
          <th data-key="col_addr"></th>
          <th data-key="col_phone"></th>
          <th data-key="col_email"></th>
          <th data-key="col_src"></th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>

<!-- ═══ PANEL: SETTINGS ═══ -->
<div class="panel" id="panel-settings">
  <div class="set-card">
    <div class="set-title" data-key="set_excl_title"></div>
    <div class="set-desc" data-key="set_excl_desc"></div>
    <textarea class="set-textarea" id="excl-domains" rows="8">silence.eco
aixam.com
microcar.fr
ligier.fr
chatenet.com
casalini.it
bellier.fr</textarea>
  </div>
  <div class="set-card">
    <div class="set-title" data-key="set_search_title"></div>
    <div style="padding:4px 0">
      <div class="tog-row"><span class="tog-lbl" data-key="tog_web"></span><label class="toggle"><input type="checkbox" checked id="tog-web"><span class="tog-sl"></span></label></div>
      <div class="tog-row"><span class="tog-lbl" data-key="tog_maps"></span><label class="toggle"><input type="checkbox" checked id="tog-maps"><span class="tog-sl"></span></label></div>
      <div class="tog-row"><span class="tog-lbl" data-key="tog_miss"></span><label class="toggle"><input type="checkbox" checked id="tog-miss"><span class="tog-sl"></span></label></div>
    </div>
  </div>
  <button class="btn-red" onclick="saveSettings()"><span data-key="btn_save"></span></button>
  <div class="banner" style="margin-top:16px" data-key="info_portable"></div>
</div>

<!-- NOTIFICATION -->
<div class="notif" id="notif"></div>

<script>
// ── i18n ─────────────────────────────────────────────────────────────────────
const LANGS = {
FR:{
  ready:"Prêt",running:"En cours…",done:"Terminé",
  tab_extract:"Extraction",tab_results:"Résultats",tab_settings:"Paramètres",
  lbl_url:"URL DE LA PAGE RÉSEAU CONCESSIONNAIRES",
  btn_extract:"Extraire",btn_running:"En cours…",btn_rerun:"Relancer",
  opt_web:"Recherche web pour emails manquants",
  opt_dedup:"Dédupliquer",opt_excl:"Exclure emails constructeur",
  info_banner:"ℹ  L'outil analyse la page, extrait nom · adresse · téléphone · email pour chaque concessionnaire, puis complète les données manquantes via une recherche web ciblée. Les emails du constructeur sont automatiquement exclus.",
  stat_total:"Concessionnaires",stat_emails:"Emails trouvés",
  stat_web:"Via recherche web",stat_addr:"Adresses",
  col_name:"Nom du concessionnaire",col_addr:"Adresse",
  col_phone:"Téléphone",col_email:"Email",col_src:"Source",
  src_page:"Page directe",src_web:"Recherche web",src_miss:"Non trouvé",
  btn_copy:"Copier les emails",btn_csv:"Exporter CSV",
  empty_title:"Aucun résultat",empty_sub:"Lancez une extraction pour voir les concessionnaires ici.",
  tbl_meta:" concessionnaires · "," emails · "," adresses",
  set_excl_title:"Domaines constructeurs à exclure",
  set_excl_desc:"Un domaine par ligne. Ces emails seront ignorés.",
  set_search_title:"Options de recherche",
  tog_web:"Recherche web automatique",tog_maps:"Inclure Google Maps",tog_miss:"Inclure lignes sans email dans le CSV",
  btn_save:"Enregistrer les paramètres",
  info_portable:"◆  Application locale — aucune donnée envoyée à l'extérieur. Le fichier CSV est téléchargé dans votre dossier Téléchargements.",
  copied:" emails copiés !",no_copy:"Aucun email à copier.",
  saved:"Paramètres enregistrés !",
  last_run:"Dernier run : ",
  prog_load:"Chargement de la page…",prog_parse:"Analyse des blocs…",
  prog_emails:"Extraction des emails…",prog_web:"Recherche web ({i}/{n})…",
  prog_dedup:"Déduplication…",prog_done:"Extraction terminée !",
},
ES:{
  ready:"Listo",running:"En proceso…",done:"Completado",
  tab_extract:"Extracción",tab_results:"Resultados",tab_settings:"Ajustes",
  lbl_url:"URL DE LA PÁGINA RED DE CONCESIONARIOS",
  btn_extract:"Extraer",btn_running:"En proceso…",btn_rerun:"Reiniciar",
  opt_web:"Búsqueda web para emails faltantes",
  opt_dedup:"Eliminar duplicados",opt_excl:"Excluir emails del fabricante",
  info_banner:"ℹ  La herramienta analiza la página, extrae nombre · dirección · teléfono · email de cada concesionario, y completa los datos faltantes mediante búsqueda web.",
  stat_total:"Concesionarios",stat_emails:"Emails encontrados",
  stat_web:"Vía búsqueda web",stat_addr:"Direcciones",
  col_name:"Nombre del concesionario",col_addr:"Dirección",
  col_phone:"Teléfono",col_email:"Email",col_src:"Fuente",
  src_page:"Página directa",src_web:"Búsqueda web",src_miss:"No encontrado",
  btn_copy:"Copiar emails",btn_csv:"Exportar CSV",
  empty_title:"Sin resultados",empty_sub:"Lance una extracción para ver los concesionarios aquí.",
  tbl_meta:" concesionarios · "," emails · "," direcciones",
  set_excl_title:"Dominios del fabricante a excluir",
  set_excl_desc:"Un dominio por línea. Estos emails serán ignorados.",
  set_search_title:"Opciones de búsqueda",
  tog_web:"Búsqueda web automática",tog_maps:"Incluir Google Maps",tog_miss:"Incluir filas sin email en el CSV",
  btn_save:"Guardar ajustes",
  info_portable:"◆  Aplicación local — ningún dato enviado al exterior. El archivo CSV se descarga en su carpeta Descargas.",
  copied:" emails copiados !",no_copy:"No hay emails para copiar.",
  saved:"¡Ajustes guardados!",
  last_run:"Última extracción: ",
  prog_load:"Cargando página…",prog_parse:"Analizando bloques…",
  prog_emails:"Extrayendo emails…",prog_web:"Búsqueda web ({i}/{n})…",
  prog_dedup:"Eliminando duplicados…",prog_done:"¡Extracción completada!",
},
EN:{
  ready:"Ready",running:"Running…",done:"Done",
  tab_extract:"Extraction",tab_results:"Results",tab_settings:"Settings",
  lbl_url:"DEALER NETWORK PAGE URL",
  btn_extract:"Extract",btn_running:"Running…",btn_rerun:"Run Again",
  opt_web:"Web search for missing emails",
  opt_dedup:"Deduplicate results",opt_excl:"Exclude manufacturer emails",
  info_banner:"ℹ  The tool scans the page, extracts name · address · phone · email for each dealer, then fills missing data via targeted web searches. Manufacturer emails are automatically excluded.",
  stat_total:"Dealers",stat_emails:"Emails found",
  stat_web:"Via web search",stat_addr:"Addresses",
  col_name:"Dealer name",col_addr:"Address",
  col_phone:"Phone",col_email:"Email",col_src:"Source",
  src_page:"Direct page",src_web:"Web search",src_miss:"Not found",
  btn_copy:"Copy emails",btn_csv:"Export CSV",
  empty_title:"No results yet",empty_sub:"Run an extraction to see dealers here.",
  tbl_meta:" dealers · "," emails · "," addresses",
  set_excl_title:"Manufacturer domains to exclude",
  set_excl_desc:"One domain per line. These emails will be ignored.",
  set_search_title:"Search options",
  tog_web:"Automatic web search",tog_maps:"Include Google Maps",tog_miss:"Include rows without email in CSV",
  btn_save:"Save settings",
  info_portable:"◆  Local app — no data sent externally. The CSV file is downloaded to your Downloads folder.",
  copied:" emails copied!",no_copy:"No emails to copy.",
  saved:"Settings saved!",
  last_run:"Last run: ",
  prog_load:"Loading page…",prog_parse:"Parsing blocks…",
  prog_emails:"Extracting emails…",prog_web:"Web search ({i}/{n})…",
  prog_dedup:"Deduplicating…",prog_done:"Extraction complete!",
},
};

let LANG = 'FR';
let T = LANGS.FR;
let results = [];

function setLang(l){
  LANG = l; T = LANGS[l];
  document.querySelectorAll('.lang-btn').forEach(b=>{b.classList.toggle('active',b.textContent===l)});
  document.querySelectorAll('[data-key]').forEach(el=>{
    const k = el.getAttribute('data-key');
    if(T[k]!==undefined) el.textContent = T[k];
  });
  renderResults();
}

// ── TABS ─────────────────────────────────────────────────────────────────────
function goTab(name){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  const tabs=['extract','results','settings'];
  document.querySelectorAll('.tab')[tabs.indexOf(name)].classList.add('active');
}

// ── PROGRESS ─────────────────────────────────────────────────────────────────
function setProgress(pct, label){
  document.getElementById('prog-fill').style.width = pct+'%';
  document.getElementById('prog-pct').textContent = pct+'%';
  if(label) document.getElementById('prog-label').textContent = label;
}
function addLog(msg){
  const el = document.getElementById('prog-log');
  const d = document.createElement('div');
  d.textContent = '▸ ' + msg;
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
}
function notify(msg, type='ok'){
  const n = document.getElementById('notif');
  n.textContent = msg;
  n.className = 'notif show ' + type;
  setTimeout(()=>n.classList.remove('show'), 3000);
}

// ── EXTRACTION ────────────────────────────────────────────────────────────────
let running = false;

async function startExtraction(){
  if(running) return;
  const url = document.getElementById('url-input').value.trim();
  if(!url.startsWith('http')){ notify('URL invalide','err'); return; }

  running = true;
  results = [];
  document.getElementById('btn-go').disabled = true;
  document.getElementById('btn-txt').innerHTML = '<div class="spin"></div>';
  document.getElementById('prog-card').classList.add('show');
  document.getElementById('prog-log').innerHTML = '';
  document.getElementById('stats').style.display = 'none';
  document.getElementById('sdot').className = 'status-dot running';
  document.getElementById('status-txt').textContent = T.running;

  const optWeb   = document.getElementById('opt-web').checked;
  const optDedup = document.getElementById('opt-dedup').checked;
  const optExcl  = document.getElementById('opt-excl').checked;
  const exclDoms = document.getElementById('excl-domains').value
    .split('\n').map(s=>s.trim()).filter(Boolean);

  try {
    setProgress(5, T.prog_load);
    addLog('URL : ' + url);

    const resp = await fetch('/api/extract', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({url, optWeb, optDedup, optExcl, exclDoms})
    });

    if(!resp.ok) throw new Error('Server error '+resp.status);

    // Stream progress via SSE-like polling
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while(true){
      const {done, value} = await reader.read();
      if(done) break;
      buffer += decoder.decode(value, {stream:true});
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for(const line of lines){
        if(!line.trim()) continue;
        try{
          const msg = JSON.parse(line);
          if(msg.type==='progress'){
            setProgress(msg.pct, msg.label);
            if(msg.log) addLog(msg.log);
          } else if(msg.type==='done'){
            results = msg.dealers;
            finishExtraction();
          } else if(msg.type==='error'){
            throw new Error(msg.message);
          }
        } catch(e){ /* partial JSON */ }
      }
    }
  } catch(e){
    notify('Erreur: '+e.message, 'err');
    addLog('ERREUR: '+e.message);
    document.getElementById('btn-go').disabled = false;
    document.getElementById('btn-txt').textContent = T.btn_extract;
    document.getElementById('sdot').className = 'status-dot';
    document.getElementById('status-txt').textContent = T.ready;
    running = false;
  }
}

function finishExtraction(){
  running = false;
  const em = results.filter(r=>r.email).length;
  const wb = results.filter(r=>r.src==='web').length;
  const ad = results.filter(r=>r.addr).length;

  document.getElementById('s-total').textContent = results.length;
  document.getElementById('s-emails').textContent = em;
  document.getElementById('s-web').textContent = wb;
  document.getElementById('s-addr').textContent = ad;
  document.getElementById('stats').style.display = 'grid';
  document.getElementById('btn-go').disabled = false;
  document.getElementById('btn-txt').textContent = T.btn_rerun;
  document.getElementById('sdot').className = 'status-dot ok';
  document.getElementById('status-txt').textContent = T.last_run + new Date().toLocaleTimeString();

  const badge = results.length ? '<span class="tab-badge">'+results.length+'</span>' : '';
  document.getElementById('tab-results').innerHTML = T.tab_results + badge;

  renderResults();
  goTab('results');
}

function renderResults(){
  const empty = document.getElementById('empty-state');
  const wrap  = document.getElementById('tbl-wrap');
  if(!results.length){ empty.style.display='block'; wrap.style.display='none'; return; }
  empty.style.display = 'none';
  wrap.style.display = 'block';

  const em = results.filter(r=>r.email).length;
  const ad = results.filter(r=>r.addr).length;
  document.getElementById('tbl-meta').textContent =
    results.length + (T.tbl_meta[0]||' · ') + em + (T.tbl_meta[1]||' · ') + ad + (T.tbl_meta[2]||'');

  const srcMap = {page: T.src_page||'Page', web: T.src_web||'Web', pending: T.src_miss||'—'};
  document.getElementById('tbody').innerHTML = results.map((r,i)=>{
    const src = r.src==='page'
      ? '<span class="badge b-page"><span class="dot"></span>'+srcMap.page+'</span>'
      : r.src==='web'
      ? '<span class="badge b-web"><span class="dot"></span>'+srcMap.web+'</span>'
      : '<span class="badge b-miss"><span class="dot"></span>'+srcMap.pending+'</span>';
    const em2 = r.email
      ? '<span class="email-val">'+r.email+'</span>'
      : '<span class="no-val">—</span>';
    const rowClass = !r.email ? ' class="miss"' : '';
    return `<tr${rowClass}>
      <td style="color:var(--muted);font-size:11px">${i+1}</td>
      <td style="font-weight:600">${esc(r.name)}</td>
      <td style="font-size:12px;color:var(--muted)">${esc(r.addr||'—')}</td>
      <td>${esc(r.phone||'—')}</td>
      <td>${em2}</td>
      <td>${src}</td>
    </tr>`;
  }).join('');
}

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function copyEmails(){
  const list = results.filter(r=>r.email).map(r=>r.email).join('\n');
  if(!list){ notify(T.no_copy,'err'); return; }
  navigator.clipboard.writeText(list).then(()=>{
    notify(results.filter(r=>r.email).length + T.copied);
  });
}

function exportCSV(){
  if(!results.length){ notify(T.no_copy,'err'); return; }
  const incMiss = document.getElementById('tog-miss').checked;
  const rows = results.filter(r=> incMiss || r.email);
  const srcMap = {page:T.src_page||'Page',web:T.src_web||'Web',pending:T.src_miss||''};
  const header = [T.col_name,T.col_addr,T.col_phone,T.col_email,T.col_src,'Date'];
  const date = new Date().toLocaleDateString();
  const csv = '\uFEFF' + [header, ...rows.map(r=>[
    r.name, r.addr||'', r.phone||'', r.email||'',
    srcMap[r.src]||r.src, date
  ])].map(row=>row.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\r\n');

  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = 'silence_dealers_'+new Date().toISOString().slice(0,10)+'.csv';
  a.click();
  notify('CSV exporté — '+rows.length+' lignes');
}

function saveSettings(){ notify(T.saved); }

// Init
setLang('FR');
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# Scraping logic (server-side)
# ─────────────────────────────────────────────────────────────────────────────
HEADERS_REQ = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
ADDR_RE  = re.compile(
    r"\d{1,4}[\s,]+[^\d\n]{5,60}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,40}", re.I)

def fetch(url, timeout=14):
    req = urllib.request.Request(url, headers=HEADERS_REQ)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        enc = r.headers.get_content_charset("utf-8") or "utf-8"
        return raw.decode(enc, errors="replace")

def clean_emails(text, excl):
    out = set()
    for m in EMAIL_RE.finditer(text):
        e = m.group(0).lower().strip(".")
        dom = e.split("@")[-1]
        if not any(x in dom for x in excl):
            out.add(e)
    return out

def clean_phones(text):
    seen, out = set(), []
    for m in PHONE_RE.finditer(text):
        p = re.sub(r"[\s.\-]", "", m.group(0))
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def strip_tags(html_text):
    return re.sub(r"<[^>]+>", " ", html_text)

def web_search_email(name, excl):
    try:
        q = urllib.parse.quote(f'"{name}" email contact')
        url = f"https://html.duckduckgo.com/html/?q={q}"
        html_text = fetch(url, timeout=10)
        emails = clean_emails(html_text, excl)
        if emails:
            return sorted(emails)[0]
    except Exception:
        pass
    return ""

def parse_page(html_text, excl, send):
    # Try to find dealer blocks using common patterns
    send(12, "Recherche des blocs concessionnaires…", "Analyse HTML")

    # Try BS4 if available
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, "html.parser")
        for t in soup(["script","style","nav","footer","head"]):
            t.decompose()

        candidates = []
        for sel in ["[class*='dealer']","[class*='concess']","[class*='revendeur']",
                    "[class*='network']","[class*='reseau']","[class*='store']",
                    "[class*='location']","article",".card",".item"]:
            found = soup.select(sel)
            if len(found) >= 3:
                candidates = found
                send(20, f"Sélecteur '{sel}' trouvé", f"{len(found)} blocs")
                break

        if not candidates:
            candidates = [d for d in soup.find_all(["div","li","article"])
                          if PHONE_RE.search(d.get_text())]
            send(20, "Fallback téléphone", f"{len(candidates)} blocs")

        seen, dealers = set(), []
        for blk in candidates[:100]:
            txt = blk.get_text(separator=" ", strip=True)
            if len(txt) < 15: continue
            name = ""
            for t in blk.find_all(["h2","h3","h4","h5","strong","b"]):
                v = t.get_text(strip=True)
                if 4 < len(v) < 80: name = v; break
            if not name:
                name = " ".join(txt.split()[:5])
            key = name.lower()[:30]
            if key in seen or len(name) < 4: continue
            seen.add(key)
            am = ADDR_RE.search(txt)
            addr = am.group(0).strip() if am else ""
            phones = clean_phones(txt)
            phone = phones[0] if phones else ""
            emails = clean_emails(txt, excl)
            for a in blk.find_all("a", href=True):
                h = a["href"]
                if h.startswith("mailto:"):
                    e = h[7:].split("?")[0].strip().lower()
                    dom = e.split("@")[-1]
                    if e and not any(x in dom for x in excl):
                        emails.add(e)
            email = sorted(emails)[0] if emails else ""
            dealers.append({"name":name[:80],"addr":addr[:100],
                            "phone":phone,"email":email,
                            "src":"page" if email else "pending"})
        return dealers

    except ImportError:
        pass

    # Regex fallback
    send(20, "Mode regex (bs4 non installé)", "")
    clean = re.sub(r"\s+", " ", strip_tags(html_text))
    emails = sorted(clean_emails(clean, excl))
    phones = clean_phones(clean)
    used, dealers = set(), []
    for ph in phones[:60]:
        idx = clean.find(re.sub(r"[\s.\-]","",ph)[:6])
        if idx < 0: continue
        ctx = clean[max(0,idx-150):idx+150]
        em_l = [e for e in clean_emails(ctx,excl) if e not in used]
        em = em_l[0] if em_l else ""
        if em: used.add(em)
        nm = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿa-zà-ÿ\-]+){1,4})", ctx)
        name = nm.group(1) if nm else f"Dealer {len(dealers)+1}"
        dealers.append({"name":name[:80],"addr":"","phone":ph,
                        "email":em,"src":"page" if em else "pending"})
    for e in emails:
        if e not in used:
            dealers.append({"name":e.split("@")[0].replace("."," ").title(),
                            "addr":"","phone":"","email":e,"src":"page"})
    return dealers

def run_extraction(data, send):
    url      = data.get("url","")
    opt_web  = data.get("optWeb", True)
    opt_ded  = data.get("optDedup", True)
    opt_excl = data.get("optExcl", True)
    excl     = data.get("exclDoms", []) if opt_excl else []

    send(5, "Chargement de la page…", f"GET {url}")
    try:
        html_text = fetch(url)
    except Exception as e:
        send(0, "", "", error=str(e))
        return

    send(15, "Page chargée", f"{len(html_text)//1024} Ko reçus")
    dealers = parse_page(html_text, excl, send)
    send(45, f"{len(dealers)} concessionnaires détectés", "")

    if opt_web:
        pending = [d for d in dealers if not d["email"]]
        send(50, f"Recherche web — {len(pending)} emails manquants", "")
        for i, d in enumerate(pending):
            pct = 50 + int(38 * i / max(len(pending), 1))
            send(pct, f"Recherche web ({i+1}/{len(pending)})", f"→ {d['name'][:40]}")
            em = web_search_email(d["name"], excl)
            if em:
                d["email"] = em
                d["src"] = "web"
            time.sleep(1.0)

    if opt_ded:
        send(92, "Déduplication…", "")
        seen, uniq = set(), []
        for d in dealers:
            k = d["name"].lower()[:30]
            if k not in seen:
                seen.add(k); uniq.append(d)
        dealers = uniq

    send(100, "Extraction terminée !", "", dealers=dealers)

# ─────────────────────────────────────────────────────────────────────────────
# HTTP Server
# ─────────────────────────────────────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence server logs

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(APP_HTML.encode("utf-8"))

    def do_POST(self):
        if self.path != "/api/extract":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        def send(pct, label, log_msg, error=None, dealers=None):
            if error:
                msg = json.dumps({"type":"error","message":error}) + "\n"
            elif dealers is not None:
                msg = json.dumps({"type":"done","dealers":dealers}) + "\n"
            else:
                msg = json.dumps({"type":"progress","pct":pct,
                                  "label":label,"log":log_msg}) + "\n"
            try:
                chunk = msg.encode("utf-8")
                size = f"{len(chunk):X}\r\n".encode()
                self.wfile.write(size + chunk + b"\r\n")
                self.wfile.flush()
            except Exception:
                pass

        run_extraction(data, send)
        try:
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except Exception:
            pass

def start_server():
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()

def main():
    # Start server in background thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(0.8)

    # Open browser
    url = f"http://127.0.0.1:{PORT}"
    print(f"\n  Silence Dealer Finder")
    print(f"  Ouvert sur : {url}")
    print(f"  Fermez cette fenetre pour quitter.\n")
    webbrowser.open(url)

    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Fermeture...")

if __name__ == "__main__":
    main()
