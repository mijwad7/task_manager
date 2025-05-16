from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']