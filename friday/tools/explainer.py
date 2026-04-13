"""
explainer.py — ויזואליזציה אינטראקטיבית של אירועים היסטוריים בשוק
פותח HTML בדפדפן עם ציר זמן, TradingView ו-typewriter narrative
"""
import os
import json
import subprocess
import tempfile
from typing import Any


def register(mcp):
    @mcp.tool()
    async def open_event_explainer(
        title: str,
        events: list,
        narrative: str
    ) -> str:
        """פותח ויזואליזציה אינטראקטיבית של אירועים היסטוריים בשוק.
        title=כותרת הניתוח, events=רשימת אירועים עם year/name/symbol/change_pct/description/causes/duration_months/recovery_years,
        narrative=הטקסט שיוצג ב-typewriter effect"""

        if not events:
            return "No events provided."

        # תגובה מיידית — הסוכן יגיד זאת בזמן שה-HTML נבנה
        _ = f"Opening historical analysis for {title}, boss. Building the timeline now..."

        first = events[0]

        # ── Timeline items ──────────────────────────────────────────
        def dot_color(pct):
            p = abs(float(pct))
            if p >= 40:
                return "#ff4444"
            if p >= 20:
                return "#ff8c00"
            return "#ffd700"

        timeline_items = []
        for i, ev in enumerate(events):
            color = dot_color(ev.get("change_pct", 0))
            pct = ev.get("change_pct", 0)
            arrow = "▼" if float(pct) < 0 else "▲"
            active_class = " active" if i == 0 else ""
            timeline_items.append(f"""
        <div class="tl-item{active_class}" data-index="{i}" onclick="selectEvent({i})">
          <div class="tl-dot" style="background:{color};box-shadow:0 0 8px {color}88"></div>
          <div class="tl-body">
            <div class="tl-year" style="color:{color}">{ev.get('year', '')}</div>
            <div class="tl-name">{ev.get('name', '')}</div>
            <div class="tl-pct" style="color:{color}">{arrow} {abs(float(pct)):.0f}%</div>
          </div>
        </div>""")

        timeline_html = "\n".join(timeline_items)

        # ── Events JSON for JS ───────────────────────────────────────
        events_json = json.dumps(events, ensure_ascii=False)

        # ── First event detail ───────────────────────────────────────
        first_causes = first.get("causes", [])
        first_causes_html = "\n".join(
            f'<li class="cause-item">{c}</li>' for c in first_causes
        )
        first_color = dot_color(first.get("change_pct", 0))
        first_pct = first.get("change_pct", 0)
        first_arrow = "▼" if float(first_pct) < 0 else "▲"

        # ── Narrative words JSON ─────────────────────────────────────
        narrative_words = json.dumps(narrative.split(), ensure_ascii=False)

        # ── TradingView symbol ───────────────────────────────────────
        def tv_symbol(sym):
            mapping = {
                "^GSPC": "SP:SPX", "^IXIC": "NASDAQ:IXIC", "^DJI": "DJ:DJI",
                "GC=F": "COMEX:GC1!", "CL=F": "NYMEX:CL1!", "BTC-USD": "BITSTAMP:BTCUSD",
                "^VIX": "CBOE:VIX", "SI=F": "COMEX:SI1!", "TA125.TA": "TASE:TA125",
            }
            return mapping.get(sym, sym.replace("^", "").replace("=F", "1!"))

        first_tv = tv_symbol(first.get("symbol", "SP:SPX"))

        html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: #09090f;
    color: #d0d0e8;
    font-family: 'Segoe UI', Arial, sans-serif;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* ── Header ── */
  #header {{
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 52px;
    background: #0d0d18;
    border-bottom: 1px solid #1e1e32;
  }}
  .header-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: .5px;
  }}
  .header-badge {{
    font-size: 10px;
    letter-spacing: 2.5px;
    color: #00c8ff;
    text-transform: uppercase;
    background: #00c8ff18;
    border: 1px solid #00c8ff33;
    border-radius: 20px;
    padding: 3px 12px;
  }}

  /* ── Main layout ── */
  #main {{
    flex: 1;
    display: flex;
    overflow: hidden;
  }}

  /* ── Left: timeline ── */
  #timeline-panel {{
    width: 30%;
    flex-shrink: 0;
    background: #0d0d18;
    border-left: 1px solid #1e1e32;
    overflow-y: auto;
    padding: 20px 0;
  }}
  #timeline-panel::-webkit-scrollbar {{ width: 4px; }}
  #timeline-panel::-webkit-scrollbar-track {{ background: transparent; }}
  #timeline-panel::-webkit-scrollbar-thumb {{ background: #2a2a44; border-radius: 2px; }}

  .tl-heading {{
    font-size: 10px;
    letter-spacing: 2px;
    color: #444466;
    text-transform: uppercase;
    padding: 0 20px 14px;
  }}

  .tl-track {{
    position: relative;
    padding: 0 20px;
  }}
  .tl-track::before {{
    content: '';
    position: absolute;
    right: 34px;
    top: 0; bottom: 0;
    width: 1px;
    background: linear-gradient(to bottom, transparent, #2a2a44 10%, #2a2a44 90%, transparent);
  }}

  .tl-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    cursor: pointer;
    transition: background .2s;
    border-radius: 8px;
    padding: 10px 12px;
    position: relative;
  }}
  .tl-item:hover {{ background: #ffffff08; }}
  .tl-item.active {{ background: #00c8ff0d; }}
  .tl-item.highlight .tl-dot {{ transform: scale(1.5); }}

  .tl-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 4px;
    transition: transform .3s;
  }}
  .tl-body {{ flex: 1; min-width: 0; }}
  .tl-year {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; }}
  .tl-name {{ font-size: 0.85rem; color: #9999bb; margin: 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .tl-pct {{ font-size: 12px; font-weight: 700; }}

  /* ── Right panel ── */
  #right-panel {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  /* TradingView chart */
  #chart-panel {{
    height: 55%;
    flex-shrink: 0;
    border-bottom: 1px solid #1e1e32;
    position: relative;
  }}
  #tv-frame {{
    width: 100%;
    height: 100%;
    border: none;
    display: block;
  }}

  /* Detail panel */
  #detail-panel {{
    flex: 1;
    display: flex;
    gap: 0;
    overflow: hidden;
  }}

  #event-detail {{
    width: 42%;
    flex-shrink: 0;
    padding: 20px 22px;
    border-left: 1px solid #1e1e32;
    overflow-y: auto;
  }}
  #event-detail::-webkit-scrollbar {{ width: 4px; }}
  #event-detail::-webkit-scrollbar-thumb {{ background: #2a2a44; border-radius: 2px; }}

  .event-name-row {{
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 6px;
  }}
  .event-name {{ font-size: 1rem; font-weight: 700; color: #fff; }}
  .event-year-badge {{
    font-size: 11px;
    color: #666688;
    background: #1e1e30;
    border-radius: 4px;
    padding: 1px 7px;
  }}

  .pct-display {{
    font-size: 2.4rem;
    font-weight: 900;
    line-height: 1;
    margin: 8px 0 14px;
    font-variant-numeric: tabular-nums;
  }}

  .stat-row {{
    display: flex;
    gap: 16px;
    margin-bottom: 14px;
  }}
  .stat-box {{
    background: #131320;
    border: 1px solid #1e1e32;
    border-radius: 8px;
    padding: 8px 14px;
    flex: 1;
  }}
  .stat-label {{ font-size: 10px; color: #555577; letter-spacing: 1px; text-transform: uppercase; }}
  .stat-value {{ font-size: 1rem; font-weight: 700; color: #cccce0; margin-top: 2px; }}

  .causes-heading {{
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #444466;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .causes-list {{ list-style: none; display: flex; flex-direction: column; gap: 6px; }}
  .cause-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 0.85rem;
    color: #9999bb;
  }}
  .cause-item::before {{ content: '›'; color: #00c8ff; flex-shrink: 0; }}

  /* Narrative panel */
  #narrative-panel {{
    flex: 1;
    padding: 20px 22px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }}
  #narrative-panel::-webkit-scrollbar {{ width: 4px; }}
  #narrative-panel::-webkit-scrollbar-thumb {{ background: #2a2a44; border-radius: 2px; }}

  .narrative-heading {{
    font-size: 10px;
    letter-spacing: 2px;
    color: #00c8ff66;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .narrative-heading::before {{
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00c8ff;
    animation: blink 1.2s infinite;
  }}
  @keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.2; }} }}

  #live-text {{
    font-size: 0.95rem;
    color: #b0b0cc;
    line-height: 1.75;
    flex: 1;
  }}
  #live-text .word {{ opacity: 0; transition: opacity .15s; }}
  #live-text .word.shown {{ opacity: 1; }}
  #live-text .word.year-highlight {{
    color: #00c8ff;
    font-weight: 700;
  }}

  .cursor {{
    display: inline-block;
    width: 2px;
    height: 1em;
    background: #00c8ff;
    margin-right: 2px;
    animation: blink 0.8s infinite;
    vertical-align: text-bottom;
  }}
