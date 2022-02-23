from django.contrib import admin
from bangazon_api import models
# Register your models here.
admin.site.register(models.Product)
admin.site.register(models.Store)
admin.site.register(models.Favorite)
admin.site.register(models.Rating)
admin.site.register(models.Recommendation)
admin.site.register(models.Category)
admin.site.register(models.Order)
admin.site.register(models.PaymentType)
