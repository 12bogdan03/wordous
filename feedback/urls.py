from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path('send/', views.SendFeedbackView.as_view(),
         name='send_feedback'),
]
