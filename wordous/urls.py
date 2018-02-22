"""
wordous URL Configuration
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('tasks/', include('tasks.urls')),
    path('payment/', include('payment.urls')),
    path('notifications/', include('notifications.urls')),
    path('feedback/', include('feedback.urls')),
    path('admins-only/', admin.site.urls),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
                   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
