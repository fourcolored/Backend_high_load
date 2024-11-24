from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.middleware.csrf import get_token
from django.core.cache import cache

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .forms import EmailForm, ProductForm, CustomUserCreationForm
from .tasks import send_email_task
from .models import OTP, Product, Email
from .utils import send_2fa_otp
from .throttles import AdminThrottle, RegularUserThrottle
from .jwt import generate_jwt
from config.permissions import *
from tasks import serializers


class EmailView(APIView):
    """
    {
        "recipient": "example@example.com",
        "subject": "Test Email",
        "body": "This is a test email body."
    }

    """
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        permissions = super().get_permissions()
        permissions.append(IsAuthenticated())

        if self.request.method == 'POST':
            permissions.append(IsUserOrAdmin())
        elif self.request.method == 'DELETE':
            permissions.append(IsAdmin())
        elif self.request.method == 'GET':
            permissions.append(IsUserOrAdmin())

        return permissions
    
    def get_throttles(self):
        if self.request.user.is_staff:
            return [AdminThrottle()]
        else:
            return [RegularUserThrottle()] 

    def post(self, request):
        form = EmailForm(request.data)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            recipient = form.cleaned_data['recipient']
            body = form.cleaned_data['body']
            send_email_task.delay(recipient, subject, body, request.user.id)
            return Response({"message": "Email is being sent in the background!"}, status=200)
    
        return Response({"message": "Email is not sent, invalid form."}, status=400)
    
    def get(self, request):
        emails = Email.objects.filter(user=request.user)
        serializer = serializers.EmailSerializer(emails, many=True)
        return Response(serializer.data, status=200)


class RegisterView(APIView):
    """
    {
        "username": "user",
        "email": "example@example.com",
        "password1": "p4ssword123",
        "password2": "p4ssword123"
    }

    """
    permission_classes = (AllowAny,)

    def post(self, request):
        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user = form.save()
            user_group, _ = Group.objects.get_or_create(name='User')
            user.groups.add(user_group)

            return redirect('tasks:login')
        
        return Response({"message": "Error unable to register"},status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.COOKIES.get('jwt_token'):
            return Response({"message": "User already logged in"}, status=status.HTTP_200_OK)
        return Response({"message": "Provide POST data to register a user."}, status=status.HTTP_200_OK)
        

class LoginView(APIView):
    """
    {
        "username":"user",
        "password":"p4ssword123"
    }
    """
    permission_classes = (AllowAny, )

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(
            username=username, password=password)
        if user is None:
            return Response({"Error": "User is None"}, status=status.HTTP_401_UNAUTHORIZED)

        # request.session['temp_user_id'] = user.id
        otp_code = send_2fa_otp(user)
        
        response = Response({"code": otp_code}, status=status.HTTP_200_OK)

        csrf_token = get_token(request)
        response.set_cookie("csrftoken", csrf_token, httponly=True, secure=True)  
        response.set_cookie("temp_user_id", user.id, httponly=True, secure=True, max_age=2 * 60)

        return response
    
    def get(self, request):
        if request.COOKIES.get('jwt_token'):
            return redirect('tasks:logout')
            # Response({"message": "User already logged in"}, status=status.HTTP_200_OK)
        
        csrf_token = get_token(request)
        response = Response({"message": "Provide POST data to login"})
        response.set_cookie("csrftoken", csrf_token, httponly=True, secure=True)
        response["X-CSRFToken"] = csrf_token
        return response

class TwoFactorView(APIView):
    def post(self, request):
        otp_code = request.data.get('code')
        user_id = request.COOKIES.get('temp_user_id')

        if request.COOKIES.get('jwt_token'):
            return Response({"message": "user already logged in"})
        
        if not user_id:
            return Response({"message": "User not logged in or cookie expired."}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.get(id=user_id)
        otp_model = OTP.objects.get(user=user)  
        
        if otp_model.is_valid(otp_code):
            login(request, user)

            otp_model.delete()

            token = generate_jwt(user)

            response = Response({"message": "Redirecting to email page..."}, status=status.HTTP_302_FOUND)
            response.set_cookie("jwt_token", token, httponly=True, secure=True) 
            response.delete_cookie("temp_user_id")
            return response
        
        return Response({"message": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        user_id = request.COOKIES.get('temp_user_id', False)
        token = request.COOKIES.get('jwt_token', False)
        if token:
            return redirect('tasks:send_email')
        if not user_id:
            return Response({"message": "User not logged in or cookie expired."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": user_id}, status=status.HTTP_200_OK)

def logout_view(request):
    logout(request)
    response = redirect('tasks:login')
    response.delete_cookie('jwt_token')
    response.delete_cookie('temp_user_id')
    return response

class ProductView(APIView):
    
    def get_permissions(self):
        permissions = super().get_permissions()
        permissions.append(IsAuthenticated())

        if self.request.method == 'POST':
            permissions.append(IsUserOrAdmin())
        elif self.request.method == 'DELETE':
            permissions.append(IsAdmin())
        elif self.request.method == 'GET':
            permissions.append(IsUserOrAdmin())

        return permissions


    def post(self, request):
        form = ProductForm(request.data)
        if form.is_valid():
            form.save()
            return redirect('tasks:secure_product')
    
        return render(request, 'secure_form.html', {'form': form})

    def get(self, request):
        form = ProductForm()

        products = cache.get('products')
        
        if not products:
            product_model = Product.objects.all()
            products = serializers.ProductSerializer(product_model, many=True).data
            cache.set('products', products, timeout=5 * 60)

        if "text/html" in request.headers.get("Accept", ""):
            return render(request, "secure_form.html", {"form": form, "products":products})

        return Response(products, status=status.HTTP_200_OK)