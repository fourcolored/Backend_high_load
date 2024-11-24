from django import forms
from django.core.exceptions import ValidationError
import magic

def validate_file_type(file):
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in ['image/jpeg', 'image/png']:
        raise ValidationError('Unsupported file type.')

class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_type])