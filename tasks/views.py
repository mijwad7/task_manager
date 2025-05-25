from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from .models import Task, UserProfile
from .serializers import TaskSerializer
from django.core.mail import send_mail
import random
from datetime import datetime, timedelta
import json
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Task API ViewSet for CRUD operations
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# User registration view
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]
        password_confirm = request.POST["password_confirm"]

        # Validate input
        if password != password_confirm:
            return render(request, "register.html", {"error": "Passwords do not match"})
        if len(password) < 8:
            return render(
                request,
                "register.html",
                {"error": "Password must be at least 8 characters long"},
            )
        if User.objects.filter(email=email).exists():
            return render(
                request, "register.html", {"error": "Email already registered"}
            )

        # Create user with email as username
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = True
        user.save()
        return redirect("login")
    return render(request, "register.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                return render(request, "login.html", {"error": "Invalid password"})
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Email not found"})
    return render(request, "login.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def otp_login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        otp = request.POST.get("otp")

        if not otp:  # Send OTP
            try:
                user = User.objects.get(email=email)
                profile, created = UserProfile.objects.get_or_create(user=user)

                # Generate and save OTP
                otp = str(random.randint(100000, 999999))
                profile.otp = otp
                profile.otp_expiry = timezone.now() + timedelta(minutes=10)
                profile.save()

                # Send OTP via email
                send_mail(
                    "Your OTP Code",
                    f"Your OTP is {otp}. It expires in 10 minutes.",
                    "from@example.com",
                    [email],
                    fail_silently=False,
                )
                return render(
                    request, "otp_login.html", {"email": email, "otp_sent": True}
                )
            except User.DoesNotExist:
                return render(request, "otp_login.html", {"error": "Email not found"})

        # Verify OTP
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            if profile.otp == otp and profile.otp_expiry > timezone.now():
                login(request, user)
                profile.otp = None
                profile.otp_expiry = None
                profile.save()
                return redirect("dashboard")
            return render(
                request,
                "otp_login.html",
                {"email": email, "error": "Invalid or expired OTP"},
            )
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return render(
                request, "otp_login.html", {"email": email, "error": "Invalid request"}
            )

    return render(request, "otp_login.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user).order_by('-due_date')
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    events = [
        {
            "title": task.title,
            "start": task.due_date.isoformat() if task.due_date else timezone.now().isoformat(),
            "id": task.id,
            "status": task.status,
        }
        for task in tasks
    ]
    return render(
        request, "dashboard.html", {
            "tasks": page_obj,
            "events": json.dumps(events),
            "page_obj": page_obj
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def task_form(request, task_id=None):
    task = Task.objects.get(id=task_id, user=request.user) if task_id else None
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        due_date = request.POST["due_date"]
        status = request.POST.get("status", "pending")

        if task:
            task.title = title
            task.description = description
            task.due_date = due_date
            task.status = status
            task.save()
        else:
            Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                due_date=due_date,
                status=status,
            )
        return redirect("dashboard")
    return render(request, "task_form.html", {"task": task})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
    return redirect("dashboard")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    response = redirect("login")
    response.delete_cookie('sessionid')
    return response