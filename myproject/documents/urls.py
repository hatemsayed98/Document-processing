# # documents/urls.py

# from django.urls import path
# from . import views

# app_name = 'documents'

# urlpatterns = [
#     path('upload/image/', views.upload_image, name='upload_image'),
#     path('upload/pdf/', views.upload_pdf),
#     path('images/', views.get_all_images, name='get_all_images'),
#     path('pdfs/', views.get_all_pdfs, name='get_all_pdfs'),
#     path('images/<int:id>/', views.get_image_details, name='get_image_details'),
#     path('pdfs/<int:id>/', views.get_pdf_details, name='get_pdf_details'),
#     path('images/<int:id>/delete/', views.delete_image, name='delete_image'),
#     path('pdfs/<int:id>/delete/', views.delete_pdf, name='delete_pdf'),
# ]

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
    

]