from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Image, PDF
from .serializers import ImageSerializer, PDFSerializer
from django.http import JsonResponse
from rest_framework import viewsets

from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from .serializers import PDFSerializer


@api_view(["POST"])
def upload_file(request):
    if request.method == "POST":
        encoded_file = request.data.get("file")
        file_extension = encoded_file.name.split(".")[-1]
        file_extension = file_extension.lower()
        print("file_extension", file_extension, type(file_extension))
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


# import base64
# from django.core.files.base import ContentFile

# @api_view(["POST"])
# def upload_pdf(request):
#     if request.method == "POST":
#         print(request.data)
#         encoded_file = request.data.get('file')
#         print(encoded_file)
#         file_extension = 'jpg'
#         print(encoded_file,file_extension)
#         if encoded_file and file_extension:
#             try:
#                 if file_extension.lower() == 'pdf':
#                     file_data = base64.b64decode(encoded_file)
#                     pdf_file = ContentFile(file_data)
#                     pdf = PDF(file=pdf_file)
#                     pdf.save()
#                     return JsonResponse(
#                         {"message": "PDF uploaded successfully", "document_id": pdf.pk}
#                     )
#                 elif file_extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
#                     file_data = base64.b64decode(encoded_file)
#                     image_file = ContentFile(file_data)
#                     image = Image(file=image_file)
#                     image.save()
#                     return JsonResponse(
#                         {"message": "Image uploaded successfully", "image_id": image.pk}
#                     )
#                 else:
#                     return JsonResponse({"error": "Invalid file extension"}, status=400)
#             except Exception as e:
#                 return JsonResponse({"error": str(e)}, status=400)
#         else:
#             return JsonResponse({"error": "Missing file or extension"}, status=400)
#     else:
#         return JsonResponse({"error": "Invalid request method"}, status=405)


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


@api_view(["GET"])
def get_image_details(request, id):
    try:
        image = Image.objects.get(id=id)
        serializer = ImageSerializer(image)
        return JsonResponse(serializer.data)
    except Image.DoesNotExist:
        return JsonResponse({"error": "Image does not exist"},status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_pdf_details(request, id):
    try:
        pdf = PDF.objects.get(id=id)
        serializer = PDFSerializer(pdf)
        return JsonResponse(serializer.data)
    except PDF.DoesNotExist:
        return JsonResponse({"error": "PDF does not exist"},status=status.HTTP_404_NOT_FOUND)



