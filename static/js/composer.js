/* ── State ──────────────────────────────────────────────────── */
let state = { root: 'C', quality: 'major', genre_slug: '', view: 'guitar', data: null };
let genreIdMap = {};  // slug -> id (populated from select options)

/* ── Init ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Build genre id map from select
  document.querySelectorAll('#genre-select option').forEach(opt => {
    if (opt.value) genreIdMap[opt.value] = opt.dataset.id || opt.value;
  });

  document.getElementById('load-btn').addEventListener('click', loadTheory);
  document.getElementById('save-btn').addEventListener('click', saveCombo);

  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.view = btn.dataset.view;
      if (state.data) renderAll(state.data);
    });
  });

  // Auto-load if ?load=<id>
  const params = new URLSearchParams(location.search);
  if (params.get('load')) loadSaved(parseInt(params.get('load')));
});

/* ── Load theory data ───────────────────────────────────────── */
function loadTheory() {
  state.root = document.getElementById('root-select').value;
  state.quality = document.getElementById('quality-select').value;
  state.genre_slug = document.getElementById('genre-select').value;

  setStatus('Loading…', true);
  const url = `${THEORY_URL}?root=${encodeURIComponent(state.root)}&quality=${encodeURIComponent(state.quality)}&genre_slug=${encodeURIComponent(state.genre_slug)}`;
  fetch(url)
    .then(r => r.json())
    .then(data => {
      state.data = data;
      renderAll(data);
      const label = data.genre ? `${data.root} ${data.quality_display} / ${data.genre.name}` : `${data.root} ${data.quality_display}`;
      setStatus(label);
    })
    .catch(() => setStatus('Error loading theory data.'));
}

function setStatus(msg, loading = false) {
  const el = document.getElementById('status-bar');
  el.textContent = msg;
  el.classList.toggle('loading', loading);
}

/* ── Render all panels ──────────────────────────────────────── */
function renderAll(data) {
  renderProgressions(data);
  renderChords(data);
  renderScales(data);
  renderArpeggios(data);
  renderImprov(data);
}

/* ── Progressions ───────────────────────────────────────────── */
function renderProgressions(data) {
  const panel = document.getElementById('progressions-panel');
  if (!data.progressions || !data.progressions.length) {
    panel.innerHTML = '<p class="empty-state">Select a genre to see progressions.</p>';
    return;
  }
  panel.innerHTML = '';
  for (const prog of data.progressions) {
    const block = document.createElement('div');
    block.className = 'progression-block';
    block.innerHTML = `<div class="progression-name">${prog.name}</div>`;
    const row = document.createElement('div');
    row.className = 'progression-chords';
    for (const ch of prog.chords) {
      const card = document.createElement('div');
      card.className = 'prog-chord';
      card.innerHTML = `
        <div class="prog-degree">${ch.degree_name}</div>
        <div class="prog-symbol">${ch.symbol}</div>
        <div class="prog-notes">${ch.notes.join(' ')}</div>`;
      row.appendChild(card);
    }
    block.appendChild(row);
    panel.appendChild(block);
  }
}

/* ── Chords ─────────────────────────────────────────────────── */
function renderChords(data) {
  const panel = document.getElementById('chords-panel');
  panel.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'chords-grid';

  for (const ch of data.chords) {
    const card = document.createElement('div');
    card.className = 'chord-card';
    card.innerHTML = `
      <div class="chord-card-header">
        <span class="chord-symbol">${ch.symbol}</span>
        <span class="chord-degree">Degree ${ch.degree}</span>
      </div>
      <div class="chord-notes">${ch.notes.join(' – ')}</div>`;

    // Diagram area
    const diagWrap = document.createElement('div');
    diagWrap.className = 'diagram-wrap';
    card.appendChild(diagWrap);

    // Voicing navigator
    const voicings = ch.voicings || [];
    const piano = ch.piano || null;
    let voicingIdx = 0;
    const nav = document.createElement('div');
    nav.className = 'voicing-nav';
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '◀';
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '▶';
    const lbl = document.createElement('span');
    lbl.className = 'voicing-label';
    nav.appendChild(prevBtn);
    nav.appendChild(lbl);
    nav.appendChild(nextBtn);
    card.appendChild(nav);

    function drawVoicing() {
      diagWrap.innerHTML = '';
      if (state.view === 'guitar') {
        if (voicings.length) {
          const v = voicings[voicingIdx];
          lbl.textContent = `${v.label} (${voicingIdx + 1}/${voicings.length})`;
          diagWrap.appendChild(renderChordChart(v));
        } else {
          lbl.textContent = 'No voicing';
          diagWrap.innerHTML = '<span style="color:var(--text-dim);font-size:11px">No voicing data</span>';
        }
      } else {
        // Piano view
        lbl.textContent = piano ? ch.symbol : 'No piano data';
        if (piano) diagWrap.appendChild(renderPiano(piano));
      }
    }

    prevBtn.addEventListener('click', () => {
      voicingIdx = (voicingIdx - 1 + Math.max(voicings.length, 1)) % Math.max(voicings.length, 1);
      drawVoicing();
    });
    nextBtn.addEventListener('click', () => {
      voicingIdx = (voicingIdx + 1) % Math.max(voicings.length, 1);
      drawVoicing();
    });

    drawVoicing();
    grid.appendChild(card);
  }
  panel.appendChild(grid);
}

