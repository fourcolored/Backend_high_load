from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.get_post_list, name='post_list'),
    # path('index/', views.index, name='index'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/comment/', views.create_comment, name='comment_post'),
    path('add/', views.create_post, name='create_post'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]