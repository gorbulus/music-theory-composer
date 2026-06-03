"""
Guitar voicings, chord diagrams, and tablature generation.
Standard tuning EADGBE (MIDI: 40, 45, 50, 55, 59, 64).
Each string is indexed 0=low E, 5=high e.
"""

from .engine import normalize_root, CHROMATIC, get_scale_notes, get_chord_notes, SCALE_INTERVALS

STRING_OPEN = [40, 45, 50, 55, 59, 64]  # EADGBE in MIDI
STRING_NAMES = ['E', 'A', 'D', 'G', 'B', 'e']

# Curated voicing library: {chord_symbol: [voicing, ...]}
# Voicing: list of 6 ints — fret number, or -1 = muted, 0 = open
# Strings ordered low-E to high-e.
# barre: fret number if full barre, or None
VOICING_LIBRARY = {
    # --- Major ---
    'C':   [{'frets': [-1, 3, 2, 0, 1, 0], 'barre': None, 'label': 'Open C'},
            {'frets': [-1, -1, 2, 1, 1, 0], 'barre': None, 'label': 'Cmaj (Capo 3 shape)'},
            {'frets': [8, 10, 10, 9, 8, 8], 'barre': 8, 'label': 'C barre (VIII)'}],
    'D':   [{'frets': [-1, -1, 0, 2, 3, 2], 'barre': None, 'label': 'Open D'},
            {'frets': [5, 5, 7, 7, 7, 5], 'barre': 5, 'label': 'D barre (V)'}],
    'E':   [{'frets': [0, 2, 2, 1, 0, 0], 'barre': None, 'label': 'Open E'},
            {'frets': [0, 2, 2, 1, 0, 0], 'barre': None, 'label': 'E shape'}],
    'F':   [{'frets': [1, 3, 3, 2, 1, 1], 'barre': 1, 'label': 'F barre (I)'},
            {'frets': [-1, -1, 3, 2, 1, 1], 'barre': 1, 'label': 'F mini barre'}],
    'G':   [{'frets': [3, 2, 0, 0, 0, 3], 'barre': None, 'label': 'Open G'},
            {'frets': [3, 5, 5, 4, 3, 3], 'barre': 3, 'label': 'G barre (III)'}],
    'A':   [{'frets': [-1, 0, 2, 2, 2, 0], 'barre': None, 'label': 'Open A'},
            {'frets': [5, 7, 7, 6, 5, 5], 'barre': 5, 'label': 'A barre (V)'}],
    'B':   [{'frets': [-1, 2, 4, 4, 4, 2], 'barre': 2, 'label': 'B barre (II)'},
            {'frets': [7, 9, 9, 8, 7, 7], 'barre': 7, 'label': 'B barre (VII)'}],
    'C#':  [{'frets': [-1, 4, 6, 6, 6, 4], 'barre': 4, 'label': 'C# barre (IV)'}],
    'Db':  [{'frets': [-1, 4, 6, 6, 6, 4], 'barre': 4, 'label': 'Db barre (IV)'}],
    'D#':  [{'frets': [-1, 6, 8, 8, 8, 6], 'barre': 6, 'label': 'D# barre (VI)'}],
    'Eb':  [{'frets': [-1, 6, 8, 8, 8, 6], 'barre': 6, 'label': 'Eb barre (VI)'}],
    'F#':  [{'frets': [2, 4, 4, 3, 2, 2], 'barre': 2, 'label': 'F# barre (II)'}],
    'Gb':  [{'frets': [2, 4, 4, 3, 2, 2], 'barre': 2, 'label': 'Gb barre (II)'}],
    'G#':  [{'frets': [4, 6, 6, 5, 4, 4], 'barre': 4, 'label': 'G# barre (IV)'}],
    'Ab':  [{'frets': [4, 6, 6, 5, 4, 4], 'barre': 4, 'label': 'Ab barre (IV)'}],
    'A#':  [{'frets': [6, 8, 8, 7, 6, 6], 'barre': 6, 'label': 'A# barre (VI)'}],
    'Bb':  [{'frets': [6, 8, 8, 7, 6, 6], 'barre': 6, 'label': 'Bb barre (VI)'}],

    # --- Minor ---
    'Cm':  [{'frets': [-1, 3, 5, 5, 4, 3], 'barre': 3, 'label': 'Cm barre (III)'}],
    'Dm':  [{'frets': [-1, -1, 0, 2, 3, 1], 'barre': None, 'label': 'Open Dm'}],
    'Em':  [{'frets': [0, 2, 2, 0, 0, 0], 'barre': None, 'label': 'Open Em'},
            {'frets': [0, 2, 2, 0, 0, 0], 'barre': None, 'label': 'Em open'}],
    'Fm':  [{'frets': [1, 3, 3, 1, 1, 1], 'barre': 1, 'label': 'Fm barre (I)'}],
    'Gm':  [{'frets': [3, 5, 5, 3, 3, 3], 'barre': 3, 'label': 'Gm barre (III)'}],
    'Am':  [{'frets': [-1, 0, 2, 2, 1, 0], 'barre': None, 'label': 'Open Am'},
            {'frets': [5, 7, 7, 5, 5, 5], 'barre': 5, 'label': 'Am barre (V)'}],
    'Bm':  [{'frets': [-1, 2, 4, 4, 3, 2], 'barre': 2, 'label': 'Bm barre (II)'}],
    'C#m': [{'frets': [-1, 4, 6, 6, 5, 4], 'barre': 4, 'label': 'C#m barre (IV)'}],
    'Dbm': [{'frets': [-1, 4, 6, 6, 5, 4], 'barre': 4, 'label': 'Dbm barre (IV)'}],
    'D#m': [{'frets': [-1, 6, 8, 8, 7, 6], 'barre': 6, 'label': 'D#m barre (VI)'}],
    'Ebm': [{'frets': [-1, 6, 8, 8, 7, 6], 'barre': 6, 'label': 'Ebm barre (VI)'}],
    'F#m': [{'frets': [2, 4, 4, 2, 2, 2], 'barre': 2, 'label': 'F#m barre (II)'}],
    'Gbm': [{'frets': [2, 4, 4, 2, 2, 2], 'barre': 2, 'label': 'Gbm barre (II)'}],
    'G#m': [{'frets': [4, 6, 6, 4, 4, 4], 'barre': 4, 'label': 'G#m barre (IV)'}],
    'Abm': [{'frets': [4, 6, 6, 4, 4, 4], 'barre': 4, 'label': 'Abm barre (IV)'}],
    'A#m': [{'frets': [6, 8, 8, 6, 6, 6], 'barre': 6, 'label': 'A#m barre (VI)'}],
    'Bbm': [{'frets': [6, 8, 8, 6, 6, 6], 'barre': 6, 'label': 'Bbm barre (VI)'}],

    # --- 7th chords ---
    'Cmaj7': [{'frets': [-1, 3, 2, 0, 0, 0], 'barre': None, 'label': 'Cmaj7 open'},
              {'frets': [-1, 3, 5, 4, 5, 3], 'barre': 3, 'label': 'Cmaj7 barre'}],
    'Dmaj7': [{'frets': [-1, -1, 0, 2, 2, 2], 'barre': None, 'label': 'Dmaj7 open'}],
    'Emaj7': [{'frets': [0, 2, 1, 1, 0, 0], 'barre': None, 'label': 'Emaj7 open'}],
    'Fmaj7': [{'frets': [-1, -1, 3, 2, 1, 0], 'barre': None, 'label': 'Fmaj7 open'}],
    'Gmaj7': [{'frets': [3, 2, 0, 0, 0, 2], 'barre': None, 'label': 'Gmaj7 open'}],
    'Amaj7': [{'frets': [-1, 0, 2, 1, 2, 0], 'barre': None, 'label': 'Amaj7 open'}],

    'Am7':   [{'frets': [-1, 0, 2, 0, 1, 0], 'barre': None, 'label': 'Am7 open'},
              {'frets': [5, 7, 5, 5, 5, 5], 'barre': 5, 'label': 'Am7 barre'}],
    'Dm7':   [{'frets': [-1, -1, 0, 2, 1, 1], 'barre': None, 'label': 'Dm7 open'}],
    'Em7':   [{'frets': [0, 2, 2, 0, 3, 0], 'barre': None, 'label': 'Em7 open'},
              {'frets': [0, 2, 0, 0, 0, 0], 'barre': None, 'label': 'Em7 simple'}],
    'Fm7':   [{'frets': [1, 3, 1, 1, 1, 1], 'barre': 1, 'label': 'Fm7 barre'}],
    'Gm7':   [{'frets': [3, 5, 3, 3, 3, 3], 'barre': 3, 'label': 'Gm7 barre'}],
    'Bm7':   [{'frets': [-1, 2, 4, 2, 3, 2], 'barre': 2, 'label': 'Bm7 barre'}],
    'C#m7':  [{'frets': [-1, 4, 6, 4, 5, 4], 'barre': 4, 'label': 'C#m7 barre'}],
    'F#m7':  [{'frets': [2, 4, 2, 2, 2, 2], 'barre': 2, 'label': 'F#m7 barre'}],

    'G7':    [{'frets': [3, 2, 0, 0, 0, 1], 'barre': None, 'label': 'G7 open'}],
    'A7':    [{'frets': [-1, 0, 2, 0, 2, 0], 'barre': None, 'label': 'A7 open'}],
    'B7':    [{'frets': [-1, 2, 1, 2, 0, 2], 'barre': None, 'label': 'B7 open'}],
    'C7':    [{'frets': [-1, 3, 2, 3, 1, 0], 'barre': None, 'label': 'C7 open'}],
    'D7':    [{'frets': [-1, -1, 0, 2, 1, 2], 'barre': None, 'label': 'D7 open'}],
    'E7':    [{'frets': [0, 2, 0, 1, 0, 0], 'barre': None, 'label': 'E7 open'}],
    'F7':    [{'frets': [1, 3, 1, 2, 1, 1], 'barre': 1, 'label': 'F7 barre'}],
    'F#7':   [{'frets': [2, 4, 2, 3, 2, 2], 'barre': 2, 'label': 'F#7 barre'}],

    # --- Dominant 9 (jazz/funk staples) ---
    'A9':    [{'frets': [-1, 0, 2, 4, 2, 3], 'barre': None, 'label': 'A9'}],
    'D9':    [{'frets': [-1, 5, 4, 5, 3, 5], 'barre': None, 'label': 'D9'}],
    'G9':    [{'frets': [3, 2, 3, 2, 3, -1], 'barre': None, 'label': 'G9'}],
    'E9':    [{'frets': [0, 2, 0, 1, 3, 2], 'barre': None, 'label': 'E9'}],
    'C9':    [{'frets': [-1, 3, 2, 3, 3, 3], 'barre': 3, 'label': 'C9 barre'}],
}


