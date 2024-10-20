from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from store import serializers
from store.models import *

from django.core.cache import cache

from .tasks import send_purchase_result

class CategoryListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        category = Category.objects.all()
        serializer = serializers.CategorySerializer(category, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    permission_classes = (AllowAny,)
    def get_object(self, id):
        try:
            category = Category.objects.get(pk=id)
            return category
        except category.DoesNotExist as e:
            return Response(str(e), status=status.HTTP_404_BAD_REQUEST)

    def get(self, request, id, format=None):
        instance = self.get_object(id)
        serializer = serializers.CategorySerializer(instance)
        products = instance.products.all()
        products_serializer = serializers.ProductSerializer(products, many=True)
        return Response({
            "cat": serializer.data,
            "products": products_serializer.data,
        })
  
class OrderListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = serializers.OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Check if the shopping_cart has items in it
        If it does save all of them in order_item -> order
        clear the cart
        """
        
        cart = ShoppingCartView.get_cart(request)
        if not cart.items.exists():
            return Response({"Error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order(user=request.user)
        order.save()

        cart_items = cart.items.prefetch_related('product')

        total_price = 0
        order_items = []

        for item in cart_items:
            order_item = OrderItem(order=order, product=item.product, quantity=item.quantity)
            order_items.append(order_item)
            total_price += item.product.price * item.quantity

        OrderItem.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save()
        
        user = request.user

        balance = user.balance
        if balance < order.total_price:
            return Response({"Error": "Balance is low"})
        
        user.update_balance(order.total_price)

        cart.items.all().delete()
        order.update_status()

        # send_purchase_result.delay(order.id)

        serializer = serializers.OrderSerializer(order)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, id):
        try:
            order = Order.objects.get(pk=id)
            if order.user != self.request.user:
                raise PermissionDenied
            return order
        except Order.DoesNotExist as e:
            return Response(str(e), status=status.HTTP_404_BAD_REQUEST)

    def get(self, request, id, format=None):
        instance = self.get_object(id)
        serializer = serializers.OrderSerializer(instance)
        return Response(serializer.data)

class ShoppingCartView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get_cart(request):
        try:
            cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            return ShoppingCart.objects.create(user=request.user)
        return cart
    
    def get_cart_items(self, cart):
        cart_items = cart.items.all()
        return serializers.CartItemSerializer(cart_items, many=True)

    def get(self, request):
        cart = self.get_cart(request)
        if cart is None:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ShoppingCartSerializer(cart)
        return Response({
            "cart_info": serializer.data,
            "cart_list": self.get_cart_items(cart).data
            })
    
    def put(self, request):
        # modify the cart by adding items   
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        cart = ShoppingCart.objects.get(user=request.user)
        
        cart.add_product(product, quantity)

        return Response({"Message": "Added successfully"}, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        # delete cart_item
        cart_item = CartItem.objects.get(id=id)
        cart_item.delete()
        return Response({'message': 'deleted item in shopping cart'})
        

class ProductListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        products = cache.get('products')
        
        if not products:
            products = Product.objects.select_related('category').all()
            serializer = serializers.ProductSerializer(products, many=True)
            cache.set('products', serializer.data, timeout=2 * 60)
        else:
            return Response(products)
        
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except product.DoesNotExist as e:
            return Response(str(e), status=status.HTTP_404_BAD_REQUEST)
        
        serializer = serializers.ProductSerializer(product)
        return Response(serializer.data)


# class WalletView(APIView):
#     permission_classes = (IsAuthenticated, )

#     @staticmethod
#     def check_wallet(request):
#         wallet = Wallet.objects.get(user=request.user)
#         return wallet
        
#     def post(self, request):
#         # create wallet for user
#         wallet = Wallet.objects.create(user=request.user, balance=request.data.get('balance'))
#         serializer = serializers.WalletSerializer(wallet)
        
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     def get(self, request):
#         instance = self.check_wallet(request)
#         if instance is None:
#             return Response({"Error": "Wallet does not exists"}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = serializers.WalletSerializer(instance)
#         return Response({"wallet": serializer.data})