</style>
</head>
<body>

<div id="header">
  <div class="header-title">{title}</div>
  <div class="header-badge">FRIDAY LIVE ANALYSIS</div>
</div>

<div id="main">

  <!-- Timeline -->
  <div id="timeline-panel">
    <div class="tl-heading">ציר זמן אינטראקטיבי</div>
    <div class="tl-track">
{timeline_html}
    </div>
  </div>

  <!-- Right -->
  <div id="right-panel">

    <div id="chart-panel">
      <iframe id="tv-frame"
        src="https://www.tradingview.com/widgetembed/?symbol={first_tv}&interval=M&theme=dark&style=1&hide_top_toolbar=0&save_image=0&studies=RSI%40tv-basicstudies&withdateranges=1&hide_side_toolbar=0"
      ></iframe>
    </div>

    <div id="detail-panel">

      <div id="event-detail">
        <div class="event-name-row">
          <span class="event-name" id="ev-name">{first.get('name','')}</span>
          <span class="event-year-badge" id="ev-year">{first.get('year','')}</span>
        </div>
        <div class="pct-display" id="ev-pct" style="color:{first_color}">
          {first_arrow} {abs(float(first_pct)):.0f}%
        </div>
        <div class="stat-row">
          <div class="stat-box">
            <div class="stat-label">משך קריסה</div>
            <div class="stat-value" id="ev-dur">{first.get('duration_months','—')} חודשים</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">התאוששות</div>
            <div class="stat-value" id="ev-rec">{first.get('recovery_years','—')} שנים</div>
          </div>
        </div>
        <div class="causes-heading">גורמים עיקריים</div>
        <ul class="causes-list" id="ev-causes">
{first_causes_html}
        </ul>
      </div>

      <div id="narrative-panel">
        <div class="narrative-heading">ניתוח חי</div>
        <div id="live-text"><span class="cursor"></span></div>
      </div>

    </div>
  </div>
