from django.db import models

from django.utils import timezone
# Create your models here.


class Language(models.Model):
    language = models.CharField(max_length=50)
    
    def __str__(self):
        return self.language
        
    def serialize(self):
        return{
            "language": self.language
        }

class Category(models.Model):
    category = models.CharField(max_length=256)

    def __str__(self):
        return self.category

    def serialize(self):
        return{
            "category": self.category
        }


class Source(models.Model):
    source = models.TextField(max_length=10240)

    def __str__(self):
        return self.source

    def serialize(self):
        return{
            "source": self.source
        }


class CodeLibrary(models.Model):
    title = models.CharField(max_length=256, unique=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    source = models.OneToOneField(Source, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now) # or use: auto_now_add=True
    updated_at = models.DateTimeField(default=timezone.now) # or use: auto_now_add=True
    is_favorite = models.BooleanField(default=False)


    def __str__(self):
        return self.title


    def delete(self, *args, **kwargs):
        self.source.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
            self.updated_at = timezone.now()
        return super(CodeLibrary, self).save(*args, **kwargs)


    def serialize(self):
        return{
            "title": self.title,
            "language": self.language,
            "category": self.category.all(),
            "is_favorite": self.is_favorite,
            "source": self.source,
        }
