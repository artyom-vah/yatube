from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path('password_change/', PasswordChangeView.as_view(
         template_name='users/password_change_form.html'),
         name='password_change'),

    path('password_change/done/', PasswordChangeDoneView.as_view(
         template_name='users/password_change_done.html'),
         name='password_change/done/'),

    path('password_reset', PasswordResetView.as_view(
         template_name='users/password_reset_form.html')),

    path('password_reset/done', PasswordResetDoneView.as_view(
         template_name='users/password_reset_done.html')),

    path('auth/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html')),

    path('auth/reset/done', PasswordResetCompleteView.as_view(
         template_name='users/password_reset_complete.html')),
]
