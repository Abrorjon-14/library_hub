from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from datetime import datetime


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Xayrli tong ☀️"
    elif hour < 18:
        return "Xayrli kun 🌤"
    else:
        return "Xayrli kech 🌙"


def home_view(request):
    feats = [
        ('📖', "Kitoblarni ko'rish", "Keng to'plamimizni o'rganing"),
        ('📄', 'Jarayonni kuzating', 'Sahifangizni istalgan vaqt saqlang'),
        ('❤️', "Xohishlar ro'yxati", "O'qimoqchi bo'lgan kitoblarni saqlang"),
        ('⭐', 'Sharh yozing', "O'qish taassurotlaringizni ulashing"),
    ]
    continue_reading = None
    if request.user.is_authenticated:
        from reading.models import ReadingProgress
        continue_reading = (
            ReadingProgress.objects
            .filter(user=request.user)
            .select_related('book')
            .order_by('-updated_at')
            .first()
        )
    return render(request, 'home.html', {
        'feats': feats,
        'continue_reading': continue_reading,
        'greeting': get_greeting(),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('books/', include('books.urls')),
    path('reading/', include('reading.urls')),
    path('reviews/', include('reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
