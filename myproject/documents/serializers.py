from rest_framework import serializers
from .models import Image, PDF

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('file',)

class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ('file',)
