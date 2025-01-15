from django.contrib import admin
from .models import JobOffer, JobApplication, JobStatus

admin.site.register(JobOffer)
admin.site.register(JobApplication)
admin.site.register(JobStatus)
