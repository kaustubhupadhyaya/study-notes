"""Build the study pages from checked fragments.

    python -I build.py            # reads src/frag_*.html and src/qa_*.json -> pages/*.html

Theory pages and the hands-on lab page are separate files. If urls.json exists, it maps page keys
to published URLs so the set navigation links work across a hosted copy.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "src", ROOT / "pages"
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..700"
         "&family=JetBrains+Mono:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,650&display=swap")

PAGES = [
    # key, title, nav label, fragment/qa source, dek, kind
    ("dist", "Distributed Databases", "Distributed DBs", "A1",
     "How analytical databases spread data over many machines, how you host them on your own racks, and how shared-nothing differs from shared-data.", "theory"),
    ("mpp", "MPP Performance", "MPP performance", "A2",
     "Scaling compute and storage independently, and the factors that decide how fast a massively parallel query runs.", "theory"),
    ("obj", "Object Storage", "Object storage", "B1",
     "Object storage from first principles, the self-hosted options in 2026, and a data-lake setup that stays fast.", "theory"),
    ("enc", "Compression and Encryption", "Compression & encryption", "B2",
     "How columnar files are laid out, how they are encoded and compressed, and how data is encrypted at rest and in transit.", "theory"),
    ("ice", "Iceberg and Catalogs", "Iceberg & catalogs", "B3",
     "Apache Iceberg's metadata tree, commits and maintenance, and the catalogs that make tables shareable across engines.", "theory"),
    ("design", "Lakehouse Design", "Design & operate", "D",
     "The whiteboard design, sizing math, day-two operations, incident drills and a 60-second opener for every topic.", "theory"),
    ("qa", "Questions", "Questions", "QA",
     "The questions a senior interviewer is most likely to ask, each with a mid-level answer and what a senior adds.", "theory"),
    ("lab", "Lakehouse Lab", "Lab (optional)", "LAB",
     "A short optional hands-on run: object store, Iceberg catalog, a second engine and small files on one laptop.", "lab"),
]
GROUP_NAMES = {"A1": "Distributed DBs", "A2": "MPP performance", "B1": "Object storage",
               "B2": "Compression & encryption", "B3": "Iceberg & catalogs", "D": "Design & operate"}


def setnav(urls: dict, current: str) -> str:
    theory = [p for p in PAGES if p[5] == "theory"]
    lab = [p for p in PAGES if p[5] == "lab"]

    def item(p):
        key, _, label = p[0], p[1], p[2]
        if key == current:
            return f'<span class="cur" aria-current="page">{html.escape(label)}</span>'
        if urls.get(key):
            return f'<a href="{html.escape(urls[key])}">{html.escape(label)}</a>'
        return f'<span class="soon">{html.escape(label)}</span>'

    return ('<nav class="setnav" aria-label="Study set"><span class="lbl">Theory</span>'
            + "".join(item(p) for p in theory)
            + '<span class="lbl" style="margin-left:.6rem">Hands-on</span>' + "".join(item(p) for p in lab) + "</nav>")


TOC_JS = r"""
(function () {
  var main = document.querySelector('main'); var list = document.getElementById('toc-list');
  if (!main || !list) return;
  function slug(t) { return t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60); }
  var seen = {}; var links = [];
  main.querySelectorAll('section.topic > h2, section.topic h3').forEach(function (h) {
    var host = h.tagName === 'H2' ? h.parentElement : h;
    var id = host.id || slug(h.textContent); while (seen[id]) id += '-x'; seen[id] = 1; host.id = id;
    var li = document.createElement('li'); li.className = h.tagName.toLowerCase();
    var a = document.createElement('a'); a.href = '#' + id; a.textContent = h.textContent; li.appendChild(a); list.appendChild(li);
    links.push([host, a]);
  });
  var d = document.querySelector('.toc details');
  if (d && window.matchMedia('(min-width: 64rem)').matches) d.open = true;
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (p) { p[1].classList.toggle('on', p[0] === e.target); }); } });
    }, { rootMargin: '0px 0px -75% 0px' });
    links.forEach(function (p) { io.observe(p[0]); });
  }
})();
"""


def words(text: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", text).split())


def page(key: str, title: str, dek: str, eyebrow: str, meta: list[str], body: str, urls: dict,
         extra_css: str = "", extra_js: str = "", toc: bool = True) -> str:
    css = (ROOT / "theme.css").read_text(encoding="utf-8") + extra_css
    toc_html = ('<aside class="toc"><details><summary>On this page</summary><ol id="toc-list"></ol></details></aside>'
                if toc else "")
    layout_cls = "layout" if toc else "layout single"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
{css}
.setnav span.soon {{ padding: .2rem .55rem; border-radius: 999px; border: 1px dashed var(--line); color: var(--muted); white-space: nowrap; }}
.layout.single {{ grid-template-columns: minmax(0, 1fr); }}
</style>
</head>
<body>
<div class="wrap">
{setnav(urls, key)}
<header class="mast">
<p class="eyebrow">{html.escape(eyebrow)}</p>
<h1>{html.escape(title)}</h1>
<p class="dek">{html.escape(dek)}</p>
<p class="meta">{''.join(f'<span>{html.escape(m)}</span>' for m in meta)}</p>
</header>
<div class="{layout_cls}">
{toc_html}
<main>
{body}
</main>
</div>
<footer class="foot">Study notes · facts checked against primary sources in October 2026; version-sensitive facts are dated. Treat rules of thumb as rules of thumb.</footer>
{setnav(urls, key)}
</div>
<script>{TOC_JS if toc else ''}{extra_js}</script>
</body>
</html>
"""


