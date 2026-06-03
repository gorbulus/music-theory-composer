from django.core.management.base import BaseCommand
from composer.models import Genre

GENRES = [
    {
        'name': 'Jazz',
        'slug': 'jazz',
        'description': 'Extended harmonies, ii-V-I progressions, bebop and swing.',
        'primary_scales': ['major', 'dorian', 'mixolydian', 'altered', 'lydian_dominant', 'diminished'],
        'primary_modes': ['dorian', 'mixolydian', 'lydian', 'altered'],
        'progression_templates': [
            {'name': 'ii-V-I', 'degrees': [2, 5, 1]},
            {'name': 'ii-V-I-VI', 'degrees': [2, 5, 1, 6]},
            {'name': 'I-VI-ii-V (Rhythm Changes A)', 'degrees': [1, 6, 2, 5]},
            {'name': 'iii-VI-ii-V', 'degrees': [3, 6, 2, 5]},
            {'name': 'I-IV-iii-VI-ii-V-I', 'degrees': [1, 4, 3, 6, 2, 5, 1]},
        ],
        'characteristic_chord_types': ['maj7', 'min7', 'dom7', 'dom9', 'm7b5', 'dim7', 'maj9'],
        'feel': 'swing',
        'tempo_range': {'min': 60, 'max': 280},
        'sort_order': 1,
    },
    {
        'name': 'Funk',
        'slug': 'funk',
        'description': 'Groove-based, 16th note rhythms, dominant 7th and 9th chords.',
        'primary_scales': ['minor', 'pentatonic_minor', 'dorian', 'mixolydian', 'blues'],
        'primary_modes': ['dorian', 'mixolydian'],
        'progression_templates': [
            {'name': 'I7-IV7 Vamp', 'degrees': [1, 4]},
            {'name': 'i7-IV7', 'degrees': [1, 4]},
            {'name': 'i-VII-VI-VII', 'degrees': [1, 7, 6, 7]},
            {'name': 'i7-bVII7-IV7', 'degrees': [1, 7, 4]},
            {'name': 'i-III-VII-IV', 'degrees': [1, 3, 7, 4]},
        ],
        'characteristic_chord_types': ['dom7', 'dom9', 'min7', 'dom7s9', 'dom7b9', 'dom13'],
        'feel': 'straight 16th',
        'tempo_range': {'min': 80, 'max': 130},
        'sort_order': 2,
    },
    {
        'name': 'Lo-fi',
        'slug': 'lofi',
        'description': 'Mellow jazz-influenced hip-hop. Dusty samples, laid-back feel.',
        'primary_scales': ['major', 'minor', 'dorian', 'pentatonic_major', 'pentatonic_minor'],
        'primary_modes': ['dorian', 'lydian'],
        'progression_templates': [
            {'name': 'I-V-vi-IV', 'degrees': [1, 5, 6, 4]},
            {'name': 'ii-V-I-VI', 'degrees': [2, 5, 1, 6]},
            {'name': 'i-VII-VI-VII', 'degrees': [1, 7, 6, 7]},
            {'name': 'I-IV-I-V', 'degrees': [1, 4, 1, 5]},
            {'name': 'vi-IV-I-V', 'degrees': [6, 4, 1, 5]},
        ],
        'characteristic_chord_types': ['maj7', 'min7', 'dom7', 'maj9', 'min9', 'maj6'],
        'feel': 'laid-back',
        'tempo_range': {'min': 60, 'max': 90},
        'sort_order': 3,
    },
    {
        'name': 'Ambient Downtempo',
        'slug': 'downtempo',
        'description': 'Atmospheric, slow tempos, open voicings and modal harmony.',
        'primary_scales': ['major', 'minor', 'dorian', 'lydian', 'phrygian', 'whole_tone'],
        'primary_modes': ['dorian', 'lydian', 'phrygian'],
        'progression_templates': [
            {'name': 'i-VII Drone', 'degrees': [1, 7]},
            {'name': 'I-II Modal', 'degrees': [1, 2]},
            {'name': 'i-VI-III-VII', 'degrees': [1, 6, 3, 7]},
            {'name': 'i-IV Vamp', 'degrees': [1, 4]},
            {'name': 'I-bVII-IV', 'degrees': [1, 7, 4]},
        ],
        'characteristic_chord_types': ['maj7', 'min7', 'sus4', 'sus2', 'maj9', 'min9'],
        'feel': 'floating',
        'tempo_range': {'min': 50, 'max': 100},
        'sort_order': 4,
    },
    {
        'name': 'Bossa Nova',
        'slug': 'bossa-nova',
        'description': 'Brazilian jazz. Samba rhythm, lush major 7ths and 9ths.',
        'primary_scales': ['major', 'lydian', 'dorian', 'harmonic_minor'],
        'primary_modes': ['lydian', 'dorian'],
        'progression_templates': [
            {'name': 'ii-V-I (Bossa)', 'degrees': [2, 5, 1]},
            {'name': 'I-VI-ii-V', 'degrees': [1, 6, 2, 5]},
            {'name': 'Imaj7-I7-IVmaj7-iv', 'degrees': [1, 1, 4, 4]},
            {'name': 'iii-VI-ii-V', 'degrees': [3, 6, 2, 5]},
        ],
        'characteristic_chord_types': ['maj7', 'maj9', 'min7', 'dom9', 'dom7', 'maj6'],
        'feel': 'samba',
        'tempo_range': {'min': 80, 'max': 160},
        'sort_order': 5,
    },
    {
        'name': 'Blues',
        'slug': 'blues',
        'description': '12-bar form, dominant 7ths throughout, blues scale.',
        'primary_scales': ['blues', 'pentatonic_minor', 'pentatonic_major', 'mixolydian'],
        'primary_modes': ['mixolydian'],
        'progression_templates': [
            {'name': '12-Bar Blues', 'degrees': [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]},
            {'name': 'Quick 4 Blues', 'degrees': [1, 4, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]},
            {'name': 'I-IV-V', 'degrees': [1, 4, 5]},
        ],
        'characteristic_chord_types': ['dom7', 'dom9', 'dom7b9'],
        'feel': 'shuffle',
        'tempo_range': {'min': 60, 'max': 160},
        'sort_order': 6,
    },
    {
        'name': 'Soul / R&B',
        'slug': 'soul',
        'description': 'Gospel-influenced, rich voicings, call-and-response.',
        'primary_scales': ['major', 'minor', 'pentatonic_minor', 'pentatonic_major', 'dorian'],
        'primary_modes': ['mixolydian', 'dorian'],
        'progression_templates': [
            {'name': 'I-IV-V-IV', 'degrees': [1, 4, 5, 4]},
            {'name': 'I-vi-IV-V', 'degrees': [1, 6, 4, 5]},
            {'name': 'ii-V-I', 'degrees': [2, 5, 1]},
            {'name': 'i-VII-VI-V', 'degrees': [1, 7, 6, 5]},
        ],
        'characteristic_chord_types': ['maj7', 'dom7', 'dom9', 'min7', 'maj6', 'dom13'],
        'feel': 'straight',
        'tempo_range': {'min': 60, 'max': 120},
        'sort_order': 7,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with genre data'

    def handle(self, *args, **kwargs):
        for data in GENRES:
            genre, created = Genre.objects.update_or_create(
                slug=data['slug'],
                defaults={k: v for k, v in data.items() if k != 'slug'},
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'{status}: {genre.name}')
        self.stdout.write(self.style.SUCCESS('Genre seed complete.'))
