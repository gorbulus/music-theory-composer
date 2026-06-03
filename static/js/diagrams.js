/* ── SVG diagram rendering ─────────────────────────────────── */

const SVG_NS = 'http://www.w3.org/2000/svg';

function svgEl(tag, attrs = {}) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

/* ── Guitar Chord Chart ─────────────────────────────────────── */
// frets: array[6] int — string order low-E(0) to high-e(5)
// -1=muted, 0=open, N=fret number
// barre: fret number or null
function renderChordChart(voicing) {
  const { frets, barre } = voicing;
  const W = 110, H = 130;
  const LEFT = 22, TOP = 28;
  const STRING_GAP = 14, FRET_GAP = 16;
  const STRINGS = 6, FRETS = 5;
  const svg = svgEl('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });

  const activeFrets = frets.filter(f => f > 0);
  const minFret = activeFrets.length ? Math.min(...activeFrets) : 1;
  const maxFret = activeFrets.length ? Math.max(...activeFrets) : FRETS;
  const displayMin = (minFret > 1) ? minFret : 1;
  const isOpen = minFret <= 1;

  // Nut or position marker
  if (isOpen) {
    svg.appendChild(svgEl('line', {
      x1: LEFT, y1: TOP, x2: LEFT + (STRINGS - 1) * STRING_GAP, y2: TOP,
      stroke: 'var(--text)', 'stroke-width': 3, class: 'chord-chart-nut'
    }));
  } else {
    const t = svgEl('text', {
      x: LEFT - 6, y: TOP + FRET_GAP / 2, class: 'chord-chart-fret-n',
      'text-anchor': 'end', 'dominant-baseline': 'central'
    });
    t.textContent = displayMin;
    svg.appendChild(t);
  }

  // Fret lines
  for (let f = 0; f <= FRETS; f++) {
    const y = TOP + f * FRET_GAP;
    svg.appendChild(svgEl('line', {
      x1: LEFT, y1: y, x2: LEFT + (STRINGS - 1) * STRING_GAP, y2: y,
      stroke: 'var(--border)', 'stroke-width': 1, class: 'chord-chart-fret'
    }));
  }

  // String lines
  for (let s = 0; s < STRINGS; s++) {
    const x = LEFT + s * STRING_GAP;
    svg.appendChild(svgEl('line', {
      x1: x, y1: TOP, x2: x, y2: TOP + FRETS * FRET_GAP,
      stroke: '#666', 'stroke-width': 1, class: 'chord-chart-string'
    }));
  }

  // Barre
  if (barre && barre > 0) {
    const barreY = TOP + (barre - displayMin + 0.5) * FRET_GAP;
    const r = svgEl('rect', {
      x: LEFT - 4, y: barreY - 6,
      width: (STRINGS - 1) * STRING_GAP + 8, height: 12,
      rx: 6, class: 'chord-chart-barre'
    });
    svg.appendChild(r);
  }

  // Open/muted/fret dots
  for (let s = 0; s < STRINGS; s++) {
    const f = frets[s];
    const x = LEFT + s * STRING_GAP;
    if (f === -1) {
      // Muted X
      const size = 5;
      svg.appendChild(svgEl('line', { x1: x - size, y1: TOP - 14, x2: x + size, y2: TOP - 4, stroke: 'var(--danger)', 'stroke-width': 1.5 }));
      svg.appendChild(svgEl('line', { x1: x + size, y1: TOP - 14, x2: x - size, y2: TOP - 4, stroke: 'var(--danger)', 'stroke-width': 1.5 }));
    } else if (f === 0) {
      // Open circle
      svg.appendChild(svgEl('circle', { cx: x, cy: TOP - 9, r: 4, fill: 'none', stroke: 'var(--text)', 'stroke-width': 1.5 }));
    } else {
      // Fret dot
      const dotY = TOP + (f - displayMin + 0.5) * FRET_GAP;
      const isRoot = (s === 0 && f === (barre || minFret)) || (s === 5 && f === (barre || minFret));
      svg.appendChild(svgEl('circle', {
        cx: x, cy: dotY, r: 6,
        fill: isRoot ? 'var(--root-clr)' : 'var(--accent)',
        class: isRoot ? 'chord-chart-root' : 'chord-chart-dot'
      }));
    }
  }

  // String name labels at bottom
  const stringNames = ['E', 'A', 'D', 'G', 'B', 'e'];
  for (let s = 0; s < STRINGS; s++) {
    const t = svgEl('text', {
      x: LEFT + s * STRING_GAP, y: TOP + FRETS * FRET_GAP + 11,
      class: 'chord-chart-label', 'text-anchor': 'middle'
    });
    t.textContent = stringNames[s];
    svg.appendChild(t);
  }

  return svg;
}


/* ── Fretboard / Tablature ──────────────────────────────────── */
// tabData: {fret_min, fret_max, notes: [{string, fret, note, is_root}]}
function renderFretboard(tabData) {
  const { fret_min, fret_max, notes } = tabData;
  const STRINGS = 6;
  const FRETS_SHOWN = Math.max(fret_max - fret_min + 2, 5);
  const LEFT = 30, TOP = 18, RIGHT_PAD = 20;
  const STRING_GAP = 18, FRET_GAP = 32;
  const W = LEFT + FRETS_SHOWN * FRET_GAP + RIGHT_PAD;
  const H = TOP + (STRINGS - 1) * STRING_GAP + 28;
  const svg = svgEl('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });

  // String lines
  const stringNames = ['e', 'B', 'G', 'D', 'A', 'E'];
  for (let s = 0; s < STRINGS; s++) {
    const y = TOP + s * STRING_GAP;
    svg.appendChild(svgEl('line', {
      x1: LEFT, y1: y, x2: LEFT + FRETS_SHOWN * FRET_GAP, y2: y,
      stroke: '#555', 'stroke-width': s === 5 ? 2 : 1
    }));
    const lbl = svgEl('text', { x: LEFT - 6, y: y, class: 'fretboard-string-n', 'text-anchor': 'end', 'dominant-baseline': 'central' });
    lbl.textContent = stringNames[s];
    svg.appendChild(lbl);
  }

  // Fret lines & numbers
  for (let f = 0; f <= FRETS_SHOWN; f++) {
    const x = LEFT + f * FRET_GAP;
    svg.appendChild(svgEl('line', {
      x1: x, y1: TOP, x2: x, y2: TOP + (STRINGS - 1) * STRING_GAP,
      stroke: '#444', 'stroke-width': f === 0 ? 2 : 1
    }));
    const fretNum = fret_min + f - 1;
    if (fretNum >= 0) {
      const fn = svgEl('text', {
        x: x + FRET_GAP / 2, y: TOP + (STRINGS - 1) * STRING_GAP + 13,
        class: 'fretboard-fret-n', 'text-anchor': 'middle'
      });
      fn.textContent = fretNum;
      svg.appendChild(fn);
    }
  }

  // Note dots
  // string 0 = high-e on display (top), string 5 = low-E (bottom)
  // data has string 0=low-E, so we invert: display_row = 5 - string
  for (const n of notes) {
    const displayRow = 5 - n.string;
    const y = TOP + displayRow * STRING_GAP;
    const x = LEFT + (n.fret - fret_min + 1) * FRET_GAP - FRET_GAP / 2;
    if (x < LEFT - 5) continue;
    svg.appendChild(svgEl('circle', {
      cx: x, cy: y, r: 8,
      fill: n.is_root ? 'var(--root-clr)' : 'var(--accent)'
    }));
    const lbl = svgEl('text', { x, y, class: 'fretboard-label' });
    lbl.textContent = n.note;
    svg.appendChild(lbl);
  }

  return svg;
}


/* ── Piano Keyboard ─────────────────────────────────────────── */
// data: {highlighted: [{pc, key_type, position, finger, is_root, note}], octaves}
function renderPiano(data) {
  const { highlighted = [], octaves = 2 } = data;
  const WW = 22, WH = 80;  // white key dimensions
  const BW = 14, BH = 50;  // black key dimensions
  const WHITES_PER_OCT = 7;
  const totalWhites = WHITES_PER_OCT * octaves;
  const W = totalWhites * WW + 2;
  const H = WH + 20;
  const svg = svgEl('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });

  // White key positions within octave (index 0-6 = C D E F G A B)
  // Black key offsets from left of their octave block
  const BLACK_X_OFFSETS = { 1: 0.6, 3: 1.6, 6: 3.6, 8: 4.6, 10: 5.6 }; // pc -> fractional white-key position

  const highlightMap = {};
  for (const h of highlighted) {
    highlightMap[`${h.pc}_${h.octave}`] = h;
  }
  // Flatten: use pc only for matching since our piano spans fixed octaves
  const hlByPC = {};
  for (const h of highlighted) hlByPC[h.pc] = h;

  const WHITE_PCS = [0, 2, 4, 5, 7, 9, 11];
  const BLACK_PCS = [1, 3, 6, 8, 10];

  // Draw white keys first
  for (let oct = 0; oct < octaves; oct++) {
    for (let wi = 0; wi < WHITES_PER_OCT; wi++) {
      const pc = WHITE_PCS[wi];
      const x = (oct * WHITES_PER_OCT + wi) * WW + 1;
      const hl = hlByPC[pc];
      let cls = 'piano-white';
      if (hl) cls = hl.is_root ? 'piano-hl-root-white' : 'piano-hl-white';
      svg.appendChild(svgEl('rect', { x, y: 1, width: WW - 1, height: WH - 2, rx: 2, class: cls }));
      if (hl) {
        const ft = svgEl('text', { x: x + WW / 2, y: WH - 12, class: 'piano-finger' });
        ft.textContent = hl.finger;
        svg.appendChild(ft);
        const nt = svgEl('text', { x: x + WW / 2, y: WH + 12, class: 'piano-note' });
        nt.textContent = hl.note;
        svg.appendChild(nt);
      }
    }
  }

  // Draw black keys on top
  for (let oct = 0; oct < octaves; oct++) {
    for (const pc of BLACK_PCS) {
      const xFrac = BLACK_X_OFFSETS[pc];
      const x = (oct * WHITES_PER_OCT + xFrac) * WW + 1 + (WW - BW) / 2;
      const hl = hlByPC[pc];
      let cls = 'piano-black';
      if (hl) cls = hl.is_root ? 'piano-hl-root-black' : 'piano-hl-black';
      svg.appendChild(svgEl('rect', { x, y: 1, width: BW, height: BH, rx: 2, class: cls }));
      if (hl) {
        const ft = svgEl('text', { x: x + BW / 2, y: BH - 6, class: 'piano-finger', fill: '#eee' });
        ft.textContent = hl.finger;
        svg.appendChild(ft);
      }
    }
  }

  return svg;
}
