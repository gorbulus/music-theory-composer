from django.contrib import admin
from .models import Genre, SavedCombination

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'feel', 'sort_order']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SavedCombination)
class SavedCombinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'root_note', 'quality', 'genre', 'updated_at']
