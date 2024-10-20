from django.db import models
# from django.contrib.auth.models import User
# from users.models import Customer, Seller
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    class Meta:
        indexes = [
            models.Index(fields=['name', 'price', 'category']),
        ]

    def __str__(self):
        return self.name
    

class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)

    def add_product(self, product, quantity):
        cart_item, ok = CartItem.objects.get_or_create(cart=self, product=product)
        if not ok:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    
    def delete_product(self, product):
        cart_item = CartItem.objects.filter(cart=self, product=product).first()
        if cart_item:
            cart_item.delete()
            self.update_price()
    
    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')  
    quantity = models.IntegerField(default=1)


    class Meta:
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_date']),
        ]

    def __str__(self) -> str:
        return str(self.id)

    def update_status(self):
        self.status = True
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    

# class Wallet(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     balance = models.IntegerField()

#     def update_balance(self, amount):
#         self.balance -= amount
#         self.save()
