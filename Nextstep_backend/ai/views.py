from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from .gemini import get_gemini_recommendations, get_career_recommendation
import logging

# Configure logging
logger = logging.getLogger(__name__)

class CareerRecommendationView(APIView):
    """
    API view to get career recommendations based on user's quiz responses.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

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


class CareerDetailRecommendationView(APIView):
    """
    API view to get a recommendation when viewing a specific career's details.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests with career data to generate a recommendation.
        Expects: { "career": {...career data...}, "userType": "student|professional|etc" }
        """
        career_data = request.data.get('career')
        user_type = request.data.get('userType')
        
        if not career_data or 'careerName' not in career_data:
            logger.warning("Career detail recommendation request with invalid career data.")
            return Response(
                {"error": "Invalid input. 'career' object with 'careerName' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            recommendation = get_career_recommendation(career_data, user_type)
            
            if not recommendation:
                logger.error("Gemini service returned no recommendation.")
                return Response(
                    {"error": "Could not generate recommendation at this time. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(recommendation, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"An unexpected error occurred in CareerDetailRecommendationView: {e}")
            return Response(
                {"error": "An internal server error occurred while generating recommendation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ---------------------------------------------------------------------------
# AI API flow (ai.views)
# ---------------------------------------------------------------------------
# - `CareerRecommendationView`: Accepts a JSON payload `{'responses': [...]}`
#   produced by frontend quiz flow, formats it and sends to `ai.gemini` for
#   model-driven career suggestions. Uses scoped throttling ('ai') to limit
#   rate and logs errors with context.
# - `CareerDetailRecommendationView`: Accepts a `career` object and optional
#   `userType` to produce a targeted recommendation (and an optional video
#   embed URL). The view validates input and returns structured JSON or a
#   500/400 with helpful messages on failure.
#
# Notes:
# - Both endpoints expect authenticated users (IsAuthenticated). If you want
#   recommendations for anonymous users, adjust permission classes.
# - The views intentionally keep LLM calls behind try/except and do not
#   expose raw LLM errors to clients; instead they log exceptions and return
#   safe error messages.
# ---------------------------------------------------------------------------