
from django.db import models
from django.contrib.auth.models import User


class PickupRequest(models.Model):
    CATEGORY_CHOICES = [
        ("Mobile", "Mobile"),
        ("Laptop", "Laptop"),
        ("Computer", "Computer"),
        ("Battery", "Battery"),
        ("Television", "Television"),
        ("Other", "Other"),
    ]

    CONDITION_CHOICES = [
        ("Working", "Working"),
        ("Damaged", "Damaged"),
        ("Not Working", "Not Working"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES)
    image = models.ImageField(upload_to="ewaste/", blank=True, null=True)
    address = models.TextField()
    pickup_date = models.DateField()
    time_slot = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.user.username}"


class RecyclerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=15)
    organization = models.CharField(max_length=150)
    address = models.TextField()
    approved = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization} - {'Approved' if self.approved else 'Pending'}"

class PickupReview(models.Model):
    pickup = models.OneToOneField(
        PickupRequest,
        on_delete=models.CASCADE,
        related_name="review"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}/5"
