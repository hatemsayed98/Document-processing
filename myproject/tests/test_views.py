import pytest
from rest_framework import status
# from rest_framework.test import APIClient
# from documents.models import Image, PDF
import io
from PIL import Image
import pytest


@pytest.mark.django_db
def test_upload_file_with_pdf():
    client = APIClient()
    file_path = '/path/to/your/test.pdf'  # Replace with the path to your test PDF file

    with open(file_path, 'rb') as file:
        data = {'file': file}
        response = client.post('/upload_file/', data, format='multipart')

    assert response.status_code == status.HTTP_200_OK
    assert 'document_id' in response.data


@pytest.mark.django_db
def test_upload_file():
    assert 1 == 1
    print("hi")

# @pytest.mark.django_db
# def test_get_all_images():
#     pass

# @pytest.mark.django_db
# def test_get_all_pdfs():
#     pass

# import io
# from PIL import Image
# import pytest
# from rest_framework import status
# from rest_framework.test import APIClient
# from django.core.files.uploadedfile import SimpleUploadedFile

# @pytest.mark.django_db
# def test_upload_file_with_pdf():
#     client = APIClient()
#     file_path = '/path/to/your/test.pdf'  # Replace with the path to your test PDF file

#     with open(file_path, 'rb') as file:
#         data = {'file': file}
#         response = client.post('/upload_file/', data, format='multipart')

#     assert response.status_code == status.HTTP_200_OK
#     assert 'document_id' in response.data

# @pytest.mark.django_db
# def test_upload_file_with_image():
#     client = APIClient()
#     file_path = '/path/to/your/test.jpg'  # Replace with the path to your test image file

#     with open(file_path, 'rb') as file:
#         data = {'file': file}
#         response = client.post('/upload_file/', data, format='multipart')

#     assert response.status_code == status.HTTP_200_OK
#     assert 'document_id' in response.data

# @pytest.mark.django_db
# def test_upload_file_with_invalid_file():
#     client = APIClient()
#     file_path = '/path/to/your/test.txt'  # Replace with the path to your test non-supported file

#     with open(file_path, 'rb') as file:
#         data = {'file': file}
#         response = client.post('/upload_file/', data, format='multipart')

#     assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

# @pytest.mark.django_db
# def test_upload_file_with_invalid_request_method():
#     client = APIClient()
#     response = client.get('/upload_file/')

#     assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED