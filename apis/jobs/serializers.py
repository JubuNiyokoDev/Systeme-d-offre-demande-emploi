from rest_framework import serializers
from apps.jobs.models import JobOffer, JobApplication
from django.utils import timezone 

class JobOfferSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher.username', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'company', 'description', 'location',
            'salary_range', 'status', 'created_at', 'expires_at',
            'publisher_name', 'is_expired'
        ]
        read_only_fields = ['publisher_name', 'created_at', 'is_expired']

    def validate_expires_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("La date d'expiration doit être dans le futur")
        return value

class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'applicant_name',
            'applied_at', 'status', 'cover_letter'
        ]
        read_only_fields = ['applicant', 'applied_at']