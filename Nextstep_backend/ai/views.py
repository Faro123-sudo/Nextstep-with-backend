from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .gemini import get_gemini_recommendations
import logging

# Configure logging
logger = logging.getLogger(__name__)

class CareerRecommendationView(APIView):
    """
    API view to get career recommendations based on user's quiz responses.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests with user's quiz responses.
        """
        user_responses = request.data
        
        if not user_responses or 'responses' not in user_responses:
            logger.warning("Career recommendation request with invalid input.")
            return Response(
                {"error": "Invalid input. 'responses' key is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            recommendations = get_gemini_recommendations(user_responses)
            
            if not recommendations:
                logger.error("Gemini service returned no recommendations.")
                return Response(
                    {"error": "Could not generate recommendations at this time. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(recommendations, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"An unexpected error occurred in CareerRecommendationView: {e}")
            return Response(
                {"error": "An internal server error occurred while generating recommendations."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )