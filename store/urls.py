from django.urls import path
from  .cbviews import *

urlpatterns = [
    path('products/', ProductListView.as_view()), # product list
    path('products/<int:id>/', ProductDetailView.as_view()), #product detail

    path('categories/', CategoryListView.as_view()),
    path('categories/<int:id>/', CategoryDetailView.as_view()),

    # login required
    path('user/cart/', ShoppingCartView.as_view()), # shopping cart of the user
    path('user/orders/', OrderListView.as_view()),
    path('user/orders/<int:id>/', OrderDetailView.as_view()),
    # path('user/wallet/', WalletView.as_view()),
]