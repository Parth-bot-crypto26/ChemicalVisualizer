import pandas as pd
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import AnalysisRecord
from .serializers import AnalysisRecordSerializer
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from reportlab.lib.utils import ImageReader

# 1. Custom Login View 
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

# 2. Main Analysis API (Secured)
class FileAnalysisView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [permissions.IsAuthenticated]  # REQUIRE LOGIN

    def get(self, request):
        records = AnalysisRecord.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
        serializer = AnalysisRecordSerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if 'file' not in request.data:
            return Response({"error": "No file uploaded"}, status=400)

        file_obj = request.data['file']
        
        try:
            df = pd.read_csv(file_obj)
        except Exception as e:
            return Response({"error": f"Invalid CSV: {str(e)}"}, status=400)

        required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        if not all(col in df.columns for col in required_cols):
             return Response({"error": f"Missing columns. Required: {required_cols}"}, status=400)

        stats = {
            'total_count': int(len(df)),
            'avg_temp': float(df['Temperature'].mean()),
            'avg_pressure': float(df['Pressure'].mean()),
            'avg_flow': float(df['Flowrate'].mean()),
            'type_distribution': df['Type'].value_counts().to_dict()
        }

        # Save record linked to USER
        record = AnalysisRecord.objects.create(
            user=request.user,
            file=file_obj,
            file_name=file_obj.name,
            total_count=stats['total_count'],
            avg_temp=stats['avg_temp'],
            avg_pressure=stats['avg_pressure'],
            avg_flow=stats['avg_flow']
        )

        # Get updated history
        history = AnalysisRecord.objects.filter(user=request.user).order_by('-uploaded_at')[:5]

        return Response({
            'stats': stats,
            'preview_data': df.head(10).to_dict(orient='records'),
            'history': AnalysisRecordSerializer(history, many=True).data
        }, status=status.HTTP_201_CREATED)

# 3. PDF Report Generation
class PDFReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, record_id):
        try:
            record = AnalysisRecord.objects.get(id=record_id, user=request.user)
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, 750, "Chemical Equipment Analysis Report")
            c.setFont("Helvetica", 12)
            c.drawString(50, 730, f"Generated for: {request.user.username}")
            c.drawString(50, 715, f"File: {record.file_name}")
            c.line(50, 700, 550, 700)

            y = 650
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Summary Statistics")
            y -= 30
            c.setFont("Helvetica", 12)
            stats = [
                f"Total Equipment Count: {record.total_count}",
                f"Average Temperature: {record.avg_temp:.2f} C",
                f"Average Pressure: {record.avg_pressure:.2f} atm",
                f"Average Flowrate: {record.avg_flow:.2f} L/m"
            ]
            for stat in stats:
                c.drawString(70, y, f"- {stat}")
                y -= 20

            try:
                df = pd.read_csv(record.file.path)
                type_counts = df['Type'].value_counts()
                
                plt.figure(figsize=(6, 4))
                type_counts.plot(kind='bar', color='#2a5298')
                plt.title("Equipment Type Distribution")
                plt.xlabel("Type")
                plt.ylabel("Count")
                plt.tight_layout()
                
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=100)
                img_buffer.seek(0)
                plt.close() 
                c.drawImage(ImageReader(img_buffer), 50, 250, width=500, height=300)
                
            except Exception as e:
                c.drawString(50, 250, f"(Chart could not be generated: {str(e)})")

            c.showPage()
            c.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
            
        except AnalysisRecord.DoesNotExist:
            return Response({"error": "Report not found or access denied"}, status=404)