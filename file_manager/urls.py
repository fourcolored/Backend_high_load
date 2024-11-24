from django.urls import path
from .views import *

app_name = 'file_manager'

urlpatterns = [
    path('upload_file/', UploadFileView.as_view(), name='upload_file'),
    path('progress/<int:id>/', CheckProgressView.as_view(), name='file_progress'),
]