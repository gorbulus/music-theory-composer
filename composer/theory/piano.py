"""
Piano keyboard layout data for chord and scale visualization.
Returns key positions and finger suggestions for rendering in SVG.
"""

from .engine import normalize_root, CHROMATIC, get_chord_notes, get_scale_notes, CHORD_TYPES

# White key pitch classes in order within an octave
WHITE_PCS = [0, 2, 4, 5, 7, 9, 11]  # C D E F G A B
BLACK_PCS = [1, 3, 6, 8, 10]        # C# D# F# G# A#
WHITE_NAMES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Black key position as fraction between white keys (0=left edge, 0.5=center)
BLACK_POSITIONS = {1: 0.6, 3: 1.6, 6: 3.6, 8: 4.6, 10: 5.6}


def keyboard_layout(octaves: int = 2, start_octave: int = 3) -> list[dict]:
    """
    Return a flat list of key descriptors for rendering.
    Each key: {type, pc, note, octave, white_index, position_x (relative), width}
    """
    keys = []
    white_index = 0
    for oct_n in range(octaves):
        for pc in range(12):
            note_name = CHROMATIC[pc]
            if pc in WHITE_PCS:
                keys.append({
                    'type': 'white',
                    'pc': pc,
                    'note': note_name,
                    'octave': start_octave + oct_n,
                    'white_index': white_index + oct_n * 7,
                    'position': white_index + oct_n * 7,
                })
                white_index += 1
        white_index = 0  # reset per-octave tracking handled by oct_n multiplier
    return keys


def chord_keyboard(root: str, chord_type: str, start_octave: int = 3) -> dict:
    """
    Return highlighted keys for a chord voicing on a 2-octave keyboard.
    Includes finger number suggestions (right hand, close position).
    """
    chord_notes = get_chord_notes(root, chord_type)
    _, _, symbol = CHORD_TYPES.get(chord_type, ('', '', ''))

    highlighted = []
    for oct_n in range(2):
        for i, note in enumerate(chord_notes):
            note_norm = normalize_root(note)
            pc = CHROMATIC.index(note_norm)
            if pc in WHITE_PCS:
                key_type = 'white'
                pos = WHITE_PCS.index(pc) + oct_n * 7
            else:
                key_type = 'black'
                pos = BLACK_POSITIONS.get(pc, 0) + oct_n * 7

            highlighted.append({
                'note': note,
                'pc': pc,
                'octave': start_octave + oct_n,
                'key_type': key_type,
                'position': pos,
                'finger': i + 1,  # simplified: 1=thumb ... 5=pinky
                'is_root': (i == 0 and oct_n == 0),
            })
        break  # one octave of chord tones for close voicing

    return {
        'symbol': f"{root}{symbol}",
        'root': root,
        'chord_type': chord_type,
        'notes': chord_notes,
        'highlighted': highlighted,
        'octaves': 2,
        'start_octave': start_octave,
    }


def scale_keyboard(root: str, scale: str, start_octave: int = 3) -> dict:
    """Return highlighted keys for a scale across 1 octave."""
    scale_notes = get_scale_notes(root, scale)
    highlighted = []
    for i, note in enumerate(scale_notes):
        note_norm = normalize_root(note)
        pc = CHROMATIC.index(note_norm)
        if pc in WHITE_PCS:
            key_type = 'white'
            pos = WHITE_PCS.index(pc)
        else:
            key_type = 'black'
            pos = BLACK_POSITIONS.get(pc, 0)

        # Standard fingering patterns (RH ascending)
        rh_fingering = _rh_scale_fingering(scale_notes)
        finger = rh_fingering[i] if i < len(rh_fingering) else i + 1

        highlighted.append({
            'note': note,
            'pc': pc,
            'octave': start_octave,
            'key_type': key_type,
            'position': pos,
            'finger': finger,
            'is_root': (i == 0),
            'degree': i + 1,
        })

    return {
        'root': root,
        'scale': scale,
        'notes': scale_notes,
        'highlighted': highlighted,
        'octaves': 1,
        'start_octave': start_octave,
    }


def _rh_scale_fingering(notes: list[str]) -> list[int]:
    """
    Approximate right-hand fingering for common scale types.
    Uses thumb-under crossings for 7-note scales.
    """
    n = len(notes)
    if n == 7:
        # Standard major/minor: 1-2-3-1-2-3-4 (thumb crosses after 3rd)
        return [1, 2, 3, 1, 2, 3, 4]
    elif n == 5:
        # Pentatonic: 1-2-3-1-2
        return [1, 2, 3, 1, 2]
    elif n == 6:
        # Blues: 1-2-3-4-1-2
        return [1, 2, 3, 4, 1, 2]
    return list(range(1, n + 1))
