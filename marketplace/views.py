
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.http import HttpResponse

from reportlab.pdfgen import canvas

from .forms import (
    RegisterForm,
    PickupRequestForm,
    RecyclerRegistrationForm,
    PickupReviewForm,
)

from .models import (
    PickupRequest,
    RecyclerProfile,
    PickupReview,
)



def home(request):
    return render(request, "marketplace/home.html")



def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    "Registration successful! Please log in."
                )
                return redirect("login")

            except IntegrityError:
                messages.error(
                    request,
                    "This username is already registered. Please use a different username."
                )
                return redirect("register")

    else:
        form = RegisterForm()

    return render(
        request,
        "marketplace/register.html",
        {"form": form}
    )




def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        try:
            user_record = User.objects.get(email__iexact=email)
            user = authenticate(
                request,
                username=user_record.username,
                password=password
            )
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid Gmail or password.")

    return render(request, "marketplace/login.html")


@login_required
def dashboard(request):
    return render(request, "marketplace/dashboard.html")


def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

    return redirect("dashboard")


@login_required
def profile(request):
    return render(request, "marketplace/profile.html")


@login_required
def create_pickup(request):
    if request.method == "POST":
        form = PickupRequestForm(request.POST, request.FILES)

        if form.is_valid():
            pickup = form.save(commit=False)
            pickup.user = request.user
            pickup.save()

            messages.success(
                request,
                "Your e-waste pickup has been scheduled!"
            )
            return redirect("dashboard")
    else:
        form = PickupRequestForm()

    return render(
        request,
        "marketplace/pickup_form.html",
        {"form": form}
    )


@login_required
def my_pickups(request):
    pickups = PickupRequest.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "marketplace/my_pickups.html",
        {"pickups": pickups}
    )



@login_required
def recycler_dashboard(request):
    # Only superusers or approved recyclers can access this page
    is_approved_recycler = RecyclerProfile.objects.filter(
        user=request.user,
        approved=True
    ).exists()

    if not (request.user.is_superuser or is_approved_recycler):
        messages.error(
            request,
            "Your recycler application is not approved yet."
        )
        return redirect("dashboard")

    if request.method == "POST":
        pickup_id = request.POST.get("pickup_id")
        new_status = request.POST.get("status")

        allowed_statuses = ["Pending", "Processing", "Completed"]

        if new_status not in allowed_statuses:
            messages.error(request, "Invalid pickup status.")
            return redirect("recycler_dashboard")

        try:
            pickup = PickupRequest.objects.get(id=pickup_id)
        except (PickupRequest.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Pickup request not found.")
            return redirect("recycler_dashboard")

        # Do not allow a completed pickup to be reopened
        if pickup.status == "Completed" and new_status != "Completed":
            messages.error(
                request,
                "A completed pickup cannot be moved back to another status."
            )
            return redirect("recycler_dashboard")

        pickup.status = new_status
        pickup.save(update_fields=["status"])

        messages.success(
            request,
            "Pickup status updated successfully!"
        )
        return redirect("recycler_dashboard")

    pickups = PickupRequest.objects.all().order_by("-created_at")

    return render(
        request,
        "marketplace/recycler_dashboard.html",
        {"pickups": pickups}
    )



def recycler_register(request):
    if request.method == "POST":
        form = RecyclerRegistrationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()

            if User.objects.filter(email__iexact=email).exists():
                form.add_error(
                    "email",
                    "This email is already registered."
                )
            else:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=form.cleaned_data["password"],
                    )

                    profile = form.save(commit=False)
                    profile.user = user
                    profile.approved = False
                    profile.save()

                messages.success(
                    request,
                    "Application submitted! Please wait for admin approval."
                )
                return redirect("login")
    else:
        form = RecyclerRegistrationForm()

    return render(
        request,
        "marketplace/recycler_register.html",
        {"form": form}
    )

@login_required
def download_certificate(request, pickup_id):
    pickup = get_object_or_404(
        PickupRequest,
        id=pickup_id,
        user=request.user
    )

    if pickup.status != "Completed":
        messages.error(
            request,
            "Certificate is available only after completion."
        )
        return redirect("my_pickups")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="EcoCycle_Certificate_{pickup.id}.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=(595, 842))
    width, height = 595, 842

    pdf.setTitle(f"EcoCycle Certificate {pickup.id}")
    pdf.setStrokeColorRGB(0.1, 0.5, 0.3)
    pdf.setLineWidth(3)
    pdf.rect(30, 30, width - 60, height - 60)

    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(width / 2, 770, "EcoCycle")

    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(width / 2, 720, "DIGITAL DISPOSAL CERTIFICATE")

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2, 675,
        "This certificate confirms completion of the recorded e-waste request."
    )

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(75, 610, f"Certificate ID: EC-{pickup.id:05d}")

    pdf.setFont("Helvetica", 13)
    pdf.drawString(75, 565, f"User Name: {pickup.user.get_full_name() or pickup.user.username}")
    pdf.drawString(75, 525, f"E-Waste Category: {pickup.category}")
    pdf.drawString(75, 485, f"Quantity: {pickup.quantity}")
    pdf.drawString(75, 445, f"Condition: {pickup.condition}")
    pdf.drawString(75, 405, f"Pickup Date: {pickup.pickup_date.strftime('%d-%m-%Y')}")
    pdf.drawString(75, 365, f"Status: {pickup.status}")

    pdf.setFont("Helvetica-Oblique", 12)
    pdf.drawCentredString(
        width / 2, 290,
        "Thank you for supporting responsible e-waste management."
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        width / 2, 100,
        "Generated digitally by EcoCycle"
    )

    pdf.save()
    return response

@login_required
def submit_review(request, pickup_id):
    pickup = get_object_or_404(
        PickupRequest,
        id=pickup_id,
        user=request.user
    )

    if pickup.status != "Completed":
        messages.error(
            request,
            "You can review only completed pickups."
        )
        return redirect("my_pickups")

    if PickupReview.objects.filter(pickup=pickup).exists():
        messages.info(request, "You have already reviewed this pickup.")
        return redirect("my_pickups")

    if request.method == "POST":
        form = PickupReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.pickup = pickup
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect("my_pickups")
    else:
        form = PickupReviewForm()

    return render(
        request,
        "marketplace/review_form.html",
        {"form": form, "pickup": pickup}
    )
