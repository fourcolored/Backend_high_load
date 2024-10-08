from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.get_posts, name='post_list'),
    path('<int:post_id>/', views.get_post_detail, name='post_detail'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
]