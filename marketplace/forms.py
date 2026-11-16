
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import PickupRequest, RecyclerProfile, PickupReview


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Gmail Address"
    )

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data["email"].strip().lower()
        user.email = email
        user.username = email

        if commit:
            user.save()

        return user


class PickupRequestForm(forms.ModelForm):
    
    def clean_pickup_date(self):
        from datetime import date

        pickup_date = self.cleaned_data["pickup_date"]

        if pickup_date < date.today():
            raise forms.ValidationError(
                "Pickup date cannot be in the past. Please select today or a future date."
            )

        return pickup_date

    class Meta:
        model = PickupRequest
        fields = [
            "category",
            "quantity",
            "condition",
            "image",
            "address",
            "pickup_date",
            "time_slot",
        ]

        widgets = {
            "pickup_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter pickup address"
                }
            ),
        }


class RecyclerRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label="Gmail Address")

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = RecyclerProfile
        fields = ["organization", "phone", "address"]

        widgets = {
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter organization address"
                }
            ),
        }


class PickupReviewForm(forms.ModelForm):
    class Meta:
        model = PickupReview
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "5 - Excellent"),
                    (4, "4 - Very Good"),
                    (3, "3 - Good"),
                    (2, "2 - Fair"),
                    (1, "1 - Poor"),
                ]
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Share your experience..."
                }
            ),
        }
