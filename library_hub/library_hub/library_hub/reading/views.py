from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from books.models import Book
from .models import ReadingProgress, Wishlist, RecentlyViewed, update_streak


@login_required
def save_progress(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)
        page = int(request.POST.get('current_page', 1))
        page = max(1, page)
        progress, _ = ReadingProgress.objects.update_or_create(
            user=request.user, book=book,
            defaults={'current_page': page}
        )
        update_streak(request.user)
        messages.success(request, f'Progress saved — page {progress.current_page}.')
    return redirect('book_detail', pk=book_id)


@login_required
def toggle_wishlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    obj = Wishlist.objects.filter(user=request.user, book=book)
    if obj.exists():
        obj.delete()
        messages.info(request, f'"{book.title}" removed from your wishlist.')
    else:
        Wishlist.objects.create(user=request.user, book=book)
        messages.success(request, f'"{book.title}" added to your wishlist.')
    return redirect('book_detail', pk=book_id)


@login_required
def my_reading(request):
    progress_list = ReadingProgress.objects.filter(user=request.user).select_related('book')
    wishlist = Wishlist.objects.filter(user=request.user).select_related('book')
    recently_viewed = RecentlyViewed.objects.filter(user=request.user).select_related('book')[:10]
    return render(request, 'reading/my_reading.html', {
        'progress_list': progress_list,
        'wishlist': wishlist,
        'recently_viewed': recently_viewed,
    })