def get_voicings(root: str, chord_type: str) -> list[dict]:
    """Return curated voicings for a chord. Falls back to generated if not found."""
    from .engine import CHORD_TYPES
    _, _, symbol = CHORD_TYPES.get(chord_type, ('', '', ''))
    key = f"{root}{symbol}"
    voicings = VOICING_LIBRARY.get(key, [])
    if not voicings:
        voicings = _generate_voicing(root, chord_type)
    return voicings


def _generate_voicing(root: str, chord_type: str) -> list[dict]:
    """Generate a barre voicing by finding root on low-E or A string."""
    from .engine import CHORD_TYPES, normalize_root
    _, intervals, symbol = CHORD_TYPES.get(chord_type, ('', [0, 4, 7], ''))
    try:
        root_norm = normalize_root(root)
        root_midi = [40, 45, 50, 55, 59, 64][0] % 12
        root_pc = [40, 45, 50, 55, 59, 64]
        # Find fret on low-E (string 0, open=E=40)
        low_e_pc = 40 % 12
        from .engine import CHROMATIC
        root_idx = CHROMATIC.index(root_norm)
        low_e_idx = 40 % 12  # E
        fret = (root_idx - low_e_idx) % 12
        frets = []
        for s, open_midi in enumerate(STRING_OPEN):
            # Find nearest chord tone
            best_fret = -1
            best_dist = 999
            for interval in intervals:
                target_pc = (root_idx + interval) % 12
                string_pc = open_midi % 12
                f = (target_pc - string_pc) % 12
                if f <= 5 or abs(f - fret) <= 2:
                    candidate = (target_pc - string_pc) % 12
                    if abs(candidate - fret) < best_dist:
                        best_dist = abs(candidate - fret)
                        best_fret = candidate
            frets.append(best_fret if best_fret != -1 else fret)
        return [{'frets': frets, 'barre': fret, 'label': f'{root}{symbol} (generated)'}]
    except Exception:
        return [{'frets': [0, 0, 0, 0, 0, 0], 'barre': None, 'label': f'{root}{symbol}'}]


