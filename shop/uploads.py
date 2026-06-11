"""Shared validation for user-uploaded images."""
from PIL import Image

# Cloudinary's free plan rejects files over 10MB
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}


def validate_image_upload(uploaded_file):
    """Return an error message if the file isn't an acceptable image, else None."""
    if uploaded_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return f'"{uploaded_file.name}" is too large (max {MAX_UPLOAD_SIZE_MB}MB).'

    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        return f'"{uploaded_file.name}" is not a supported image type (use JPEG, PNG, GIF, or WebP).'

    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
    except Exception:
        return f'"{uploaded_file.name}" could not be read as an image. Try re-exporting it.'

    return None
