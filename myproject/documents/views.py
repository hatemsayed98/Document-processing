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
import base64
import fitz
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

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
    # Check HTTP Request
    if request.method != "POST":
        return JsonResponse(
            {"error": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Read data from frontend
    encoded_file_data = request.data.get("file")
    file_extension = request.data.get("extension", "").lower()

    try:
        filename = encoded_file_data.name.split(".txt")[0]
    except AttributeError:
        filename = "uploaded_file"

    # Exception handle bad body data
    if not encoded_file_data or not file_extension:
        error_message = "Missing file data or invalid extension"
        return Response(
            {"error": error_message},
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    # Decode the incomming Base64 file
    try:
        encoded_file_content = encoded_file_data.read()
        decoded_file_data = base64.b64decode(encoded_file_content)
    except:
        return Response(
            {"error": "Invalid base64 file"},
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    serialized_data = None
    # Serialize the data with PDF Serializer
    if is_pdf(file_extension):
        # Wrap the decoded bytes in a BytesIO object
        pdf_io = io.BytesIO(decoded_file_data)
        num_pages = get_num_pdf_pages(pdf_io)
        serialized_data = PDFSerializerDetailed(
            data={
                "file": ContentFile(
                    decoded_file_data, name=f"{filename}.{file_extension}"
                ),
                "num_pages": num_pages,
            }
        )
    # Serialize the data with Image Serializer
    elif is_image(file_extension):
        serialized_data = ImageSerializer(
            data={
                "file": ContentFile(
                    decoded_file_data, name=f"{filename}.{file_extension}"
                )
            }
        )
    # Exception not Image or PDF
    else:
        return Response(
            {"error": "Unsupported Media Type"},
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    # Save the serialized data if valid, and Add attributes neccessary after saving
    try:
        if serialized_data.is_valid():
            document = serialized_data.save()

            # Check if it is pdf, save in PDF table and calculate the PDF page height, width
            if is_pdf(file_extension):
                pdf_document = fitz.open(stream=decoded_file_data, filetype="pdf")
                page = pdf_document[0]  # First page
                page_width = page.bound().width
                page_height = page.bound().height
                pdf_document.close()

                # Update the PDF model instance with calculated values
                document.page_width = page_width
                document.page_height = page_height
                document.save()

            # Check if it is Image, save the Image instance and update its page height, width
            elif is_image(file_extension):
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
        # Error in serialized_data
        else:
            return JsonResponse(
                {"error": serialized_data.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    # Error in file formate
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
    # Get image instance from ID
    image = get_object_or_404(Image, id=id)

    # Return detailed image by ID
    if request.method == "GET":
        serializer = ImageSerializerDetailed(image)
        return JsonResponse(serializer.data, safe=False)

    # Delete image and its file instance by ID
    elif request.method == "DELETE":
        image.file.delete()
        image.delete()
        return JsonResponse(
            {"message": "Image Deleted"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET", "DELETE"])
def get_delete_pdf(request, id):
    # Get pdf instance from ID
    pdf = get_object_or_404(PDF, id=id)

    # Return detailed pdf by ID
    if request.method == "GET":
        serializer = PDFSerializerDetailed(pdf)
        return JsonResponse(serializer.data, safe=False)

    # Delete pdf and its file instance by ID
    elif request.method == "DELETE":
        pdf.file.delete()
        pdf.delete()
        return JsonResponse(
            {"message": "PDF Deleted"}, status=status.HTTP_204_NO_CONTENT
        )


from PIL import ImageOps


@api_view(["POST"])
def rotate_image_view(request):
    image_id = request.data.get("image_id")
    rotation_angle = request.data.get("rotation_angle")

    # Get image object or raise 404 ID sent does not exist
    image = get_object_or_404(Image, id=image_id)

    # Error handle if rotation angle is not a number
    try:
        rotation_angle = int(rotation_angle)
    except ValueError:
        return JsonResponse(
            {"error": "Invalid rotation angle"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Open the image as IO Bytes and create a PIL Image object
    # Open the image as IO Bytes and create a PIL Image object
    with io.BytesIO(image.file.read()) as photo_new_io:
        pil_image = PILImage.open(photo_new_io)

        # Rotate the image and allow expansion
        rotated_image = pil_image.rotate(rotation_angle, expand=True)

        # Convert the image to RGB mode
        rotated_image = ImageOps.exif_transpose(rotated_image.convert("RGB"))

        # Resize if dimensions exceed the defined width and height
        if image.width is not None and image.height is not None:
            if rotated_image.width > image.width or rotated_image.height > image.height:
                rotated_image.thumbnail((image.width, image.height))

        # Save the rotated image to IO Bytes
        rotated_image_io = io.BytesIO()
        rotated_image.save(rotated_image_io, format="JPEG")

        # Overwrite the existing image file with the rotated image data
        with open(image.file.path, "wb") as f:
            f.write(rotated_image_io.getvalue())

    # Obtain the rotated image URL
    rotated_image_url = image.file.url
    return JsonResponse(
        {
            "message": "Image rotated",
            "rotated_image_url": rotated_image_url,
        },
        status=status.HTTP_200_OK,
    )


from pdf2image import convert_from_path
from django.conf import settings


@api_view(["POST"])
def convert_pdf_to_image(request):
    pdf_id = request.data.get("pdf_id")

    # Get the PDF object using the provided ID
    try:
        pdf = PDF.objects.get(id=int(pdf_id))
    except:
        return JsonResponse(
            {"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Convert the PDF to a list of images
    images = convert_from_path(pdf.file.path)
    # Generate a list of image paths to be returned after conversion
    generated_image_paths = []

    for i, image in enumerate(images):
        # Create the 'images' directory if it doesn't exist
        images_dir = "images/"

        # Extract the PDF file name
        pdf_name = os.path.basename(pdf.file.name)

        # Generate image filename with page number
        image_filename = f"{pdf_name}_page{i+1}.jpg"
        generated_image_path = os.path.join(images_dir, image_filename)

        # Save the image to the 'images' directory
        image.save("media/" + generated_image_path, "JPEG")

        # Create Image instance in the database
        new_image_instance = Image.objects.create(file=generated_image_path, uploaded_at=pdf.uploaded_at)

        # Assign PDF page width, height, and channel values to the image instance
        new_image_instance.width = pdf.page_width
        new_image_instance.height = pdf.page_height
        new_image_instance.number_of_channels = 3  # Assuming RGB format

        # Save the updated image instance
        new_image_instance.save()


        # Add the generated image URL to the list
        generated_image_paths.append("/media/" + generated_image_path)

    # Delete the original PDF file and PDF object
    pdf.file.delete()
    pdf.delete()

    # Return a success response with generated image paths
    return JsonResponse(
        {
            "message": "PDF converted to image(s) successfully",
            "image_paths": generated_image_paths,
        },
        status=status.HTTP_200_OK,
    )


# @api_view(["POST"])
# def convert_pdf_to_image(request):
#     pdf_id = request.data.get("pdf_id")
#     try:
#         pdf = PDF.objects.get(id=pdf_id)
#     except ObjectDoesNotExist:
#         return JsonResponse(
#             {"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND
#         )

#     images = convert_from_path(pdf.file.path)  # Convert PDF to images
#     generated_image_paths = []

#     for i, image in enumerate(images):
#         image_dir = "images/"
#         os.makedirs(
#             image_dir, exist_ok=True
#         )  # Create the 'images' directory if it doesn't exist
#         pdf_name = os.path.basename(pdf.file.name)  # Extract the PDF file name
#         image_path = os.path.join(image_dir, f"{pdf_name}_page{i+1}.jpg")

#         image.save("media/" + image_path, "JPEG")
#         Image.objects.create(file=image_path, uploaded_at=pdf.uploaded_at)
#         generated_image_paths.append(
#             "/media/" + image_path
#         )  # Add the generated image path to the list

#     pdf.file.delete()  # Delete the original PDF file
#     pdf.delete()  # Delete the PDF object

#     return JsonResponse(
#         {
#             "message": "PDF converted to image(s) successfully",
#             "image_paths": generated_image_paths,
#         },
#         status=status.HTTP_200_OK,
#     )


# @api_view(["POST"])
# def upload_file(request):
#     if request.method == "POST":
#         encoded_file = request.FILES["file"]
#         file_extension = encoded_file.name.split(".")[-1].lower()
#         serialized_data = None

#         if is_pdf(file_extension):
#             num_pages = get_num_pdf_pages(encoded_file)
#             print(num_pages)
#             serialized_data = PDFSerializerDetailed(
#                 data={
#                     "file": encoded_file,
#                     "num_pages": num_pages,
#                 }
#             )
#         elif is_image(file_extension):
#             serialized_data = ImageSerializer(data={"file": encoded_file})
#         else:
#             return Response(
#                 {"error": "Unsupported Media Type"},
#                 status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#             )

#         if serialized_data.is_valid():
#             document = serialized_data.save()

#             if is_pdf(file_extension):
#                 with open(document.file.path, "rb") as pdf_file:
#                     pdf_reader = PyPDF2.PdfReader(pdf_file)
#                     page = pdf_reader.pages[
#                         0
#                     ]  # Assuming you want dimensions of the first page
#                     page_width = page.mediabox[2] - page.mediabox[0]
#                     page_height = page.mediabox[3] - page.mediabox[1]

#                 # Update the PDF model instance with calculated values
#                 document.page_width = page_width
#                 document.page_height = page_height
#                 document.save()

#             elif is_image(file_extension):
#                 # Open the image using PIL
#                 with PILImage.open(document.file.path) as image:
#                     width, height = image.size
#                     number_of_channels = len(image.getbands())

#                 # Update the image model instance with calculated values
#                 document.width = width
#                 document.height = height
#                 document.number_of_channels = number_of_channels
#                 document.save()

#             return Response(
#                 {"message": "File uploaded successfully", "document_id": document.pk},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response({"error": serialized_data.errors}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(
#             {"error": "Invalid request method"},
#             status=status.HTTP_405_METHOD_NOT_ALLOWED,
#         )
