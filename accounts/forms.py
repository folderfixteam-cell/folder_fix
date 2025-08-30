# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# helper to add bootstrap class
def add_bootstrap(field, placeholder=None):
    css = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = f"{css} form-control".strip()
    if placeholder:
        field.widget.attrs["placeholder"] = placeholder
    return field


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        ),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last name"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username or Email"}
        ),
        label="Username or Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
        label="Password",
    )

    def clean(self):
        cleaned = super().clean()
        uoe = cleaned.get("username_or_email", "").strip()
        password = cleaned.get("password")
        user = None
        if "@" in uoe:
            try:
                obj = User.objects.get(email=uoe)
                user = authenticate(username=obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=uoe, password=password)

        if not user:
            raise forms.ValidationError("Invalid credentials.")
        cleaned["user"] = user
        return cleaned


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter OTP"}
        ),
        label="OTP",
    )


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your registered email"}
        ),
        label="Email",
    )


class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New password"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
        label="Confirm Password",
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password1") != cleaned.get("new_password2"):
            self.add_error("new_password2", "Passwords do not match.")
        return cleaned


# accounts/forms.py (append this at the bottom or place near other forms)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last name"}
            ),
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            # email is rendered read-only in template (disabled), but keep widget for display
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                    "readonly": "readonly",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        # Prevent email edits through form tampering
        return self.instance.email
