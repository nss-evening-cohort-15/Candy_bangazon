from django.contrib.auth.models import User
from django.db import models


class Recommendation(models.Model):
    recommender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_by')
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendations")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
