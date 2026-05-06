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
    from reading.models import ReadingProgress, Wishlist
    from reviews.models import Review

    user = request.user
    books_read = ReadingProgress.objects.filter(user=user).count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    reviews_count = Review.objects.filter(user=user).count()
    in_progress = ReadingProgress.objects.filter(user=user).select_related('book')[:3]

    # Build recent activity: merge reviews + wishlist entries, sort by date, take latest 10
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
        'books_read': books_read,
        'wishlist_count': wishlist_count,
        'reviews_count': reviews_count,
        'in_progress': in_progress,
        'activity': activity,
    })
