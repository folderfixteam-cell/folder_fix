from django import forms
from .models import ContactMessage,FAQ,Feedback

class ContactForm(forms.ModelForm):
    # Honeypot to block simple bots (hidden in template)
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control shadow-none p-2",
                "placeholder": "Enter your name",
                "required": True
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control shadow-none p-2",
                "placeholder": "Enter your email",
                "required": True
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control shadow-none p-2",
                "rows": 5,
                "placeholder": "Write your message",
                "required": True
            }),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Spam detected.")
        return cleaned




class FAQForm(forms.ModelForm):
    
    class Meta:
        model=FAQ
        fields = ["question"]
        widgets = {
            "question": forms.TextInput(attrs={
                "class": "form-control shadow-none p-2 ",
                "placeholder": "Enter your question ?",
                "required": True
            }),}





from django import forms
from .models import Feedback  # import your Feedback model

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your feedback here..."
            }),
        }
