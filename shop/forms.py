from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Category, Product


class AddProduct(forms.Form):
    name = forms.CharField(label="Название")
    price = forms.DecimalField(label="Цена, BYN")
    description = forms.CharField(label="Описание", widget=forms.Textarea)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label="Категории",
        widget=forms.CheckboxSelectMultiple
    )   
    slug = forms.SlugField(label="Уникальный URL", required=False)
    image = forms.ImageField(label="Изображение", required=False)
    is_active = forms.BooleanField(label="Товар активен", required=False, help_text='Установите флажок, чтобы товар показывался пользователям')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            *self.fields.keys(),
            Submit("submit", "Отправить", css_class="btn-primary")
        )