def build_theory(p, urls) -> str:
    key, title, _, src, dek, _ = p
    frag = (SRC / f"frag_{src}.html").read_text(encoding="utf-8")
    mins = max(5, round(words(frag) / 220 / 5) * 5)
    n_inc = frag.count('class="box incident"')
    meta = [f"about {mins} min read", f"{n_inc} incident drills", "Theory"]
    return page(key, title, dek, "Study notes · theory", meta, frag, urls)


QA_CSS = """
.qa-bar { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--paper); padding-block: .7rem;
  border-bottom: 1px solid var(--line); display: grid; gap: .55rem; }
.qa-row { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; }
.qa-bar input[type=search] { flex: 1 1 14rem; min-width: 0; font: inherit; font-size: .95rem; padding: .45rem .7rem; border-radius: 6px;
  border: 1px solid var(--line); background: var(--surface); color: var(--ink); }
.chip { font-family: var(--font-display); font-size: .82rem; padding: .28rem .65rem; border-radius: 999px; border: 1px solid var(--line);
  background: var(--surface); color: var(--ink); cursor: pointer; }
.chip[aria-pressed=true] { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.qa-count { font-family: var(--font-mono); font-size: .78rem; color: var(--muted); margin-left: auto; }
.qa-list { display: grid; gap: 1rem; margin-top: 1.2rem; }
.qa { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 1rem 1.1rem; }
.qa h3 { font-size: 1.15rem; margin: .1rem 0 .55rem; }
.qa .tags { display: flex; flex-wrap: wrap; gap: .35rem; font-family: var(--font-mono); font-size: .72rem; color: var(--muted); }
.qa .tags span { border: 1px solid var(--line); border-radius: 3px; padding: .05rem .4rem; }
.qa .ans { margin: .7rem 0 0; padding: .7rem .9rem; border-radius: 6px; }
.qa .ans b.lbl { display: inline-block; font-family: var(--font-mono); font-size: .7rem; text-transform: uppercase; letter-spacing: .08em;
  padding: .1rem .45rem; border-radius: 3px; margin-bottom: .3rem; }
.qa .mid { background: var(--say-bg); } .qa .mid b.lbl { background: var(--say-fg); color: var(--say-bg); }
.qa .sen { background: var(--sen-bg); } .qa .sen b.lbl { background: var(--sen-fg); color: var(--sen-bg); }
.qa .ans p { margin: 0; max-width: none; }
.qa details { margin-top: .6rem; font-size: .95rem; }
.qa details summary { cursor: pointer; font-family: var(--font-display); font-size: .88rem; color: var(--accent); }
.qa details dl { margin: .5rem 0 0; } .qa details dt { font-weight: 650; margin-top: .4rem; } .qa details dd { margin: .1rem 0 0 0; }
.qa .bri { margin-top: .6rem; font-size: .92rem; color: var(--bri-fg); }
.qa .foot { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; margin-top: .8rem; }
.qa .reveal { font-family: var(--font-display); font-size: .82rem; padding: .3rem .7rem; border-radius: 6px; border: 1px solid var(--accent);
  background: none; color: var(--accent); cursor: pointer; }
.qa label.known { font-family: var(--font-display); font-size: .82rem; color: var(--muted); display: inline-flex; gap: .35rem; align-items: center; margin-left: auto; cursor: pointer; }
.qa.is-known { border-color: var(--bri-fg); }
.qa-empty { color: var(--muted); padding: 2rem 0; }
"""

