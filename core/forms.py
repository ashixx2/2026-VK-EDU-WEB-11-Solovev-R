from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from questions.models import Profile


class LoginForm(forms.Form):
    login = forms.CharField(
        label="Логин или email",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите логин или email",
            "id": "login-email",
        }),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль",
            "id": "login-password",
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        login_value = cleaned_data.get("login")
        password = cleaned_data.get("password")

        if not login_value or not password:
            return cleaned_data

        username = login_value

        if "@" in login_value:
            try:
                username = User.objects.get(email__iexact=login_value).username
            except User.DoesNotExist:
                raise ValidationError("Пользователь с таким email не найден.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise ValidationError("Неверный логин или пароль.")

        if not user.is_active:
            raise ValidationError("Этот аккаунт отключён.")

        cleaned_data["user"] = user
        return cleaned_data


class SignupForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите логин",
            "id": "signup-login",
        }),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите email",
            "id": "signup-email",
        }),
    )
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите имя",
            "id": "signup-first-name",
        }),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль",
            "id": "signup-password",
        }),
    )
    password_repeat = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Повторите пароль",
            "id": "signup-password-repeat",
        }),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")

        if password and password_repeat and password != password_repeat:
            self.add_error("password_repeat", "Пароли не совпадают.")

        if password:
            user = User(
                username=cleaned_data.get("username"),
                email=cleaned_data.get("email"),
                first_name=cleaned_data.get("first_name", ""),
            )

            try:
                password_validation.validate_password(password, user)
            except ValidationError as error:
                self.add_error("password", error)

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data.get("first_name", ""),
        )

        Profile.objects.create(user=user)

        return user


class ProfileForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "profile-username",
        }),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "id": "profile-email",
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        if user and not self.is_bound:
            self.fields["username"].initial = user.username
            self.fields["email"].initial = user.email

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.exclude(pk=self.user.pk).filter(username__iexact=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")

        return email

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.save(update_fields=["username", "email"])

        return self.user