from django.urls import path, reverse_lazy
import django.contrib.auth.views as auth_views
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/',
         auth_views.LoginView.as_view(redirect_authenticated_user=True),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('accounts:password_change_done')
         ), name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy('accounts:password_reset_done')
         ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('accounts:password_reset_complete')
         ), name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('account-activation/', views.AccountActivationView.as_view(),
         name='account_activation_sent'),
    path('account-activation/confirm/<uidb64>/<token>/',
         views.AccountActivationConfirmView.as_view(),
         name='account_activation_confirm'),
    path('detail/<int:pk>/', views.ExecutorDetailView.as_view(),
         name='executor_detail'),
    path('edit/', views.EditInfoView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(),
         name='delete'),
    path('ajax/validate_username/', views.validate_username,
         name='validate_username'),
    path('ajax/validate_email/', views.validate_email,
         name='validate_email'),
    path('<str:status>/', views.DashboardView.as_view(), name='dashboard'),
    path('', views.DashboardView.as_view(), name='dashboard'),
]
