from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API router
router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='tasks')

urlpatterns = [
    path('', views.login_view, name='login'),
    path('otp-login/', views.otp_login_view, name='otp_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/new/', views.task_form, name='task_create'),
    path('task/<int:task_id>/edit/', views.task_form, name='task_edit'),
    path('task/<int:task_id>/delete/', views.delete_task, name='task_delete'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),
]