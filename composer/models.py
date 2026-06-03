from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subgenres'
    )
    description = models.TextField(blank=True)
    primary_scales = models.JSONField(default=list)
    primary_modes = models.JSONField(default=list)
    progression_templates = models.JSONField(default=list)
    characteristic_chord_types = models.JSONField(default=list)
    feel = models.CharField(max_length=50, blank=True)
    tempo_range = models.JSONField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class SavedCombination(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='combinations')
    name = models.CharField(max_length=200)
    root_note = models.CharField(max_length=3)
    quality = models.CharField(max_length=30)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.root_note} {self.quality} / {self.genre.name})"
