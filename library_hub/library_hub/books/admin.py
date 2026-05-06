from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre_display', 'views_count', 'created_at')
    list_filter = ('genre',)
    search_fields = ('title', 'author')

    @admin.display(description='Janr')
    def genre_display(self, obj):
        return obj.get_genre_display()
