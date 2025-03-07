from django.db import models

# Create your models here.
class Recruiter(models.Model):
    recruiter_id = models.AutoField(primary_key=True)
    recruiter_email = models.EmailField(max_length=255,unique=True)
    recruiter_password = models.CharField(max_length=255)
    recruiter_qr_code = models.ImageField(upload_to='recruiter_qr_codes/', null=True, blank=True)

    def __str__(self):
        return self.recruiter_email
    
    class Meta:
        db_table = 'recruiter'
