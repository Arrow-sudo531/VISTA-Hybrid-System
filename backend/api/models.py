from django.db import models
from django.contrib.auth.models import User


class EquipmentDataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipment_datasets')
    file_name = models.CharField(max_length=255)
    summary_data = models.JSONField()
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Equipment Dataset'
        verbose_name_plural = 'Equipment Datasets'
    
    def __str__(self):
        return f"{self.file_name} - {self.user.username} ({self.upload_date.strftime('%Y-%m-%d')})"