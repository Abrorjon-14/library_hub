from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Book

def book_list(request):
    books = Book.objects.annotate(avg_rating=Avg('reviews__rating'))

    query = request.GET.get('q', '').strip()
    if query:
        books = books.filter(title__icontains=query)

    genre = request.GET.get('genre', '').strip()
    if genre:
        books = books.filter(genre=genre)

    paginator = Paginator(books, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_genre': genre,
        'genres': Book.GENRE_CHOICES,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    Book.objects.filter(pk=pk).update(views_count=book.views_count + 1)
    book.refresh_from_db()

    progress = None
    in_wishlist = False
    if request.user.is_authenticated:
        from reading.models import RecentlyViewed, ReadingProgress, Wishlist
        RecentlyViewed.objects.update_or_create(user=request.user, book=book)
        progress = ReadingProgress.objects.filter(user=request.user, book=book).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()

    # Reviews
    from reviews.models import Review
    reviews = book.reviews.select_related('user').prefetch_related('likes')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    user_review = None
    liked_review_ids = set()
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        liked_review_ids = set(
            book.reviews.filter(likes__user=request.user).values_list('id', flat=True)
        )

    return render(request, 'books/book_detail.html', {
        'book': book,
        'progress': progress,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'liked_review_ids': liked_review_ids,
    })


def book_read(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.pdf_file:
        raise Http404("No PDF available for this book.")

    progress = None
    resumed = False

    if request.user.is_authenticated:
        from reading.models import ReadingProgress, update_streak

        # POST: user saved a page number from the reading page
        if request.method == 'POST':
            try:
                page = int(request.POST.get('current_page', 1))
                page = max(1, page)
                if book.total_pages:
                    page = min(page, book.total_pages)
            except (ValueError, TypeError):
                page = 1
            progress, _ = ReadingProgress.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={'current_page': page},
            )
            update_streak(request.user)
        else:
            # GET: create record on first visit, or load existing
            progress, created = ReadingProgress.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={'current_page': 1},
            )
            update_streak(request.user)

        resumed = progress.current_page > 1

    return render(request, 'books/book_read.html', {
        'book': book,
        'progress': progress,
        'resumed': resumed,
    })


def save_reading_progress(request, pk):
    """AJAX endpoint — saves current PDF page for authenticated users."""
    if not request.user.is_authenticated:
        from django.http import JsonResponse
        return JsonResponse({'error': 'login required'}, status=401)

    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'error': 'method not allowed'}, status=405)

    from django.http import JsonResponse
    from reading.models import ReadingProgress, update_streak

    book = get_object_or_404(Book, pk=pk)

    try:
        import json
        data = json.loads(request.body)
        page = int(data.get('page', 1))
        page = max(1, page)
        if book.total_pages:
            page = min(page, book.total_pages)
    except (ValueError, TypeError, Exception):
        return JsonResponse({'error': 'invalid page'}, status=400)

    progress, _ = ReadingProgress.objects.update_or_create(
        user=request.user,
        book=book,
        defaults={'current_page': page},
    )
    update_streak(request.user)

    return JsonResponse({'saved': True, 'page': progress.current_page})
