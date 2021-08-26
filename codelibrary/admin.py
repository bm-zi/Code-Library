from django.contrib import admin
from .models import Category, CodeLibrary, Language, Source

# Register your models here.

admin.site.register(Category)
admin.site.register(CodeLibrary)
admin.site.register(Language)
admin.site.register(Source)