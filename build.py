#!/usr/bin/env python3
"""
Generate docs/oekaki/index.html from decoded puzzle data.
Run from repo root: python3 docs/oekaki/build.py
"""
import json
import os

import importlib.util
_here = os.path.dirname(os.path.abspath(__file__))
_decoder_path = os.path.join(_here, 'oekaki-decode.py')
if not os.path.exists(_decoder_path):
    _decoder_path = os.path.join(_here, '..', '..', 'gaming', 'oekaki-decode.py')
_spec = importlib.util.spec_from_file_location('oekaki_decode', _decoder_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
decode_all = _mod.decode_all

ROM = '/tmp/oekaki.ws'
OUT = os.path.join(os.path.dirname(__file__), 'index.html')

DIFF_NAMES = ['入門', '初級', '中級', '上級', '超上級']
DIFF_EN    = ['Beginner', 'Easy', 'Normal', 'Hard', 'Expert']

def main():
    print(f'Decoding {ROM}...')
    puzzles = decode_all(ROM)

    # Slim payload: only what the page needs
    slim = []
    for p in puzzles:
        slim.append({
            'd': p['difficulty'],
            'n': p['local_num'],
            'r': p['rows'],
            'c': p['cols'],
            'rc': p['row_clues'],
            'cc': p['col_clues'],
            's': p['solution'],
        })

    payload = json.dumps(slim, separators=(',', ':'))
    print(f'Payload: {len(payload)//1024}KB')

    diff_counts = [sum(1 for p in slim if p['d'] == d) for d in range(5)]

    html = HTML_TEMPLATE.replace('__PAYLOAD__', payload)
    html = html.replace('__DIFF_NAMES__', json.dumps(DIFF_NAMES))
    html = html.replace('__DIFF_EN__', json.dumps(DIFF_EN))
    html = html.replace('__DIFF_COUNTS__', json.dumps(diff_counts))

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {OUT}')


HTML_TEMPLATE = r"""<!DOCTYPE html>
<!--
  ╔══════════════════════════════════════════════════════╗
  ║   あなたはソースを読んでいる。                       ║
  ║   You are reading the source. That tracks.           ║
  ╚══════════════════════════════════════════════════════╝

  Hidden puzzle — solve this 5x5 nonogram:

         2 4 4 4 2
         ---------
    1 1 |
      5 |
      5 |
      3 |
      1 |

  The solution is a shape that appears 372 times on this page.

  ---------------------------------------------------------
  ROM archaeology notes (WonderSwan V30MZ, SunSoft 2000):

    LUT:        file 0x20690  (372 x 4 bytes: size_cat u16le, sub_idx u16le)
    Decode:     file 0xA0000 + SI - 0x80000
    Grid loop:  60 outer x 4 inner; MOV AX,[SI]; XCHG AL,AH -> big-endian;
                extract 2-bit pairs MSB-first; cell > 1 = filled
    Difficulty: entries [0,89,179,249,300,372] in the LUT
    Grid dims:  size_cat -> rows x cols: 0=5x5, 1=10x10, 2=15x15, 3=15x20, 4=15x25

  If you can read this, you can reproduce every puzzle from the ROM.
  oekaki-decode.py in this repo will do it for you.
  ---------------------------------------------------------
-->
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>おーちゃんのおえかきロジック — Solutions</title>
<meta name="description" content="Solution viewer for all 372 nonogram puzzles in O-Chan no Oekaki Logic (おーちゃんのおえかきロジック), WonderSwan, SunSoft 2000. Ring reveal for stuck players — see the outer border before committing to the full solution.">
<meta property="og:title" content="おーちゃんのおえかきロジック — Puzzle Solutions">
<meta property="og:description" content="All 372 nonogram (picross) solutions for O-Chan no Oekaki Logic, WonderSwan, SunSoft 2000. Progressive ring reveal to help without fully spoiling.">
<meta property="og:type" content="website">
<meta name="keywords" content="oekaki logic, nonogram, picross, WonderSwan, SunSoft, O-Chan, solutions, walkthrough, おーちゃんのおえかきロジック">
<style>
:root {
  --bg: #1a1a2e;
  --surface: #16213e;
  --border: #0f3460;
  --accent: #e94560;
  --text: #e0e0e0;
  --dim: #888;
  --cell: 18px;
  --cell-hidden: #111;
  --filled: #e94560;
  --empty-revealed: #2a2a4a;
  --ring: #4a9eff;
  --ring-empty: #1e3a5a;
  --grid-line: rgba(255,255,255,0.018);
  --cell-border: #222;
  --filled-border: #c03040;
  --empty-border: #1a1a3a;
  --ring-border: #3080cc;
  --ring-e-border: #1a2a3a;
  --grid5: #4a4a6a;
}
[data-theme="light"] {
  --bg: #f5f0ff;
  --surface: #ffffff;
  --border: #00b8c8;
  --accent: #ff006e;
  --text: #1a1a2e;
  --dim: #5a5a7a;
  --cell-hidden: #ddd;
  --filled: #ff006e;
  --empty-revealed: #c8f5f5;
  --ring: #00b8c8;
  --ring-empty: #9aeaea;
  --grid-line: rgba(0,0,0,0.05);
  --cell-border: #bbb;
  --filled-border: #cc005a;
  --empty-border: #8ae8e8;
  --ring-border: #009090;
  --ring-e-border: #5ad0d0;
  --grid5: #9090b0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg); color: var(--text); font-family: 'Courier New', monospace;
  min-height: 100vh; width: 100%; overflow-x: hidden;
  display: flex; flex-direction: column; align-items: center; padding: 20px;
  background-image:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 20px 20px;
  transition: background-color 0.2s, color 0.2s;
}

/* pixel cat — bottom-right corner, faint */
body::after {
  content: '';
  display: block;
  position: fixed;
  bottom: 18px;
  right: 22px;
  width: 3px;
  height: 3px;
  color: rgba(233,69,96,0.15);
  box-shadow:
    6px 0px 0 0 currentColor,
    9px 0px 0 0 currentColor,
    15px 0px 0 0 currentColor,
    18px 0px 0 0 currentColor,
    3px 3px 0 0 currentColor,
    6px 3px 0 0 currentColor,
    9px 3px 0 0 currentColor,
    12px 3px 0 0 currentColor,
    15px 3px 0 0 currentColor,
    18px 3px 0 0 currentColor,
    0px 6px 0 0 currentColor,
    3px 6px 0 0 currentColor,
    6px 6px 0 0 currentColor,
    9px 6px 0 0 currentColor,
    12px 6px 0 0 currentColor,
    15px 6px 0 0 currentColor,
    18px 6px 0 0 currentColor,
    21px 6px 0 0 currentColor,
    0px 9px 0 0 currentColor,
    3px 9px 0 0 currentColor,
    9px 9px 0 0 currentColor,
    12px 9px 0 0 currentColor,
    18px 9px 0 0 currentColor,
    21px 9px 0 0 currentColor,
    0px 12px 0 0 currentColor,
    3px 12px 0 0 currentColor,
    6px 12px 0 0 currentColor,
    9px 12px 0 0 currentColor,
    12px 12px 0 0 currentColor,
    15px 12px 0 0 currentColor,
    18px 12px 0 0 currentColor,
    21px 12px 0 0 currentColor,
    3px 15px 0 0 currentColor,
    6px 15px 0 0 currentColor,
    9px 15px 0 0 currentColor,
    12px 15px 0 0 currentColor,
    15px 15px 0 0 currentColor,
    18px 15px 0 0 currentColor,
    6px 18px 0 0 currentColor,
    9px 18px 0 0 currentColor,
    12px 18px 0 0 currentColor,
    15px 18px 0 0 currentColor,
    9px 21px 0 0 currentColor,
    12px 21px 0 0 currentColor;
  pointer-events: none;
}

h1 { font-size: 1.1rem; color: var(--accent); letter-spacing: 2px; margin-bottom: 4px; text-align: center; }
.subtitle { color: var(--dim); font-size: 0.75rem; margin-bottom: 20px; }

.picker { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
select {
  background: var(--surface); color: var(--text); border: 1px solid var(--border);
  padding: 6px 10px; font-family: inherit; font-size: 0.85rem; cursor: pointer;
  transition: background 0.2s;
}
select:focus { outline: 1px solid var(--accent); }

.puzzle-area { display: flex; flex-direction: column; align-items: center; gap: 16px; width: 100%; }
.info { color: var(--dim); font-size: 0.75rem; }

.nonogram { display: grid; }
.col-clues-row { display: flex; }
.col-clue {
  width: var(--cell); display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end;
  font-size: 9px; color: var(--dim); padding-bottom: 2px; min-height: 60px;
}
.col-clue span { line-height: 11px; }
.clue-corner { min-height: 60px; }

.grid-row { display: flex; align-items: center; }
.row-clue {
  display: flex; gap: 2px; align-items: center; justify-content: flex-end;
  font-size: 9px; color: var(--dim); padding-right: 4px; min-width: 60px;
}
.row-clue span { white-space: nowrap; }

#grid-wrap { overflow-x: auto; width: fit-content; max-width: 100%; padding-bottom: 4px; }

.cell { width: var(--cell); height: var(--cell); border: 1px solid var(--cell-border); flex-shrink: 0; }
.cell.hidden { background: var(--cell-hidden); }
.cell.filled { background: var(--filled); border-color: var(--filled-border); }
.cell.empty  { background: var(--empty-revealed); border-color: var(--empty-border); }
.cell.ring-f { background: var(--ring); border-color: var(--ring-border); }
.cell.ring-e { background: var(--ring-empty); border-color: var(--ring-e-border); }
.cell.b5r { border-right: 2px solid var(--grid5); }
.cell.b5b { border-bottom: 2px solid var(--grid5); }

.controls { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
button {
  background: var(--surface); color: var(--text); border: 1px solid var(--border);
  padding: 8px 16px; font-family: inherit; font-size: 0.85rem; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
button:hover { background: var(--border); border-color: var(--accent); }
button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
#btn-theme { padding: 8px 10px; font-size: 1rem; border-color: var(--border); }

.legend { display: flex; gap: 16px; font-size: 0.7rem; color: var(--dim); flex-wrap: wrap; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-swatch { width: 12px; height: 12px; border: 1px solid var(--cell-border); }

footer { margin-top: 30px; color: var(--dim); font-size: 0.7rem; text-align: center; line-height: 1.8; }
footer a { color: var(--accent); text-decoration: none; }
footer a:hover { text-decoration: underline; }

@media (max-width: 500px) {
  :root { --cell: 13px; }
  .col-clue { font-size: 8px; }
  .row-clue { font-size: 8px; min-width: 40px; }
}
</style>
</head>
<body>
<h1>おーちゃんのおえかきロジック</h1>
<p class="subtitle">O-Chan no Oekaki Logic &mdash; WonderSwan &mdash; SunSoft 2000 &mdash; 372 puzzles</p>

<div class="picker">
  <select id="sel-diff"></select>
  <select id="sel-num"></select>
  <button id="btn-theme" onclick="toggleTheme()" title="Toggle light/dark">&#9680;</button>
</div>

<div class="puzzle-area">
  <div class="info" id="info"></div>
  <div id="grid-wrap"></div>
  <div class="controls">
    <button id="btn-ring" onclick="reveal('ring')">Show ring</button>
    <button id="btn-full" onclick="reveal('full')">Full solution</button>
    <button onclick="reveal('none')">Reset</button>
  </div>
  <div class="legend">
    <div class="legend-item"><div class="legend-swatch" style="background:var(--ring)"></div>Ring reveal (filled)</div>
    <div class="legend-item"><div class="legend-swatch" style="background:var(--ring-empty)"></div>Ring reveal (empty)</div>
    <div class="legend-item"><div class="legend-swatch" style="background:var(--filled)"></div>Full reveal (filled)</div>
    <div class="legend-item"><div class="legend-swatch" style="background:var(--empty-revealed)"></div>Full reveal (empty)</div>
  </div>
</div>

<footer>
  Decoded from ROM via MAME Lua scripting +
  <a href="https://www.capstone-engine.org" target="_blank" rel="noopener">Capstone</a> disassembly
  &mdash;
  <a href="https://github.com/frobknob/ochan-oekaki-no-netabare">source</a>
  &mdash;
  <a href="about.html">how this got made</a>
  <br>
  Viewer code: <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>.
  Puzzle content &copy; SunSoft 2000.
</footer>

<script>
const PUZZLES = __PAYLOAD__;
const DIFF_NAMES = __DIFF_NAMES__;
const DIFF_EN = __DIFF_EN__;
const DIFF_COUNTS = __DIFF_COUNTS__;

let state = { d: 0, n: 1, reveal: 'none' };

function toggleTheme() {
  const html = document.documentElement;
  const next = html.dataset.theme === 'light' ? 'dark' : 'light';
  html.dataset.theme = next === 'dark' ? '' : 'light';
  localStorage.setItem('oekaki-theme', next);
  document.getElementById('btn-theme').textContent = next === 'light' ? '◑' : '◐';
}

(function initTheme() {
  const saved = localStorage.getItem('oekaki-theme');
  if (saved === 'light') {
    document.documentElement.dataset.theme = 'light';
    document.getElementById('btn-theme').textContent = '◑';
  }
})();

function byDiff(d) { return PUZZLES.filter(p => p.d === d); }
function current() { return byDiff(state.d).find(p => p.n === state.n); }

function buildDiffSelect() {
  const sel = document.getElementById('sel-diff');
  DIFF_NAMES.forEach((jp, i) => {
    const o = document.createElement('option');
    o.value = i;
    o.textContent = `${jp} ${DIFF_EN[i]} (${DIFF_COUNTS[i]})`;
    sel.appendChild(o);
  });
  sel.value = 0;
  sel.onchange = () => {
    state.d = +sel.value;
    state.n = 1;
    state.reveal = 'none';
    buildNumSelect();
    draw();
  };
}

function buildNumSelect() {
  const sel = document.getElementById('sel-num');
  sel.innerHTML = '';
  const puz = byDiff(state.d);
  puz.forEach(p => {
    const o = document.createElement('option');
    o.value = p.n;
    o.textContent = `#${p.n}  (${p.r}\xd7${p.c})`;
    sel.appendChild(o);
  });
  sel.value = state.n;
  sel.onchange = () => {
    state.n = +sel.value;
    state.reveal = 'none';
    draw();
  };
}

function reveal(mode) {
  state.reveal = mode;
  draw();
}

function draw() {
  const p = current();
  if (!p) return;

  document.getElementById('info').textContent =
    `${DIFF_NAMES[state.d]} #${p.n}  —  ${p.r}\xd7${p.c} puzzle`;

  document.getElementById('btn-ring').className = state.reveal === 'ring' ? 'active' : '';
  document.getElementById('btn-full').className = state.reveal === 'full' ? 'active' : '';

  const R = p.r, C = p.c;
  const sol = p.s;

  function cellClass(r, c) {
    const filled = sol[r][c] === 'X';
    let base = 'cell';
    if ((c + 1) % 5 === 0 && c < C - 1) base += ' b5r';
    if ((r + 1) % 5 === 0 && r < R - 1) base += ' b5b';
    if (state.reveal === 'none') return base + ' hidden';
    if (state.reveal === 'ring') {
      const onRing = r === 0 || r === R-1 || c === 0 || c === C-1;
      if (!onRing) return base + ' hidden';
      return base + (filled ? ' ring-f' : ' ring-e');
    }
    return base + (filled ? ' filled' : ' empty');
  }

  const maxColDepth = Math.max(...p.cc.map(c => c.length));
  const maxRowWidth = Math.max(...p.rc.map(r => r.length));
  const rowClueW = maxRowWidth * 18 + 8;

  let html = '<div class="nonogram">';
  html += '<div class="col-clues-row">';
  html += `<div class="clue-corner" style="min-width:${rowClueW}px"></div>`;
  for (let c = 0; c < C; c++) {
    const nums = p.cc[c];
    const padded = Array(maxColDepth - nums.length).fill('').concat(nums);
    html += '<div class="col-clue">';
    padded.forEach(n => { html += `<span>${n === '' ? '&nbsp;' : n}</span>`; });
    html += '</div>';
  }
  html += '</div>';

  for (let r = 0; r < R; r++) {
    html += '<div class="grid-row">';
    html += `<div class="row-clue" style="min-width:${rowClueW}px">`;
    html += `<span>${p.rc[r].join(' ')}</span>`;
    html += '</div>';
    for (let c = 0; c < C; c++) {
      html += `<div class="${cellClass(r, c)}"></div>`;
    }
    html += '</div>';
  }

  html += '</div>';
  document.getElementById('grid-wrap').innerHTML = html;
}

buildDiffSelect();
buildNumSelect();
draw();

console.log('\n  372 puzzles. 0 hints.\n\n  (there is one more puzzle here — check the page source)\n');
</script>
</body>
</html>
"""

if __name__ == '__main__':
    main()
