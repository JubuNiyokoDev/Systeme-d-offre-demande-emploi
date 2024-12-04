from rest_framework import serializers
from .models import JobOffer, JobApplication

class JobOfferSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    publisher_name = serializers.CharField(source='publisher.username', read_only=True)

    class Meta:
        model = JobOffer
        fields = ['id', 'title', 'description', 'company', 'location', 'publisher',
                 'publisher_name', 'status', 'created_at', 'expires_at', 
                 'salary_range', 'is_expired']
        read_only_fields = ['publisher', 'status']

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'applicant', 'applicant_name', 
                 'status', 'applied_at', 'cover_letter']
        read_only_fields = ['applicant', 'status']