</div>

<script>
const EVENTS = {events_json};
const WORDS  = {narrative_words};
const TV_MAP = {{
  '^GSPC':'SP:SPX','^IXIC':'NASDAQ:IXIC','^DJI':'DJ:DJI',
  'GC=F':'COMEX:GC1!','CL=F':'NYMEX:CL1!','BTC-USD':'BITSTAMP:BTCUSD',
  '^VIX':'CBOE:VIX','SI=F':'COMEX:SI1!','TA125.TA':'TASE:TA125'
}};

function tvSymbol(s) {{
  return TV_MAP[s] || s.replace('^','').replace('=F','1!');
}}

function dotColor(pct) {{
  const p = Math.abs(parseFloat(pct));
  if (p >= 40) return '#ff4444';
  if (p >= 20) return '#ff8c00';
  return '#ffd700';
}}

let currentIdx = 0;

function selectEvent(idx) {{
  const ev = EVENTS[idx];
  if (!ev) return;
  currentIdx = idx;

  // highlight timeline
  document.querySelectorAll('.tl-item').forEach((el, i) => {{
    el.classList.toggle('active', i === idx);
  }});

  // update chart
  const sym = tvSymbol(ev.symbol || 'SP:SPX');
  document.getElementById('tv-frame').src =
    `https://www.tradingview.com/widgetembed/?symbol=${{sym}}&interval=M&theme=dark&style=1&hide_top_toolbar=0&save_image=0&studies=RSI%40tv-basicstudies&withdateranges=1&hide_side_toolbar=0`;

  // update detail
  const pct  = parseFloat(ev.change_pct || 0);
  const color = dotColor(pct);
  const arrow = pct < 0 ? '▼' : '▲';
  document.getElementById('ev-name').textContent = ev.name || '';
  document.getElementById('ev-year').textContent = ev.year || '';
  document.getElementById('ev-pct').style.color = color;
  document.getElementById('ev-pct').textContent  = arrow + ' ' + Math.abs(pct).toFixed(0) + '%';
  document.getElementById('ev-dur').textContent  = (ev.duration_months || '—') + ' חודשים';
  document.getElementById('ev-rec').textContent  = (ev.recovery_years  || '—') + ' שנים';

  const causesList = document.getElementById('ev-causes');
  causesList.innerHTML = (ev.causes || [])
    .map(c => `<li class="cause-item">${{c}}</li>`).join('');
}}