/* ── Scales & Modes ─────────────────────────────────────────── */
function renderScales(data) {
  const panel = document.getElementById('scales-panel');
  panel.innerHTML = '';

  for (const scale of (data.scales || [])) {
    const block = document.createElement('div');
    block.className = 'scale-block';
    block.innerHTML = `<div class="scale-title">${scale.display}</div>`;

    // Note pills
    const noteRow = document.createElement('div');
    noteRow.className = 'scale-notes-row';
    for (const n of scale.notes) {
      const pill = document.createElement('span');
      pill.className = 'scale-note' + (n === data.root ? ' is-root' : '');
      pill.textContent = n;
      noteRow.appendChild(pill);
    }
    block.appendChild(noteRow);

    // Tab positions (guitar) or piano
    const diagArea = document.createElement('div');
    diagArea.className = 'diagram-wrap';
    block.appendChild(diagArea);

    if (state.view === 'guitar') {
      // Position buttons
      const tabs = (data.scale_tabs || []).filter(t => t.scale === scale.name || scale.name === data.quality);
      if (tabs.length) {
        const posRow = document.createElement('div');
        posRow.className = 'position-tabs';
        let activePos = 0;
        tabs.forEach((tab, i) => {
          const pb = document.createElement('button');
          pb.className = 'pos-btn' + (i === 0 ? ' active' : '');
          pb.textContent = `Pos ${tab.position}`;
          pb.addEventListener('click', () => {
            posRow.querySelectorAll('.pos-btn').forEach(b => b.classList.remove('active'));
            pb.classList.add('active');
            activePos = i;
            diagArea.innerHTML = '';
            diagArea.appendChild(renderFretboard(tabs[i]));
          });
          posRow.appendChild(pb);
        });
        block.insertBefore(posRow, diagArea);
        diagArea.appendChild(renderFretboard(tabs[0]));
      }
    } else {
      // Piano
      if (data.scale_piano) {
        diagArea.appendChild(renderPiano(data.scale_piano));
      }
    }

    panel.appendChild(block);
  }
}

/* ── Arpeggios ──────────────────────────────────────────────── */
function renderArpeggios(data) {
  const panel = document.getElementById('arpeggios-panel');
  panel.innerHTML = '';
  for (const arp of (data.arpeggios || [])) {
    const block = document.createElement('div');
    block.className = 'arpeggio-block';
    block.innerHTML = `<div class="arpeggio-title">${arp.symbol}</div>`;
    const noteRow = document.createElement('div');
    noteRow.className = 'arpeggio-notes';
    for (const n of arp.notes) {
      const pill = document.createElement('span');
      pill.className = 'arp-note' + (n.octave === 0 && n.semitone === 0 ? ' is-root' : '');
      pill.textContent = n.note;
      noteRow.appendChild(pill);
    }
    block.appendChild(noteRow);
    if (state.view === 'guitar' && arp.tab) {
      const wrap = document.createElement('div');
      wrap.className = 'diagram-wrap';
      wrap.appendChild(renderFretboard(arp.tab));
      block.appendChild(wrap);
    }
    panel.appendChild(block);
  }
  if (!data.arpeggios || !data.arpeggios.length) {
    panel.innerHTML = '<p class="empty-state">No arpeggio data.</p>';
  }
}

/* ── Improv Maps ────────────────────────────────────────────── */
function renderImprov(data) {
  const panel = document.getElementById('improv-panel');
  panel.innerHTML = '';
  for (const map of (data.improv_maps || [])) {
    const block = document.createElement('div');
    block.className = 'improv-block';
    block.innerHTML = `
      <div class="improv-title">${map.scale_display} — target vs passing tones</div>
      <div class="improv-legend">
        <span><span class="legend-dot" style="background:var(--target-clr)"></span>Chord tone (target)</span>
        <span><span class="legend-dot" style="background:var(--surface2)"></span>Passing tone</span>
      </div>`;
    const noteRow = document.createElement('div');
    noteRow.className = 'improv-notes';
    noteRow.style.marginTop = '10px';
    for (const n of map.notes) {
      const pill = document.createElement('span');
      pill.className = `improv-note ${n.role}`;
      pill.textContent = n.note;
      noteRow.appendChild(pill);
    }
    block.appendChild(noteRow);
    panel.appendChild(block);
  }
  if (!data.improv_maps || !data.improv_maps.length) {
    panel.innerHTML = '<p class="empty-state">No improv data.</p>';
  }
}

/* ── Tab switching ──────────────────────────────────────────── */
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === `tab-${name}`));
}

/* ── Save combination ───────────────────────────────────────── */
function saveCombo() {
  const name = document.getElementById('combo-name').value.trim();
  if (!name) { alert('Enter a name for this combination.'); return; }
  if (!state.data) { alert('Load a combination first.'); return; }

  // Find genre id from slug
  const genreSelect = document.getElementById('genre-select');
  const genreOpt = genreSelect.options[genreSelect.selectedIndex];
  const genreId = genreOpt.dataset.id || genreOpt.value;

  fetch(SAVE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
    body: JSON.stringify({ name, root: state.root, quality: state.quality, genre_id: genreId }),
  })
  .then(r => r.json())
  .then(d => {
    setStatus(`Saved: ${d.name}`);
    document.getElementById('combo-name').value = '';
  })
  .catch(() => setStatus('Error saving.'));
}

/* ── Load saved combination ─────────────────────────────────── */
function loadSaved(id) {
  fetch(`/api/load/${id}/`)
    .then(r => r.json())
    .then(d => {
      document.getElementById('root-select').value = d.root;
      document.getElementById('quality-select').value = d.quality;
      document.getElementById('genre-select').value = d.genre_slug;
      loadTheory();
    });
}

/* ── Delete saved combination ───────────────────────────────── */
function deleteSaved(id, btn) {
  if (!confirm('Delete this saved combination?')) return;
  fetch(`/api/delete/${id}/`, { method: 'POST', headers: { 'X-CSRFToken': CSRF } })
    .then(r => r.json())
    .then(() => {
      const item = btn.closest('.saved-item');
      if (item) item.remove();
    });
}
