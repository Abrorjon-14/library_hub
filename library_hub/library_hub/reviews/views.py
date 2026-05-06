from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from books.models import Book
from .models import Review, ReviewLike
from .forms import ReviewForm


def review_list(request, book_id):
    """Reviews are shown inline on book_detail — this is a fallback redirect."""
    return redirect('book_detail', pk=book_id)


@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if Review.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, 'You have already reviewed this book.')
        return redirect('book_detail', pk=book_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Your review has been posted!')
            return redirect('book_detail', pk=book_id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {
        'form': form, 'book': book, 'action': 'Add'
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated!')
            return redirect('book_detail', pk=review.book.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/review_form.html', {
        'form': form, 'book': review.book, 'action': 'Edit'
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    book_id = review.book.pk
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted.')
    return redirect('book_detail', pk=book_id)


@login_required
def toggle_like(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    like = ReviewLike.objects.filter(user=request.user, review=review)
    if like.exists():
        like.delete()
    else:
        ReviewLike.objects.create(user=request.user, review=review)
    return redirect('book_detail', pk=review.book.pk)