QA_JS = r"""
(function () {
  var DATA = JSON.parse(document.getElementById('qa-data').textContent);
  var GROUPS = JSON.parse(document.getElementById('qa-groups').textContent);
  var store = { get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
                set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };
  var known = store.get('study-known', {});
  var state = { group: 'all', level: 'all', q: '', drill: false, unknown: false, order: null };
  var list = document.getElementById('qa-list'), count = document.getElementById('qa-count');
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function render() {
    var items = DATA.filter(function (d) {
      if (state.group !== 'all' && d.group !== state.group) return false;
      if (state.level !== 'all' && d.level !== state.level) return false;
      if (state.unknown && known[d.id]) return false;
      if (state.q) { var hay = (d.q + ' ' + d.mid + ' ' + d.senior + ' ' + d.topic).toLowerCase(); if (hay.indexOf(state.q) < 0) return false; }
      return true;
    });
    if (state.order) items.sort(function (a, b) { return state.order[a.id] - state.order[b.id]; });
    var nKnown = DATA.filter(function (d) { return known[d.id]; }).length;
    count.textContent = items.length + ' shown · ' + nKnown + ' / ' + DATA.length + ' known';
    if (!items.length) { list.innerHTML = '<p class="qa-empty">No questions match. Clear the search or pick another topic.</p>'; return; }
    list.innerHTML = items.map(function (d) {
      var fu = (d.followups || []).map(function (f) { return '<dt>' + esc(f.q) + '</dt><dd>' + esc(f.a) + '</dd>'; }).join('');
      var hide = state.drill ? ' hidden' : '';
      return '<article class="qa' + (known[d.id] ? ' is-known' : '') + '" data-id="' + esc(d.id) + '">' +
        '<div class="tags"><span>' + esc(GROUPS[d.group] || d.group) + '</span><span>' + esc(d.topic) + '</span><span>' + esc(d.level) + '</span><span>' + esc(d.id) + '</span></div>' +
        '<h3>' + esc(d.q) + '</h3>' +
        '<div class="ans mid"' + hide + '><b class="lbl">Mid-level answer</b><p>' + esc(d.mid) + '</p></div>' +
        '<div class="ans sen"' + hide + '><b class="lbl">What a senior adds</b><p>' + esc(d.senior) + '</p></div>' +
        (fu ? '<details' + hide + '><summary>Likely follow-ups</summary><dl>' + fu + '</dl></details>' : '') +
        
        '<div class="foot">' + (state.drill ? '<button class="reveal" type="button">Show answers</button>' : '') +
        '<label class="known"><input type="checkbox" id="known-' + esc(d.id) + '"' + (known[d.id] ? ' checked' : '') + '> I can say this</label></div>' +
        '</article>';
    }).join('');
  }
  list.addEventListener('click', function (e) {
    var b = e.target.closest('.reveal'); if (!b) return;
    var card = b.closest('.qa'); card.querySelectorAll('[hidden]').forEach(function (el) { el.hidden = false; }); b.remove();
  });
  list.addEventListener('change', function (e) {
    if (!e.target.matches('label.known input')) return;
    var id = e.target.closest('.qa').dataset.id; if (e.target.checked) known[id] = 1; else delete known[id];
    store.set('study-known', known); e.target.closest('.qa').classList.toggle('is-known', e.target.checked);
    var nKnown = DATA.filter(function (d) { return known[d.id]; }).length;
    count.textContent = count.textContent.replace(/\d+ \/ \d+ known/, nKnown + ' / ' + DATA.length + ' known');
  });
  function press(groupSel, btn) { document.querySelectorAll(groupSel).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); }); }
  document.querySelectorAll('[data-group]').forEach(function (b) { b.addEventListener('click', function () { state.group = b.dataset.group; press('[data-group]', b); render(); }); });
  document.querySelectorAll('[data-level]').forEach(function (b) { b.addEventListener('click', function () { state.level = b.dataset.level; press('[data-level]', b); render(); }); });
  document.getElementById('qa-search').addEventListener('input', function (e) { state.q = e.target.value.trim().toLowerCase(); render(); });
  var drill = document.getElementById('qa-drill'), unk = document.getElementById('qa-unknown');
  drill.addEventListener('click', function () { state.drill = !state.drill; drill.setAttribute('aria-pressed', String(state.drill)); render(); });
  unk.addEventListener('click', function () { state.unknown = !state.unknown; unk.setAttribute('aria-pressed', String(state.unknown)); render(); });
  document.getElementById('qa-shuffle').addEventListener('click', function () {
    var o = {}; DATA.forEach(function (d) { o[d.id] = Math.random(); }); state.order = o; render();
  });
  render();
})();
"""


