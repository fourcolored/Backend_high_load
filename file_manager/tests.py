from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from threading import Thread

from .models import FileModel

class FileUploadTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='p4ssword123')
        user_group, _ = Group.objects.get_or_create(name='User')
        self.user.groups.add(user_group)

        login_response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'p4ssword123',
        })
        otp_code = login_response.json().get('code')
        otp_response = self.client.post('/otp-auth/', {'code': otp_code}, cookies=login_response.cookies)
        self.jwt_token = otp_response.cookies.get('jwt_token') 

    def test_file_upload_valid(self):
        self.client.cookies['jwt_token'] = self.jwt_token
        file = SimpleUploadedFile("test.csv", b"data,data", content_type="text/csv")
        response = self.client.post('/file/upload_file/', {'file': file})
        self.assertEqual(response.status_code, 201)

    def test_invalid_file_type(self):
        self.client.cookies['jwt_token'] = self.jwt_token
        file = SimpleUploadedFile("test.txt", b"data", content_type="text/plain")
        response = self.client.post('/file/upload_file/', {'file': file})
        self.assertEqual(response.status_code, 400)

    