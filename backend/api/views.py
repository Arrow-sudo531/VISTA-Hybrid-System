from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import process_csv
from .models import EquipmentDataset
from django.contrib.auth import authenticate
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Login endpoint that returns an auth token
    CSRF exempt because desktop clients can't handle CSRF tokens
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for username: {username}")
        
        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                logger.warning(f"Inactive user login attempt: {username}")
                return Response({"error": "Account is disabled"}, status=401)
            
            token, created = Token.objects.get_or_create(user=user)
            logger.info(f"Successful login for user: {username} (Token {'created' if created else 'retrieved'})")
            
            return Response({
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            })
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return Response({"error": "Invalid username or password"}, status=401)


class LogoutView(APIView):
    """
    Logout endpoint - deletes the user's token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({"success": True, "message": "Logged out successfully"})
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({"error": "Logout failed"}, status=500)


class UploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Upload request from user: {request.user.username}")
        
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=400)
            
        file_obj = request.FILES['file']
        
        try:
            results = process_csv(file_obj)
            
            user_history = EquipmentDataset.objects.filter(user=request.user)
            if user_history.count() >= 5:
                user_history.order_by('upload_date').first().delete()
            
            EquipmentDataset.objects.create(
                user=request.user, 
                file_name=file_obj.name,
                summary_data=results
            )
            
            logger.info(f"Successfully processed file {file_obj.name} for user {request.user.username}")
            return Response(results, status=201)
        except ValueError as e:
            logger.error(f"CSV processing error for user {request.user.id}: {str(e)}")
            return Response({"error": f"Invalid CSV format: {str(e)}"}, status=400)
        except Exception as e:
            logger.error(f"Upload error for user {request.user.id}: {str(e)}")
            return Response({"error": "Failed to process file"}, status=500)


class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = EquipmentDataset.objects.filter(user=request.user).order_by('-upload_date')
        data = [
            {
                "id": h.id,
                "name": h.file_name, 
                "date": h.upload_date.isoformat()
            } 
            for h in history
        ]
        return Response(data)


class DownloadPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = EquipmentDataset.objects.filter(user=request.user).order_by('-upload_date').first()
        
        if not latest:
            return Response({"error": "No data found"}, status=404)

        try:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Report_{latest.file_name}.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, "V.I.S.T.A. Analytics Report")
            
            p.setFont("Helvetica", 10)
            p.drawString(100, 735, f"User: {request.user.username}")
            p.drawString(100, 720, f"Source: {latest.file_name}")
            p.drawString(100, 705, f"Generated: {latest.upload_date.strftime('%Y-%m-%d %H:%M')}")
            
            p.line(100, 690, 500, 690)
            
            summary = latest.summary_data
            p.setFont("Helvetica", 12)
            p.drawString(100, 660, f"Total Equipment: {summary.get('total_count', 'N/A')}")
            p.drawString(100, 640, f"Avg Pressure: {summary.get('averages', {}).get('avg_pressure', 'N/A')} PSI")
            p.drawString(100, 620, f"Avg Temp: {summary.get('averages', {}).get('avg_temp', 'N/A')} °C")
            
            p.showPage()
            p.save()
            return response
        except Exception as e:
            logger.error(f"PDF generation error for user {request.user.id}: {str(e)}")
            return Response({"error": "Failed to generate PDF"}, status=500)