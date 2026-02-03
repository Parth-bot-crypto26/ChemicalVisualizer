from django.urls import path
from .views import FileAnalysisView, PDFReportView, CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('analyze/', FileAnalysisView.as_view(), name='analyze'),
    path('report/<int:record_id>/', PDFReportView.as_view(), name='pdf_report'),
]