from django.db import models


class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width = models.PositiveIntegerField(null=True)
    height = models.PositiveIntegerField(null=True)
    number_of_channels = models.PositiveIntegerField(null=True)
    

class PDF(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    num_pages = models.PositiveIntegerField(null=True)
    page_width = models.PositiveIntegerField(null=True)
    page_height = models.PositiveIntegerField(null=True)