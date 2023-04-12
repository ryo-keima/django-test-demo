from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    content = models.TextField()
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
