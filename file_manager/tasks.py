from django.core.cache import cache
from celery import shared_task
from .models import FileModel
import csv
# import pyclamd

import logging
logger = logging.getLogger(__name__)

@shared_task
def process_dataset(file_id):
    upload = FileModel.objects.get(id=file_id)

    try:
        with open(upload.file.path, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
        
        # scan_file_for_malware(upload.file.path)

        if is_csv_empty(data):
            raise ValueError("CSV file is empty.")
        
        
        if not is_safe_csv(data):
            raise ValueError("CSV contains dangerous characters.")


        upload.status = 'COMPLETED'
        upload.save()
        cache.set(f'file_status_{file_id}', 'COMPLETED', timeout=300)

        logger.info(f"Completed validating file {file_id}")

    except Exception as e:
        print(f"Error validating file {file_id}: {str(e)}")
        logger.error(f"Error validating file {file_id}: {str(e)}")
        upload.status = "FAILED"
        upload.save()


def is_safe_csv(data):
    for row in data:
        for cell in row:
            if cell.startswith(('=', '@')):
                return False
    return True

def is_csv_empty(data):
    return not any(row for row in data)

# def scan_file_for_malware(file_path):
#     clamav = pyclamd.ClamdUnixSocket(host='127.0.0.1', port=3310)
#     if clamav.ping():
#         result = clamav.scan_file(file_path)
#         if result:
#             raise ValueError("File contains malware.")


