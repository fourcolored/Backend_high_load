from django.urls import path
from .views import *

app_name = 'tasks'

urlpatterns = [
    path('send-email/', EmailView.as_view(), name='send_email'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('otp-auth/', TwoFactorView.as_view(), name='otp_auth'),
    path('secure_product/', ProductView.as_view(), name='secure_product')
]
