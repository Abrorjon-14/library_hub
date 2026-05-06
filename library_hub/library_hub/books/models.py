from django.db import models


class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Badiiy'),
        ('non_fiction', 'Publitsistika'),
        ('science', 'Ilmiy'),
        ('history', 'Tarix'),
        ('biography', 'Biografiya'),
        ('fantasy', 'Fantastika'),
        ('mystery', 'Detektiv'),
        ('romance', 'Romantik'),
        ('thriller', 'Triller'),
        ('other', 'Boshqa'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='other')
    total_pages = models.PositiveIntegerField(default=0, help_text="Total number of pages (0 = unknown)")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author}"