// ── Typewriter ──────────────────────────────────────────────────
function allYears() {{
  return EVENTS.map(e => String(e.year)).filter(Boolean);
}}

function buildText() {{
  const container = document.getElementById('live-text');
  container.innerHTML = '';

  const years = allYears();
  const yearSet = new Set(years);

  const cursor = document.createElement('span');
  cursor.className = 'cursor';

  WORDS.forEach((w, i) => {{
    const span = document.createElement('span');
    span.className = 'word';
    span.dataset.index = i;
    // check if word contains a year
    const bare = w.replace(/[^0-9]/g, '');
    if (yearSet.has(bare)) {{
      span.classList.add('year-highlight');
      span.dataset.year = bare;
    }}
    span.textContent = w + ' ';
    container.appendChild(span);
  }});
  container.appendChild(cursor);
}}

function runTypewriter() {{
  const spans = document.querySelectorAll('#live-text .word');
  const years = allYears();
  let i = 0;
  const cursor = document.querySelector('#live-text .cursor');

  function next() {{
    if (i >= spans.length) {{
      if (cursor) cursor.style.display = 'none';
      return;
    }}
    spans[i].classList.add('shown');

    // auto-highlight timeline when a year word appears
    const yr = spans[i].dataset.year;
    if (yr) {{
      const evIdx = EVENTS.findIndex(e => String(e.year) === yr);
      if (evIdx !== -1) {{
        document.querySelectorAll('.tl-item').forEach((el, j) => {{
          el.classList.toggle('highlight', j === evIdx);
        }});
        setTimeout(() => {{
          document.querySelectorAll('.tl-item')[evIdx]
            .scrollIntoView({{behavior:'smooth', block:'nearest'}});
        }}, 100);
      }}
    }}

    // scroll narrative
    spans[i].scrollIntoView({{behavior:'smooth', block:'nearest'}});
    i++;
    setTimeout(next, 80);
  }}
  setTimeout(next, 600);
}}

// ── Init ────────────────────────────────────────────────────────
buildText();
runTypewriter();
</script>
</body>
</html>"""

        # שמור לקובץ זמני ופתח
        tmp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".html",
            prefix="friday_explainer_",
            dir=os.path.abspath("data"),
            mode="w",
            encoding="utf-8"
        )
        tmp.write(html)
        tmp.close()

        subprocess.Popen(
            ['powershell', '-c', f'Start-Process "{tmp.name}"'],
            shell=True
        )

        return f"Opening historical analysis for '{title}', boss. {len(events)} events on the timeline, {len(narrative.split())} words in the narrative. It's live in your browser."
