from django.contrib import admin
from .models import Review, ReviewLike


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'like_count', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'book__title')


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')
