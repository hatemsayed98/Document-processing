



# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import FilesViewSet

# router = DefaultRouter()
# router.register('upload', FilesViewSet, basename='upload')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('images/', get_all_images, name='get_all_images'),
    path('pdfs/', get_all_pdfs, name='get_all_pdfs'),
    path('images/<int:id>/', get_image_details, name='get_image_details'),
    path('pdfs/<int:id>/', get_pdf_details, name='get_pdf_details'),

]