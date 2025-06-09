from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный URL",
        help_text="Короткая метка для контента, содержащая только буквы, цифры, подчеркивания (_) или дефисы (-)",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, verbose_name="Категория")
    slug = models.SlugField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name="Уникальный URL",
        help_text="Короткая метка для контента, содержащая только буквы, цифры, подчеркивания (_) или дефисы (-)",
    )
    image = models.ImageField(
        upload_to="images/products", verbose_name="Изображение", null=True, blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Товар активен")

    @property
    def cats(self):
        return [cat.name for cat in self.categories.all()]

    def __str__(self):
        catword = "категории" if self.categories.count() > 1 else "категория"
        return f"{self.name} -- {self.price} BYN -- активен: {self.is_active} -- {catword}: {', '.join(self.cats)}"

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Comment(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to="images/comments", verbose_name="Изображение", null=True, blank=True
    )

    def __str__(self):
        return f"Комментарий {self.author} на товар {self.product} в {self.created_at}"

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
