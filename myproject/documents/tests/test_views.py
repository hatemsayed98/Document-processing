import pytest
import io
import os
import PyPDF2
import base64
from django.test import TestCase
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIRequestFactory
from documents.models import Image, PDF


from documents.serializers import (
    ImageSerializer,
    PDFSerializer,
    ImageSerializerDetailed,
    PDFSerializerDetailed,
)

from documents.views import (
    upload_file,
    rotate_image_view,
    get_all_images,
    get_all_pdfs,
    get_delete_image,
    get_delete_pdf,
    convert_pdf_to_image,
)
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUploadFileView:
    def setup_method(self):
        self.factory = APIRequestFactory()

    def test_upload_image_file(self):
        test_image_path = os.path.join(
            os.path.dirname(__file__), "test_files", "rdi_image_encoded.txt"
        )

        image_content = PILImage.new("RGBA", (173, 117), "white")
        image_io = io.BytesIO()
        image_content.save(image_io, format="PNG")  # Save as PNG

        # Convert the RGBA image to RGB
        rgb_image = image_content.convert("RGB")

        image_file = SimpleUploadedFile(
            "rdi_image_encoded.txt", open(test_image_path, "rb").read(), content_type="image/jpeg"
        )

        data = {"file": image_file, "extension": "png"}
        request = self.factory.post("/upload/", data, format="multipart")
        response = upload_file(request)
        assert response.status_code == status.HTTP_200_OK

        image = Image.objects.last()
        assert image is not None
        assert image.width == 173
        assert image.height == 117
        assert image.number_of_channels == 4  # RGBA


    def test_upload_pdf_file(self):
        test_pdf_path = os.path.join(
            os.path.dirname(__file__), "test_files", "encoded-base64_pdf_2_pages.txt"
        )

        pdf_file_content = open(test_pdf_path, "rb").read()

        pdf_file = SimpleUploadedFile(
            "encoded-base64_pdf_2_pages.txt", pdf_file_content, content_type="application/pdf"
        )

        data = {"file": pdf_file, "extension": "pdf"}
        request = self.factory.post("/upload/", data, format="multipart")
        response = upload_file(request)
        assert response.status_code == status.HTTP_200_OK

        pdf = PDF.objects.last()
        assert pdf is not None


    def test_upload_unmatched_extension_and_file(self):
        invalid_file = SimpleUploadedFile("encoded-base64_pdf_2_pages.txt", b"Test content")
        data = {"file": invalid_file, "extension": "jpg"}
        request = self.factory.post("/upload/", data, format="multipart")
        response = upload_file(request)
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    def test_upload_invalid_file_type(self):
        invalid_file = SimpleUploadedFile("test_text.txt", b"Test content")
        data = {"file": invalid_file, "extension": "txt"}
        request = self.factory.post("/upload/", data, format="multipart")
        response = upload_file(request)
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


@pytest.mark.django_db
class RotateImageViewTestCase:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.image_width = 800
        self.image_height = 631
        self.image = Image.objects.create(
            file=SimpleUploadedFile(
                "speech.jpg",
                b"Test content",
                content_type="image/jpg",
            ),
            width=self.image_width,
            height=self.image_height,
            number_of_channels=4,
        )

    def test_rotate_image_success(self):
        data = {"image_id": self.image.pk, "rotation_angle": 90}
        request = self.factory.post("/rotate/", data, format="json")
        response = rotate_image_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()

    def test_rotate_image_failure_invalid_id(self):
        invalid_image_id = 1000
        data = {"image_id": invalid_image_id, "rotation_angle": 90}
        request = self.factory.post("/rotate/", data, format="json")
        response = rotate_image_view(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rotate_image_failure_invalid_angle(self):
        data = {"image_id": self.image.pk, "rotation_angle": "invalid_angle"}
        request = self.factory.post("/rotate/", data, format="json")
        response = rotate_image_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.image.delete()


@pytest.mark.django_db
class ImageViewsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.image = Image.objects.create(
            file=SimpleUploadedFile(
                "speech.jpg", b"Test content", content_type="image/jpeg"
            ),
            width=800,
            height=631,
            number_of_channels=4,
        )

    def test_get_all_images(self):
        request = self.factory.get("/get_all_images/")
        response = get_all_images(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_image_details_success(self):
        request = self.factory.get(f"/get_delete_image/{self.image.pk}/")
        response = get_delete_image(request, self.image.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_image_details_failure(self):
        invalid_image_id = self.image.pk + 1000
        request = self.factory.get(f"/get_delete_image/{invalid_image_id}/")
        response = get_delete_image(request, invalid_image_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_image_success(self):
        request = self.factory.delete(f"/get_delete_image/{self.image.pk}/")
        response = get_delete_image(request, self.image.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_image_failure(self):
        invalid_image_id = self.image.pk + 1000
        request = self.factory.delete(f"/get_delete_image/{invalid_image_id}/")
        response = get_delete_image(request, invalid_image_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        self.image.delete()


@pytest.mark.django_db
class PDFViewsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.pdf = PDF.objects.create(
            file=SimpleUploadedFile(
                "DRF_revision.pdf", b"Test content", content_type="application/pdf"
            ),
            num_pages=5,
        )

    def test_get_all_pdfs(self):
        request = self.factory.get("/get_all_pdfs/")
        response = get_all_pdfs(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pdf_details_success(self):
        request = self.factory.get(f"/get_delete_pdf/{self.pdf.pk}/")
        response = get_delete_pdf(request, self.pdf.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pdf_details_failure(self):
        invalid_pdf_id = self.pdf.pk + 1000
        request = self.factory.get(f"/get_delete_pdf/{invalid_pdf_id}/")
        response = get_delete_pdf(request, invalid_pdf_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_pdf_success(self):
        request = self.factory.delete(f"/get_delete_pdf/{self.pdf.pk}/")
        response = get_delete_pdf(request, self.pdf.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_pdf_failure(self):
        invalid_pdf_id = self.pdf.pk + 1000
        request = self.factory.delete(f"/get_delete_pdf/{invalid_pdf_id}/")
        response = get_delete_pdf(request, invalid_pdf_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        self.pdf.delete()


@pytest.mark.django_db
class ConvertPDFToImageViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.pdf = PDF.objects.create(
            file=SimpleUploadedFile(
                "Backend Task (Document Processing).pdf",
                b"Sample PDF content",
                content_type="application/pdf",
            ),
            num_pages=2,
        )

    from unittest.mock import patch
    from pdf2image.exceptions import PDFPageCountError

    @patch("pdf2image.pdf2image.pdfinfo_from_path")
    def test_convert_pdf_to_image_success(self, mock_pdfinfo_from_path):
        # Mock the pdfinfo_from_path function to return a dictionary
        mock_pdfinfo_from_path.return_value = {"Pages": 2}

        data = {"pdf_id": self.pdf.pk}
        request = self.factory.post("/convert/", data, format="json")
        response = convert_pdf_to_image(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_convert_pdf_to_image_failure_pdf_not_found(self):
        data = {"pdf_id": 999}  # Non-existing PDF ID
        request = self.factory.post("/convert/", data, format="json")
        response = convert_pdf_to_image(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_convert_pdf_to_image_failure_missing_pdf_id(self):
        data = {}
        request = self.factory.post("/convert/", data, format="json")
        response = convert_pdf_to_image(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        Image.objects.all().delete()