# CAGED scale box positions on fretboard
# Returns list of positions: each is a list of (string, fret) tuples
def get_scale_tab(root: str, scale: str, position: int = 0) -> dict:
    """
    Return tablature for a scale at a given CAGED position (0-4).
    Output: {'position': N, 'fret_span': (low, high), 'notes': [(string, fret, note_name), ...]}
    """
    from .engine import normalize_root, CHROMATIC
    scale_pcs = set()
    from .engine import get_scale_notes, SCALE_INTERVALS
    scale_notes = get_scale_notes(root, scale)
    scale_pcs = set(CHROMATIC.index(n) if n in CHROMATIC else None for n in scale_notes)
    scale_pcs.discard(None)

    # CAGED base frets (approximate box starting frets for each position)
    root_norm = normalize_root(root)
    root_pc = CHROMATIC.index(root_norm)

    # Find lowest root on low-E string
    low_e_root_fret = (root_pc - (40 % 12)) % 12
    if low_e_root_fret == 0:
        low_e_root_fret = 12

    box_offsets = [0, 3, 5, 7, 10]
    start_fret = (low_e_root_fret + box_offsets[position % 5]) % 12
    if start_fret == 0:
        start_fret = 12

    notes = []
    for string_idx, open_midi in enumerate(STRING_OPEN):
        open_pc = open_midi % 12
        for fret in range(start_fret - 1, start_fret + 5):
            if fret < 0:
                continue
            note_pc = (open_pc + fret) % 12
            if note_pc in scale_pcs:
                note_name = CHROMATIC[note_pc]
                is_root = (note_pc == root_pc)
                notes.append({
                    'string': string_idx,
                    'string_name': STRING_NAMES[string_idx],
                    'fret': fret,
                    'note': note_name,
                    'is_root': is_root,
                })

    frets_used = [n['fret'] for n in notes if n['fret'] > 0]
    fret_min = min(frets_used) if frets_used else start_fret
    fret_max = max(frets_used) if frets_used else start_fret + 4

    return {
        'position': position + 1,
        'fret_min': fret_min,
        'fret_max': fret_max,
        'notes': notes,
        'scale': scale,
        'root': root,
    }


