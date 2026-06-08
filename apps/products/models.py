from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=50
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    # factory = models.ForeignKey(
    #     Factory,
    #     on_delete=models.PROTECT,
    #     related_name="products"
    # )

    name = models.CharField(max_length=255)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["name"]

    def __str__(self):
        return self.name