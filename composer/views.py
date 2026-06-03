import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from .models import Genre, SavedCombination
from .theory.engine import (
    CHROMATIC, SCALE_INTERVALS, SCALE_DISPLAY_NAMES, CHORD_TYPES,
    get_scale_notes, diatonic_chords, build_progression, improv_map,
    get_chord_notes, get_arpeggio_notes,
)
from .theory.guitar import get_voicings, get_scale_tab, get_arpeggio_tab
from .theory.piano import chord_keyboard, scale_keyboard

ROOT_NOTES = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
QUALITIES = list(SCALE_INTERVALS.keys())


@login_required
def index(request):
    genres = Genre.objects.filter(parent=None)
    saved = SavedCombination.objects.filter(user=request.user)[:10]
    return render(request, 'composer/index.html', {
        'genres': genres,
        'root_notes': ROOT_NOTES,
        'qualities': [(q, SCALE_DISPLAY_NAMES.get(q, q)) for q in QUALITIES],
        'saved': saved,
    })


@login_required
@require_GET
def theory_data(request):
    """
    JSON endpoint: returns all theory data for a root+quality+genre combination.
    ?root=A&quality=minor&genre_slug=jazz
    """
    root = request.GET.get('root', 'C')
    quality = request.GET.get('quality', 'major')
    genre_slug = request.GET.get('genre_slug', '')

    if root not in ROOT_NOTES:
        return JsonResponse({'error': 'Invalid root'}, status=400)
    if quality not in SCALE_INTERVALS:
        return JsonResponse({'error': 'Invalid quality'}, status=400)

    genre = None
    progressions = []
    if genre_slug:
        try:
            genre = Genre.objects.get(slug=genre_slug)
            for tmpl in genre.progression_templates:
                prog = build_progression(root, quality, tmpl['degrees'])
                progressions.append({
                    'name': tmpl['name'],
                    'chords': prog,
                })
        except Genre.DoesNotExist:
            pass

    scale_notes = get_scale_notes(root, quality)
    chords = diatonic_chords(root, quality)

    # Guitar voicings for each diatonic chord
    for chord in chords:
        chord['voicings'] = get_voicings(chord['root'], chord['type'])

    # Piano data for each diatonic chord
    for chord in chords:
        try:
            chord['piano'] = chord_keyboard(chord['root'], chord['type'])
        except Exception:
            chord['piano'] = None

    # Scale tab (5 positions)
    scale_tabs = []
    for pos in range(5):
        try:
            scale_tabs.append(get_scale_tab(root, quality, pos))
        except Exception:
            pass

    # Scale piano
    try:
        scale_piano = scale_keyboard(root, quality)
    except Exception:
        scale_piano = None

    # Improv maps
    improv_maps = []
    if chords:
        # Primary chord improv map
        primary = chords[0]
        improv_maps.append(improv_map(root, quality, primary['type']))
        # V chord if exists
        if len(chords) >= 5:
            v_chord = chords[4]
            improv_maps.append(improv_map(root, quality, v_chord['type']))

    # Arpeggios for each diatonic chord
    arpeggios = []
    for chord in chords[:4]:
        try:
            tab = get_arpeggio_tab(chord['root'], chord['type'])
            notes = get_arpeggio_notes(chord['root'], chord['type'])
            arpeggios.append({
                'symbol': chord['symbol'],
                'notes': notes,
                'tab': tab,
            })
        except Exception:
            pass

    # Scales/modes info
    scales_info = []
    if genre:
        for scale_name in genre.primary_scales:
            if scale_name in SCALE_INTERVALS:
                try:
                    notes = get_scale_notes(root, scale_name)
                    scales_info.append({
                        'name': scale_name,
                        'display': SCALE_DISPLAY_NAMES.get(scale_name, scale_name),
                        'notes': notes,
                    })
                except Exception:
                    pass
    # Always include the primary scale
    scales_info.insert(0, {
        'name': quality,
        'display': SCALE_DISPLAY_NAMES.get(quality, quality),
        'notes': scale_notes,
    })
    # Deduplicate
    seen = set()
    unique_scales = []
    for s in scales_info:
        if s['name'] not in seen:
            seen.add(s['name'])
            unique_scales.append(s)

    return JsonResponse({
        'root': root,
        'quality': quality,
        'quality_display': SCALE_DISPLAY_NAMES.get(quality, quality),
        'genre': {'name': genre.name, 'slug': genre.slug, 'feel': genre.feel} if genre else None,
        'scale_notes': scale_notes,
        'chords': chords,
        'progressions': progressions,
        'scale_tabs': scale_tabs,
        'scale_piano': scale_piano,
        'improv_maps': improv_maps,
        'arpeggios': arpeggios,
        'scales': unique_scales,
    })


@login_required
@require_POST
def save_combination(request):
    data = json.loads(request.body)
    combo = SavedCombination.objects.create(
        user=request.user,
        name=data.get('name', 'Untitled'),
        root_note=data['root'],
        quality=data['quality'],
        genre_id=data['genre_id'],
        notes=data.get('notes', ''),
    )
    return JsonResponse({'id': combo.id, 'name': combo.name})


@login_required
@require_POST
def delete_combination(request, pk):
    combo = get_object_or_404(SavedCombination, pk=pk, user=request.user)
    combo.delete()
    return JsonResponse({'ok': True})


@login_required
def load_combination(request, pk):
    combo = get_object_or_404(SavedCombination, pk=pk, user=request.user)
    return JsonResponse({
        'id': combo.id,
        'name': combo.name,
        'root': combo.root_note,
        'quality': combo.quality,
        'genre_slug': combo.genre.slug,
        'notes': combo.notes,
    })


@login_required
def saved_list(request):
    saved = SavedCombination.objects.filter(user=request.user)
    return render(request, 'composer/saved.html', {'saved': saved})
