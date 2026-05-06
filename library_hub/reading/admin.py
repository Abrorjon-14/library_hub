from django.contrib import admin
from .models import ReadingProgress, Wishlist, RecentlyViewed


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'current_page', 'updated_at')
    list_filter = ('user',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'viewed_at')
