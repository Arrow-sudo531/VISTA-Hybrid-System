from django.contrib import admin
from django.urls import path
from api.views import UploadView, HistoryView, DownloadPDFView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/upload/', UploadView.as_view(), name='upload'),
    path('api/history/', HistoryView.as_view(), name='history'),
    path('api/download-pdf/', DownloadPDFView.as_view(), name='download_pdf'),
]