from django.db import models
from django.contrib.auth.models import User
from books.models import Book


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='readers')
    current_page = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} – {self.book.title} (p.{self.current_page})"

    @property
    def percent_complete(self):
        """Return reading percentage (0–100). Returns 0 if total_pages unknown."""
        if self.book.total_pages and self.book.total_pages > 0:
            pct = int((self.current_page / self.book.total_pages) * 100)
            return min(pct, 100)
        return 0


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} → {self.book.title}"


class ReadingStreak(models.Model):
    """Tracks the user's daily reading streak."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} – {self.current_streak} day streak"


def update_streak(user):
    """
    Call this whenever a user saves reading progress.
    - Same day  → no change (already counted today)
    - Yesterday → increment streak
    - Older     → reset streak to 1
    """
    from django.utils import timezone
    today = timezone.localdate()

    streak, _ = ReadingStreak.objects.get_or_create(user=user)
    last = streak.last_activity_date

    if last == today:
        return  # already updated today
    elif last is not None and (today - last).days == 1:
        streak.current_streak += 1
    else:
        streak.current_streak = 1  # missed a day (or first time)

    streak.last_activity_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.save()


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.book.title}"
