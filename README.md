# 🎮 Music Theory Composer

> Your personal SNES-themed music theory sidekick — built for guitarists and composers.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?style=flat-square&logo=django)
![SNES.css](https://img.shields.io/badge/UI-SNES.css-9b5de5?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-f2c019?style=flat-square)

---

## What It Does

Select a **key**, a **scale/mode**, and a **genre** — and instantly get:

| Panel | Contents |
|---|---|
| **Progressions** | Genre-appropriate chord progressions (ii-V-I, i-VII-VI, etc.) |
| **Chords** | All diatonic chords with guitar chord charts + piano voicings |
| **Scales & Modes** | Scale notes with 5 CAGED fretboard positions + piano keyboard |
| **Arpeggios** | Chord arpeggio shapes on the fretboard |
| **Improv Maps** | Target tones vs. passing tones highlighted for soloing |

Supports a **Guitar / Piano toggle** so you can see the same harmony visualized on both instruments.

---

## Screenshots

```
♪ MTC ♪                                              [SAVED] [▶ user] [QUIT]
───────────────────────────────────────────────────────────────────────────────
┌──────────────────┐  ▶ A NATURAL MINOR / JAZZ
│  SELECT KEY      │  ─────────────────────────────────────────────────────
│  Root:  [A  ▼]   │  [PROGRESSIONS] [CHORDS] [SCALES] [ARPEGGIOS] [IMPROV]
│  Scale: [minor▼] │
│  Genre: [Jazz ▼] │  ┌─────────┐ ┌─────────┐ ┌─────────┐
│                  │  │  ii-V-i │ │   Am7   │ │   Dm7   │
│  [▶ LOAD]        │  │ Bm7b5   │ │         │ │         │
├──────────────────┤  │  Em7    │ │ [chord  │ │ [chord  │
│  VIEW            │  │  Am7    │ │  chart] │ │  chart] │
│ [GUITAR] [PIANO] │  └─────────┘ └─────────┘ └─────────┘
└──────────────────┘
```

---

## Genres

| Genre | Key Scales | Characteristic Chords | Feel |
|---|---|---|---|
| **Jazz** | Dorian, Mixolydian, Altered, Diminished | maj7, min7, dom9, m7b5, dim7 | Swing |
| **Funk** | Dorian, Pentatonic Minor, Blues | dom7, dom9, 7#9, 7b9, 13 | Straight 16th |
| **Lo-fi** | Major, Dorian, Lydian | maj7, min7, maj9, m9, maj6 | Laid-back |
| **Ambient Downtempo** | Lydian, Phrygian, Whole Tone | maj7, sus4, sus2, min9 | Floating |
| **Bossa Nova** | Lydian, Dorian, Harmonic Minor | maj7, maj9, dom9, maj6 | Samba |
| **Blues** | Blues, Pentatonic Minor, Mixolydian | dom7, dom9, 7b9 | Shuffle |
| **Soul / R&B** | Dorian, Pentatonic Major/Minor | maj7, dom9, 13, maj6 | Straight |

> **Designed for microgenre expansion** — every genre is a database row with JSON arrays for scales, progressions, and chord types. Add a new genre with zero code changes.

---

## Tech Stack

- **Backend** — Django 5.2 + pure Python music theory engine (no external music libraries)
- **Database** — SQLite (dev) / Postgres-ready
- **Frontend** — Django templates + Vanilla JS + SVG diagrams (no build step)
- **UI** — [SNES.css](https://github.com/devMiguelCarrero/snes.css) — pixel-art component library with Press Start 2P font
- **Auth** — Django built-in `contrib.auth` (multi-user)

---

## Local Setup

### Requirements
- Python 3.10+
- pip

### Install & Run

```bash
# 1. Clone
git clone https://github.com/gorbulus/music-theory-composer.git
cd music-theory-composer

# 2. Create virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Migrate database
python manage.py migrate

# 5. Seed genres
python manage.py seed_genres

# 6. Create your account
python manage.py createsuperuser

# 7. Run
python manage.py runserver
```

Open **http://127.0.0.1:8000** — register, log in, and start composing.

---

## Project Structure

```
music-theory-composer/
├── composer/
│   ├── theory/
│   │   ├── engine.py        # Core music theory engine (scales, modes, chords)
│   │   ├── guitar.py        # Guitar voicings, CAGED tab, arpeggio fretboard
│   │   └── piano.py         # Piano keyboard layout + fingering
│   ├── management/commands/
│   │   └── seed_genres.py   # Django mgmt command to seed genre data
│   ├── models.py            # Genre, SavedCombination
│   └── views.py             # Main composer view + JSON theory API
├── accounts/                # Login / register / logout
├── templates/
│   ├── base.html
│   ├── composer/
│   │   ├── index.html       # Main composer UI
│   │   └── saved.html       # Saved combinations list
│   └── accounts/
│       ├── login.html
│       └── register.html
├── static/
│   ├── css/main.css         # Layout + SNES palette overrides
│   └── js/
│       ├── diagrams.js      # SVG renderers: chord chart, fretboard, piano
│       └── composer.js      # App logic, fetch, tab switching, state
└── config/                  # Django settings, urls, wsgi
```

---

## Music Theory Engine

The engine in `composer/theory/engine.py` is entirely algorithmic — no hardcoded scales per key. Given any root note, it:

1. Computes the chromatic pitch class for the root
2. Applies interval patterns (e.g. `[0,2,3,5,7,8,10]` for natural minor)
3. Derives diatonic chord qualities from the scale
4. Generates chord tones, arpeggio sequences, and improv tone roles

**Scales supported:** Major, all 7 modes, Harmonic Minor, Melodic Minor, Pentatonic Major/Minor, Blues, Whole Tone, Diminished, Lydian Dominant, Altered, Phrygian Dominant.

**Chord types:** triads, 6ths, 7ths, 9ths, 11ths, 13ths, altered dominants (7b9, 7#9), dim7, m7b5, minMaj7.

---

## Guitar Diagrams

- **Chord charts** — SVG fretboard grid, barre indicators, open/muted strings, root highlighting
- **Scale tab** — 5 CAGED positions, configurable via position buttons
- **Arpeggio tab** — fretboard positions for each diatonic chord's arpeggio
- Standard tuning EADGBE only (v1). Alternate tunings on the roadmap.

---

## Roadmap

- [ ] Alternate guitar tunings (Drop D, Open G, Open E)
- [ ] Microgenre expansion (Bebop, Samba, Neo-Soul, Afrobeat...)
- [ ] User-editable notes per saved combination
- [ ] MIDI playback of progressions / arpeggios
- [ ] Export chord charts as PNG/PDF
- [ ] Mobile-responsive layout

---

## Contributing

This is a personal project built to support music composition — PRs and issues welcome, especially for:
- Additional genre definitions
- Curated guitar voicings for unusual chord types
- Alternate tuning support

---

## License

MIT — do whatever you want with it, just keep making music.

---

*Built with [Claude Code](https://claude.ai/claude-code) + [SNES.css](https://github.com/devMiguelCarrero/snes.css)*
