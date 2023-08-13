from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('images/', get_all_images, name='get_all_images'),
    path('pdfs/', get_all_pdfs, name='get_all_pdfs'),
    path('images/<int:id>/', get_delete_image),
    path('pdfs/<int:id>/', get_delete_pdf),
    path('rotate/', rotate_image_view),
    path('convert-pdf-to-image/', convert_pdf_to_image),
]