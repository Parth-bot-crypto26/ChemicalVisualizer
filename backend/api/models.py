from django.db import models
from django.contrib.auth.models import User

class AnalysisRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    file = models.FileField(upload_to='csv_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    
    # Statistics
    total_count = models.IntegerField(default=0)
    avg_temp = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_flow = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at}"