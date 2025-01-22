from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserChangeForm,
    PasswordChangeForm,
    SetPasswordForm,
)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        help_text="Lettres, chiffres et @/./+/-/_ uniquement.",
    )

    email = forms.EmailField(
        label="Adresse email",
        required=True,
        help_text="Nous ne partagerons jamais votre email.",
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(),
        help_text="8 caractères minimum",
    )

    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(),
        help_text="Entrez le même mot de passe que précédemment.",
    )

    is_recruiter = forms.BooleanField(
        required=False,
        label="Je suis un recruteur",
        help_text="Cochez cette case si vous souhaitez publier des offres d'emploi",
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "is_recruiter")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supprimer les messages d'aide par défaut
        self.fields["username"].help_text = "Lettres, chiffres et @/./+/-/_ uniquement."
        self.fields["password1"].help_text = "8 caractères minimum"
        self.fields[
            "password2"
        ].help_text = "Entrez le même mot de passe que précédemment."

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1, self.instance)
        except forms.ValidationError as error:
            # Personnaliser les messages d'erreur
            custom_error_messages = {
                "password_too_short": "Le mot de passe doit contenir au moins 8 caractères.",
                "password_too_common": "Ce mot de passe est trop courant.",
                "password_entirely_numeric": "Le mot de passe ne peut pas être entièrement numérique.",
                "password_too_similar": "Le mot de passe ne peut pas être trop similaire à vos informations personnelles.",
            }

            # Remplacer les messages d'erreur par défaut
            custom_errors = []
            for e in error.messages:
                for key, message in custom_error_messages.items():
                    if key in e:
                        custom_errors.append(message)
                        break
                else:
                    custom_errors.append(e)

            raise forms.ValidationError(custom_errors)

        return password1


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomUserChangeForm(UserChangeForm):
    password = None  # Exclure le champ de mot de passe du formulaire

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "phone_number", "first_name", "last_name"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs obligatoires
        self.fields["email"].required = True
        self.fields["username"].help_text = None  # Supprimer le texte d'aid


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des messages d'erreur
        self.error_messages = {
            "password_incorrect": "Votre ancien mot de passe est incorrect.",
            "password_mismatch": "Les deux mots de passe ne correspondent pas.",
        }

        # Ajout des classes Bootstrap aux champs
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": f"Entrez votre {self.fields[field].label.lower()}",
                }
            )
