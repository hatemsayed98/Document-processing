# Django Imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from PIL import Image as PILImage
import io

# User Imports
from .models import Image, PDF
from .serializers import ImageSerializer, PDFSerializer


@api_view(["POST"])
def upload_file(request):
    if request.method == "POST":
        encoded_file = request.data.get("file")
        file_extension = encoded_file.name.split(".")[-1]
        file_extension = file_extension.lower()
        form = None
        if file_extension == "pdf":
            form = PDFSerializer(data=request.data)

        elif file_extension in ["jpg", "jpeg", "png", "gif"]:
            form = ImageSerializer(data=request.data)
        else:
            return JsonResponse({"error": "Unsupported Media Type"}, status=415)
        if form.is_valid():
            document = form.save()
            return JsonResponse(
                {"message": "File uploaded successfully", "document_id": document.pk},
                status=200,
            )
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@api_view(["GET"])
def get_all_images(request):
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_all_pdfs(request):
    pdfs = PDF.objects.all()
    serializer = PDFSerializer(pdfs, many=True)
    return Response(serializer.data)


@api_view(["GET", "DELETE"])
def get_delete_image(request, id):
    image = Image.objects.get(id=id)
    if request.method == "DELETE":
        try:
            image.file.delete()
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == "GET":
        try:
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_delete_pdf(request, id):
    pdf = PDF.objects.get(id=id)
    if request.method == "DELETE":
        try:
            pdf.file.delete()
            pdf.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PDF.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == "GET":
        try:
            serializer = PDFSerializer(image)
            return Response(serializer.data)
        except PDF.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def rotate_image_view(request):
    image_id = request.data.get("image_id")
    rotation_angle = request.data.get("rotation_angle")

    try:
        myModel = Image.objects.get(id=image_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        rotation_angle = int(rotation_angle)
    except ValueError:
        return JsonResponse(
            {"error": "Invalid rotation angle"}, status=status.HTTP_400_BAD_REQUEST
        )

    photo_new = io.BytesIO(myModel.file.read())
    image = PILImage.open(photo_new)
    image = image.rotate(rotation_angle)

    image_file = io.BytesIO()
    image.save(image_file, "JPEG")

    with open(myModel.file.path, "wb") as f:
        f.write(image_file.getvalue())

    return JsonResponse(
        {"message": "Image rotated successfully"}, status=status.HTTP_200_OK
    )


from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import os
poppler_path = r'C:\\Program Files\\poppler-23.08.0\\Library\\bin'  # Replace with the correct path to your Poppler bin directory
os.environ['PATH'] += os.pathsep + poppler_path


@api_view(['POST'])
def convert_pdf_to_image(request):
    pdf_id = request.data.get("pdf_id")
    try:
        pdf = PDF.objects.get(id=pdf_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND)

    images = convert_from_path(pdf.file.path)  # Convert PDF to images
    for i, image in enumerate(images):
        image_dir = 'images/'
        os.makedirs(image_dir, exist_ok=True)  # Create the 'images' directory if it doesn't exist
        pdf_name = os.path.basename(pdf.file.name)  # Extract the PDF file name
        image_path = os.path.join(image_dir, f"{pdf_name}_page{i+1}.jpg")

        image.save(image_path, 'JPEG')
        Image.objects.create(file=image_path, uploaded_at=pdf.uploaded_at)

    pdf.file.delete()  # Delete the original PDF file
    pdf.delete()  # Delete the PDF object

    return JsonResponse({"message": "PDF converted to image(s) successfully"}, status=status.HTTP_200_OK)