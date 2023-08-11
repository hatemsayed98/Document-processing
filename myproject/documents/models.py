from django.db import models


class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    

class PDF(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # class Meta:
    #     ordering = ['file']
     
    # def __str__(self):
    #     return self.file