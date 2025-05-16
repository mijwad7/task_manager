from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Task, UserProfile
from .serializers import TaskSerializer
from django.core.mail import send_mail
import random
from datetime import datetime, timedelta
import json
from django.utils import timezone

# Task API ViewSet for CRUD operations
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return tasks for the authenticated user only
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Assign the task to the authenticated user
        serializer.save(user=self.request.user)

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            # Find user by email
            user = User.objects.get(email=email)
            # Authenticate using the username (which may be the email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Email not found'})
    return render(request, 'login.html')

# OTP login view
def otp_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        
        if not otp:  # Send OTP
            try:
                user = User.objects.get(email=email)
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Generate and save OTP
                otp = str(random.randint(100000, 999999))
                profile.otp = otp
                profile.otp_expiry = timezone.now() + timedelta(minutes=10)
                profile.save()
                
                # Send OTP via email (configure settings.py for email)
                send_mail(
                    'Your OTP Code',
                    f'Your OTP is {otp}. It expires in 10 minutes.',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                return render(request, 'otp_login.html', {'email': email, 'otp_sent': True})
            except User.DoesNotExist:
                return render(request, 'otp_login.html', {'error': 'Email not found'})
        
        # Verify OTP
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            if profile.otp == otp and profile.otp_expiry > timezone.now():
                login(request, user)
                profile.otp = None  # Clear OTP
                profile.otp_expiry = None
                profile.save()
                return redirect('dashboard')
            return render(request, 'otp_login.html', {'email': email, 'error': 'Invalid or expired OTP'})
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return render(request, 'otp_login.html', {'email': email, 'error': 'Invalid request'})
    
    return render(request, 'otp_login.html')

# Dashboard view with task list and calendar data
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    # Prepare calendar events
    events = [
        {
            'title': task.title,
            'start': task.due_date.isoformat(),
            'id': task.id,
            'status': task.status
        } for task in tasks
    ]
    return render(request, 'dashboard.html', {'tasks': tasks, 'events': json.dumps(events)})

# Task form for create/edit
@login_required
def task_form(request, task_id=None):
    task = Task.objects.get(id=task_id, user=request.user) if task_id else None
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        due_date = request.POST['due_date']
        status = request.POST.get('status', 'pending')
        
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
                status=status
            )
        return redirect('dashboard')
    return render(request, 'task_form.html', {'task': task})

# Delete task
@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.delete()
    return redirect('dashboard')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')