def build_qa(urls) -> tuple[str, int]:
    data = []
    for g in GROUP_NAMES:
        f = SRC / f"qa_{g}.json"
        if not f.exists():
            continue
        for d in json.loads(f.read_text(encoding="utf-8")):
            d["group"] = g
            data.append(d)
    chips = "".join(f'<button class="chip" type="button" data-group="{g}" aria-pressed="false">{html.escape(n)}</button>'
                    for g, n in GROUP_NAMES.items())
    body = f"""
<section class="topic" id="how"><h2>How to use this page</h2>
<p class="lede">Read a question, say your answer out loud, then compare it with the mid-level answer and with what a senior adds. Tick the ones you can say cleanly. Drill mode hides the answers until you ask for them.</p>
<aside class="box senior"><b class="lbl">What separates the two answers</b><p>A mid-level answer is correct and complete. A senior answer adds the trade-off, a number, the failure mode and what it costs to operate. In the interview, give the mid-level answer first in one breath, then add one senior point. That shape sounds experienced without overclaiming.</p></aside>
</section>
<div class="qa-bar" role="region" aria-label="Filters">
<div class="qa-row"><input type="search" id="qa-search" placeholder="Search questions and answers" aria-label="Search questions and answers">
<button class="chip" type="button" id="qa-drill" aria-pressed="false">Drill mode</button>
<button class="chip" type="button" id="qa-unknown" aria-pressed="false">Not yet known</button>
<button class="chip" type="button" id="qa-shuffle">Shuffle</button></div>
<div class="qa-row"><button class="chip" type="button" data-group="all" aria-pressed="true">All topics</button>{chips}</div>
<div class="qa-row"><button class="chip" type="button" data-level="all" aria-pressed="true">All levels</button>
<button class="chip" type="button" data-level="core" aria-pressed="false">Core</button>
<button class="chip" type="button" data-level="deep" aria-pressed="false">Deep</button>
<span class="qa-count" id="qa-count" aria-live="polite"></span></div>
</div>
<div class="qa-list" id="qa-list"></div>
<script type="application/json" id="qa-data">{json.dumps(data, ensure_ascii=False).replace('</', '<\\/')}</script>
<script type="application/json" id="qa-groups">{json.dumps(GROUP_NAMES)}</script>
"""
    meta = [f"{len(data)} questions", "mid-level and senior answers", "Theory"]
    p = next(p for p in PAGES if p[0] == "qa")
    return page("qa", p[1], p[4], "Study notes · question drill", meta, body, urls,
                extra_css=QA_CSS, extra_js=QA_JS, toc=False), len(data)


def build_lab(urls) -> str:
    body = (SRC / "lab_body.html").read_text(encoding="utf-8")
    p = next(p for p in PAGES if p[0] == "lab")
    meta = ["10 min read · 30 s to run", "verified end to end in October 2026", "optional"]
    return page("lab", p[1], p[4], "Study notes · hands-on (separate from theory)", meta, body, urls)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    urls_file = ROOT / "urls.json"
    urls = json.loads(urls_file.read_text(encoding="utf-8")) if urls_file.exists() else {}
    only = set(sys.argv[1:])
    for p in PAGES:
        key = p[0]
        if only and key not in only:
            continue
        if p[3] == "QA":
            text, n = build_qa(urls)
            print(f"qa: {n} questions")
        elif p[3] == "LAB":
            if not (SRC / "lab_body.html").exists():
                continue
            text = build_lab(urls)
        else:
            if not (SRC / f"frag_{p[3]}.html").exists():
                print(f"skip {key}: no fragment yet")
                continue
            text = build_theory(p, urls)
        (OUT / f"{key}.html").write_text(text, encoding="utf-8")
        print(f"built pages/{key}.html ({len(text)//1024} KB)")


if __name__ == "__main__":
    main()
