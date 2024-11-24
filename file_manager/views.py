from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.permissions import *
from django.http import JsonResponse
from .models import FileModel
from .tasks import process_dataset


class UploadFileView(APIView):

    permission_classes = (IsAuthenticated, IsUserOrAdmin)

    def post(self, request):
        request_file = request.FILES.get('file')

        if not request_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        if request_file.content_type != "text/csv":
            return Response({"error": "Only CSV files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = FileModel.objects.create(user = request.user, file = request_file)

        process_dataset.delay(uploaded_file.id)

        return Response({"message": "File uploaded successfully.", "file_id": uploaded_file.id}, status=status.HTTP_201_CREATED)

    def get(self, request):
        return render(request, 'upload_file.html')
    
class CheckProgressView(APIView):
    def get(self, request, id):
        status = cache.get(f'file_status_{id}')
        if status:
            return JsonResponse({'status': status})
        
        try:
            file = FileModel.objects.only('status').get(id=id)
            cache.set(f'file_status_{id}', file.status, timeout=60)
            return JsonResponse({'status': file.status})
        except FileModel.DoesNotExist:
            return JsonResponse({'error': 'file not found'}, status=404)

