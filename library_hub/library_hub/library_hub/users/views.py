from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    from django.db.models import Sum, Count, F, Q
    from django.utils import timezone
    from reading.models import ReadingProgress, Wishlist, ReadingStreak
    from reviews.models import Review

    user = request.user

    # ── Core counts ──────────────────────────────────────────────────────────
    all_progress = (
        ReadingProgress.objects
        .filter(user=user)
        .select_related('book')
    )

    books_started   = all_progress.count()
    wishlist_count  = Wishlist.objects.filter(user=user).count()
    reviews_count   = Review.objects.filter(user=user).count()

    # Books considered "finished": progress ≥ 100 % (requires total_pages set)
    books_finished = sum(
        1 for p in all_progress
        if p.book.total_pages and p.current_page >= p.book.total_pages
    )

    # ── Pages read ───────────────────────────────────────────────────────────
    # Sum current_page across all tracked books (best real approximation)
    total_pages_read = sum(p.current_page for p in all_progress)

    # ── Currently in-progress (not finished, ordered by last activity) ───────
    in_progress = [
        p for p in all_progress
        if not (p.book.total_pages and p.current_page >= p.book.total_pages)
    ][:3]

    # ── Favourite genre ──────────────────────────────────────────────────────
    # Count books per genre across all tracked books, pick the top one
    genre_counts: dict[str, int] = {}
    for p in all_progress:
        g = p.book.get_genre_display()
        genre_counts[g] = genre_counts.get(g, 0) + 1
    favourite_genre = max(genre_counts, key=genre_counts.get) if genre_counts else None

    # ── Active reading days ──────────────────────────────────────────────────
    # Count distinct calendar dates where progress was updated (approximation
    # using updated_at — one date per distinct day).
    active_dates = (
        ReadingProgress.objects
        .filter(user=user)
        .dates('updated_at', 'day')       # returns distinct date objects
    )
    active_days = active_dates.count()

    # ── Avg pages per active day ─────────────────────────────────────────────
    avg_pages_per_day = (
        round(total_pages_read / active_days) if active_days else 0
    )

    # ── Streak ───────────────────────────────────────────────────────────────
    streak = ReadingStreak.objects.filter(user=user).first()

    # ── Recent activity feed ─────────────────────────────────────────────────
    recent_reviews = [
        {'type': 'review', 'book': r.book, 'date': r.created_at, 'rating': r.rating}
        for r in Review.objects.filter(user=user).select_related('book').order_by('-created_at')[:10]
    ]
    recent_wishlist = [
        {'type': 'wishlist', 'book': w.book, 'date': w.added_at}
        for w in Wishlist.objects.filter(user=user).select_related('book').order_by('-added_at')[:10]
    ]
    activity = sorted(recent_reviews + recent_wishlist, key=lambda x: x['date'], reverse=True)[:10]

    return render(request, 'users/profile.html', {
        'user': user,
        # counts
        'books_read':        books_started,
        'books_finished':    books_finished,
        'wishlist_count':    wishlist_count,
        'reviews_count':     reviews_count,
        # reading stats
        'total_pages_read':  total_pages_read,
        'active_days':       active_days,
        'avg_pages_per_day': avg_pages_per_day,
        'favourite_genre':   favourite_genre,
        # lists
        'in_progress':       in_progress,
        'streak':            streak,
        'activity':          activity,
    })
