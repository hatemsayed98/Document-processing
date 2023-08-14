from rest_framework import serializers
from .models import Image, PDF


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file')

class ImageSerializerDetailed(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file', 'width' , 'height', 'number_of_channels', 'uploaded_at')


class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ('id', 'file')

class PDFSerializerDetailed(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ('id', 'file','num_pages','page_width','page_height', 'uploaded_at')