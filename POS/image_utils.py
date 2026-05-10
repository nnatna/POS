from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError


def convert_uploaded_image_to_png(uploaded_file, output_name):
    try:
        uploaded_file.seek(0)
    except (AttributeError, OSError):
        pass

    try:
        with Image.open(uploaded_file) as image:
            has_alpha = image.mode in ('RGBA', 'LA') or (
                image.mode == 'P' and 'transparency' in image.info
            )
            converted_image = image.convert('RGBA' if has_alpha else 'RGB')

            buffer = BytesIO()
            converted_image.save(buffer, format='PNG')
            return ContentFile(buffer.getvalue(), name=output_name)
    except UnidentifiedImageError as exc:
        raise ValueError('Upload a valid image file.') from exc
