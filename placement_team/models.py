from django.db import models
from django.utils.timezone import now
# Create your models here.
from django.db.models import UniqueConstraint

class Job_fairs(models.Model):
    job_fair_id = models.AutoField(primary_key=True)
    district = models.CharField(max_length=100)
    date_of_job_fair = models.DateField()
    date_of_creation = models.DateTimeField(default=now)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    class Meta:
        db_table = 'job_fairs'  

    def __str__(self):
        return f"{self.district} - {self.date_of_job_fair}"

class Recruiter(models.Model):
    recruiter_id = models.AutoField(primary_key=True)
    recruiter_email = models.EmailField(max_length=255,unique=True)
    recruiter_password = models.CharField(max_length=255)
    recruiter_qr_code = models.ImageField(upload_to='recruiter_qr_codes/', null=True, blank=True)

    def __str__(self):
        return self.recruiter_email
    
    class Meta:
        db_table = 'recruiter'

class RecruiterJobFair(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='recruiter_job_fairs')
    job_fair = models.ForeignKey(Job_fairs, on_delete=models.CASCADE, related_name='job_fair_recruiters')

    class Meta:
        db_table = 'recruiter_job_fair'
        constraints = [
            UniqueConstraint(fields=['recruiter', 'job_fair'], name='unique_recruiter_job_fair')
        ]