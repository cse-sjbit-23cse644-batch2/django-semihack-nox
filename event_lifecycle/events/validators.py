from django.core.exceptions import ValidationError
import os

ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']
MAX_FILE_SIZE_MB = 2


def validate_receipt_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type '{ext}'. Allowed: PDF, PNG, JPG.")
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")
