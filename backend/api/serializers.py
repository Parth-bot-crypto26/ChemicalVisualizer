from rest_framework import serializers
from .models import AnalysisRecord

class AnalysisRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRecord
        fields = '__all__'