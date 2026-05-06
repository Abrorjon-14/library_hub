from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Book


def book_list(request):
    books = Book.objects.all()

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
