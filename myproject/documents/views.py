# Django Imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image as PILImage
import io
import os
from PIL import Image as PILImage
from PyPDF2 import PdfReader
import PyPDF2
from pdf2image import convert_from_path

# User Imports
from .models import Image, PDF
from .serializers import (
    ImageSerializer,
    ImageSerializerDetailed,
    PDFSerializer,
    PDFSerializerDetailed,
)
from .utils import get_num_pdf_pages, is_pdf, is_image


# Views here

@api_view(["POST"])
def upload_file(request):
    if request.method == "POST":
        encoded_file = request.FILES["file"]
        file_extension = encoded_file.name.split(".")[-1].lower()
        form = None

        if is_pdf(file_extension):
            num_pages = get_num_pdf_pages(encoded_file)
            print(num_pages)
            form = PDFSerializerDetailed(
                data={
                    "file": encoded_file,
                    "num_pages": num_pages,
                }
            )
        elif is_image(file_extension):
            form = ImageSerializer(data={"file": encoded_file})
        else:
            return Response(
                {"error": "Unsupported Media Type"},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        if form.is_valid():
            document = form.save()

            if is_pdf(file_extension):
                with open(document.file.path, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    page = pdf_reader.pages[
                        0
                    ]  # Assuming you want dimensions of the first page
                    page_width = page.mediabox[2] - page.mediabox[0]
                    page_height = page.mediabox[3] - page.mediabox[1]

                # Update the PDF model instance with calculated values
                document.page_width = page_width
                document.page_height = page_height
                document.save()

            elif is_image(file_extension):
                # Open the image using PIL
                with PILImage.open(document.file.path) as image:
                    width, height = image.size
                    number_of_channels = len(image.getbands())

                # Update the image model instance with calculated values
                document.width = width
                document.height = height
                document.number_of_channels = number_of_channels
                document.save()

            return Response(
                {"message": "File uploaded successfully", "document_id": document.pk},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"error": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@api_view(["GET"])
def get_all_images(request):
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
def get_all_pdfs(request):
    pdfs = PDF.objects.all()
    serializer = PDFSerializer(pdfs, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET", "DELETE"])
def get_delete_image(request, id):
    try:
        image = Image.objects.get(id=id)
    except:
        return JsonResponse(
            {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
        )
    if request.method == "GET":
        try:
            serializer = ImageSerializerDetailed(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == "DELETE":
        try:
            image.file.delete()
            image.delete()
            return JsonResponse(
                {"message": "Image Deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except Image.DoesNotExist:
            return JsonResponse(
                {"error": "Image does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET", "DELETE"])
def get_delete_pdf(request, id):
    try:
        pdf = PDF.objects.get(id=id)
    except:
        return JsonResponse(
            {"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND
        )
    if request.method == "GET":
        try:
            serializer = PDFSerializerDetailed(pdf)
            return Response(serializer.data)
        except PDF.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == "DELETE":
        try:
            pdf.file.delete()
            pdf.delete()
            return JsonResponse(
                {"message": "PDF Deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except PDF.DoesNotExist:
            return JsonResponse(
                {"error": "PDF does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


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
    rotated_image = image.rotate(
        rotation_angle, expand=True
    )  # Allow the image to expand when rotating

    # Check if the rotated image dimensions exceed the defined dimensions
    if myModel.width is not None and myModel.height is not None:
        if rotated_image.width > myModel.width or rotated_image.height > myModel.height:
            rotated_image.thumbnail((myModel.width, myModel.height))


    rotated_image_io = io.BytesIO()
    rotated_image.save(rotated_image_io, format="JPEG")

    # Overwrite the existing image file with the rotated image data
    with open(myModel.file.path, "wb") as f:
        f.write(rotated_image_io.getvalue())

    rotated_image_url = myModel.file.url

    return JsonResponse(
        {
            "message": "Image rotated and resized if necessary",
            "rotated_image_url": rotated_image_url,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def convert_pdf_to_image(request):
    pdf_id = request.data.get("pdf_id")
    try:
        pdf = PDF.objects.get(id=pdf_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND
        )

    images = convert_from_path(pdf.file.path)  # Convert PDF to images
    generated_image_paths = []

    for i, image in enumerate(images):
        image_dir = "images/"
        os.makedirs(
            image_dir, exist_ok=True
        )  # Create the 'images' directory if it doesn't exist
        pdf_name = os.path.basename(pdf.file.name)  # Extract the PDF file name
        image_path = os.path.join(image_dir, f"{pdf_name}_page{i+1}.jpg")

        image.save("media/" + image_path, "JPEG")
        Image.objects.create(file=image_path, uploaded_at=pdf.uploaded_at)
        generated_image_paths.append(
            "/media/" + image_path
        )  # Add the generated image path to the list

    pdf.file.delete()  # Delete the original PDF file
    pdf.delete()  # Delete the PDF object

    return JsonResponse(
        {
            "message": "PDF converted to image(s) successfully",
            "image_paths": generated_image_paths,
        },
        status=status.HTTP_200_OK,
    )
