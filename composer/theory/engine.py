"""
Core music theory computation engine.
All output is computed from intervals — nothing is hardcoded per-key.
"""

CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC = {
    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#',
    'C#': 'C#', 'D#': 'D#', 'F#': 'F#', 'G#': 'G#', 'A#': 'A#',
}
FLAT_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Interval patterns (semitones from root)
SCALE_INTERVALS = {
    'major':       [0, 2, 4, 5, 7, 9, 11],
    'minor':       [0, 2, 3, 5, 7, 8, 10],
    'dorian':      [0, 2, 3, 5, 7, 9, 10],
    'phrygian':    [0, 1, 3, 5, 7, 8, 10],
    'lydian':      [0, 2, 4, 6, 7, 9, 11],
    'mixolydian':  [0, 2, 4, 5, 7, 9, 10],
    'locrian':     [0, 1, 3, 5, 6, 8, 10],
    'harmonic_minor':   [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor':    [0, 2, 3, 5, 7, 9, 11],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues':       [0, 3, 5, 6, 7, 10],
    'whole_tone':  [0, 2, 4, 6, 8, 10],
    'diminished':  [0, 2, 3, 5, 6, 8, 9, 11],
    'lydian_dominant': [0, 2, 4, 6, 7, 9, 10],
    'altered':     [0, 1, 3, 4, 6, 8, 10],
    'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],
}

SCALE_DISPLAY_NAMES = {
    'major': 'Major (Ionian)',
    'minor': 'Natural Minor (Aeolian)',
    'dorian': 'Dorian',
    'phrygian': 'Phrygian',
    'lydian': 'Lydian',
    'mixolydian': 'Mixolydian',
    'locrian': 'Locrian',
    'harmonic_minor': 'Harmonic Minor',
    'melodic_minor': 'Melodic Minor',
    'pentatonic_major': 'Major Pentatonic',
    'pentatonic_minor': 'Minor Pentatonic',
    'blues': 'Blues Scale',
    'whole_tone': 'Whole Tone',
    'diminished': 'Diminished (Half-Whole)',
    'lydian_dominant': 'Lydian Dominant',
    'altered': 'Altered (Super Locrian)',
    'phrygian_dominant': 'Phrygian Dominant',
}

# Chord types: {name: (display, intervals, symbol)}
CHORD_TYPES = {
    'maj':   ('Major',              [0, 4, 7],        ''),
    'min':   ('Minor',              [0, 3, 7],        'm'),
    'dim':   ('Diminished',         [0, 3, 6],        'dim'),
    'aug':   ('Augmented',          [0, 4, 8],        'aug'),
    'sus2':  ('Sus2',               [0, 2, 7],        'sus2'),
    'sus4':  ('Sus4',               [0, 5, 7],        'sus4'),
    'maj7':  ('Major 7th',          [0, 4, 7, 11],    'maj7'),
    'min7':  ('Minor 7th',          [0, 3, 7, 10],    'm7'),
    'dom7':  ('Dominant 7th',       [0, 4, 7, 10],    '7'),
    'dim7':  ('Diminished 7th',     [0, 3, 6, 9],     'dim7'),
    'm7b5':  ('Half-Diminished',    [0, 3, 6, 10],    'm7b5'),
    'minmaj7': ('Minor Major 7th',  [0, 3, 7, 11],    'mMaj7'),
    'maj9':  ('Major 9th',          [0, 4, 7, 11, 14], 'maj9'),
    'min9':  ('Minor 9th',          [0, 3, 7, 10, 14], 'm9'),
    'dom9':  ('Dominant 9th',       [0, 4, 7, 10, 14], '9'),
    'dom7b9': ('7b9',               [0, 4, 7, 10, 13], '7b9'),
    'dom7s9': ('7#9',               [0, 4, 7, 10, 15], '7#9'),
    'maj6':  ('Major 6th',          [0, 4, 7, 9],     '6'),
    'min6':  ('Minor 6th',          [0, 3, 7, 9],     'm6'),
    'dom11': ('Dominant 11th',      [0, 4, 7, 10, 14, 17], '11'),
    'maj13': ('Major 13th',         [0, 4, 7, 11, 14, 21], 'maj13'),
    'dom13': ('Dominant 13th',      [0, 4, 7, 10, 14, 21], '13'),
}

# Scale degree -> chord quality for each scale
SCALE_CHORD_QUALITIES = {
    'major':      ['maj7', 'min7', 'min7', 'maj7', 'dom7', 'min7', 'm7b5'],
    'minor':      ['min7', 'm7b5', 'maj7', 'min7', 'min7', 'maj7', 'dom7'],
    'dorian':     ['min7', 'min7', 'maj7', 'dom7', 'min7', 'm7b5', 'maj7'],
    'mixolydian': ['dom7', 'min7', 'm7b5', 'maj7', 'min7', 'min7', 'maj7'],
    'harmonic_minor': ['minmaj7', 'm7b5', 'maj7', 'min7', 'dom7', 'maj7', 'dim7'],
    'melodic_minor':  ['minmaj7', 'min7', 'maj7', 'dom7', 'dom7', 'm7b5', 'm7b5'],
}


def normalize_root(root: str) -> str:
    if root in ENHARMONIC:
        return ENHARMONIC[root]
    if root in CHROMATIC:
        return root
    raise ValueError(f"Unknown root: {root}")


def root_index(root: str) -> int:
    r = normalize_root(root)
    return CHROMATIC.index(r)


def note_at(root: str, semitones: int, prefer_flats: bool = False) -> str:
    idx = (root_index(root) + semitones) % 12
    if prefer_flats:
        return FLAT_NAMES[idx]
    return CHROMATIC[idx]


def get_scale_notes(root: str, scale: str) -> list[str]:
    intervals = SCALE_INTERVALS.get(scale)
    if not intervals:
        raise ValueError(f"Unknown scale: {scale}")
    prefer_flats = root in ('F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb')
    return [note_at(root, i, prefer_flats) for i in intervals]


def get_chord_notes(root: str, chord_type: str) -> list[str]:
    _, intervals, _ = CHORD_TYPES[chord_type]
    prefer_flats = root in ('F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb')
    return [note_at(root, i % 12, prefer_flats) for i in intervals]


def get_chord_symbol(root: str, chord_type: str) -> str:
    _, _, symbol = CHORD_TYPES[chord_type]
    return f"{root}{symbol}"


def diatonic_chords(root: str, scale: str) -> list[dict]:
    """Return all diatonic chords for a scale with notes and symbols."""
    scale_notes = get_scale_notes(root, scale)
    qualities = SCALE_CHORD_QUALITIES.get(scale, ['maj7'] * len(scale_notes))
    result = []
    for i, note in enumerate(scale_notes):
        q = qualities[i] if i < len(qualities) else 'maj7'
        chord_notes = get_chord_notes(note, q)
        _, _, symbol = CHORD_TYPES[q]
        result.append({
            'degree': i + 1,
            'root': note,
            'type': q,
            'symbol': f"{note}{symbol}",
            'notes': chord_notes,
            'display': CHORD_TYPES[q][0],
        })
    return result


DEGREE_NAMES = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']

def build_progression(root: str, scale: str, degrees: list[int]) -> list[dict]:
    """Build a chord progression from scale degree numbers (1-indexed)."""
    all_chords = diatonic_chords(root, scale)
    scale_len = len(SCALE_INTERVALS.get(scale, [0]*7))
    result = []
    for deg in degrees:
        idx = (deg - 1) % scale_len
        if idx < len(all_chords):
            chord = dict(all_chords[idx])
            chord['degree_name'] = DEGREE_NAMES[idx] if idx < 7 else str(deg)
            result.append(chord)
    return result


def get_arpeggio_notes(root: str, chord_type: str, octaves: int = 2) -> list[dict]:
    """Return arpeggio note sequence with octave and semitone info."""
    _, intervals, _ = CHORD_TYPES[chord_type]
    prefer_flats = root in ('F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb')
    notes = []
    for oct_n in range(octaves):
        for interval in intervals:
            semitone = interval + (oct_n * 12)
            note_name = note_at(root, interval, prefer_flats)
            notes.append({'note': note_name, 'octave': oct_n, 'semitone': semitone})
    return notes


def improv_map(root: str, scale: str, chord_type: str | None = None) -> dict:
    """
    Return scale notes + chord tones highlighted for improvisation guidance.
    Chord tones are marked as 'target', passing tones as 'passing'.
    """
    scale_notes = get_scale_notes(root, scale)
    chord_tones = set()
    if chord_type:
        chord_tones = set(get_chord_notes(root, chord_type))

    notes_map = []
    for note in scale_notes:
        role = 'target' if note in chord_tones else 'passing'
        notes_map.append({'note': note, 'role': role})

    return {
        'scale': scale,
        'scale_display': SCALE_DISPLAY_NAMES.get(scale, scale),
        'root': root,
        'notes': notes_map,
        'chord_tones': list(chord_tones),
    }


ALL_NOTES = CHROMATIC

def note_midi(note: str, octave: int = 4) -> int:
    """Return MIDI note number (C4 = 60)."""
    idx = CHROMATIC.index(normalize_root(note))
    return (octave + 1) * 12 + idx