def get_arpeggio_tab(root: str, chord_type: str) -> dict:
    """Return fretboard positions for an arpeggio."""
    from .engine import CHORD_TYPES, normalize_root, CHROMATIC
    _, intervals, symbol = CHORD_TYPES.get(chord_type, ('', [0, 4, 7], ''))
    root_norm = normalize_root(root)
    root_pc = CHROMATIC.index(root_norm)
    chord_pcs = set((root_pc + i) % 12 for i in intervals)

    low_e_root_fret = (root_pc - (40 % 12)) % 12
    if low_e_root_fret == 0:
        low_e_root_fret = 12

    notes = []
    for string_idx, open_midi in enumerate(STRING_OPEN):
        open_pc = open_midi % 12
        for fret in range(low_e_root_fret - 2, low_e_root_fret + 7):
            if fret < 0:
                continue
            note_pc = (open_pc + fret) % 12
            if note_pc in chord_pcs:
                note_name = CHROMATIC[note_pc]
                is_root = (note_pc == root_pc)
                notes.append({
                    'string': string_idx,
                    'string_name': STRING_NAMES[string_idx],
                    'fret': fret,
                    'note': note_name,
                    'is_root': is_root,
                })

    frets_used = [n['fret'] for n in notes if n['fret'] > 0]
    return {
        'root': root,
        'chord_type': chord_type,
        'symbol': f"{root}{symbol}",
        'fret_min': min(frets_used) if frets_used else low_e_root_fret,
        'fret_max': max(frets_used) if frets_used else low_e_root_fret + 5,
        'notes': notes,
    }
