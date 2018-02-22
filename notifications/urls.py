from django.urls import path

from . import views

app_name = 'notifications'
urlpatterns = [
    path('ajax/notifications/', views.NewNotificationsView.as_view(),
         name='ajax_notifications'),
    path('', views.NotificationListView.as_view(), name='notification_list'),
]
