from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import Category, Comment, Order
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class AddProduct(forms.Form):
    name = forms.CharField(label="Название")
    price = forms.DecimalField(label="Цена, BYN")
    description = forms.CharField(label="Описание", widget=forms.Textarea)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label="Категории",
        widget=forms.CheckboxSelectMultiple,
    )
    slug = forms.SlugField(
        label="Уникальный URL",
        required=False,
        help_text="Короткая метка для контента, содержащая только буквы, цифры, подчеркивания (_) или дефисы (-)",
    )
    image = forms.ImageField(label="Изображение", required=False)
    is_active = forms.BooleanField(
        label="Товар активен",
        required=False,
        help_text="Установите флажок, чтобы товар был доступен пользователям",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            *self.fields.keys(), Submit("submit", "Отправить", css_class="btn-primary")
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": ""}


class CustomRegister(UserCreationForm):
    email = forms.EmailField(
        label="Email", required=False, help_text="Необязательное поле."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Зарегистрироваться", css_class="btn-primary")
        )


class CustomLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Войти", css_class="btn-primary"))


class OrderConfirm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address_street",
            "address_building",
            "address_apartment",
            "address_floor",
            
        ]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
            "address_street": "Улица",
            "address_building": "Дом",
            "address_apartment": "Квартира",
            "address_floor": "Этаж",
        }
