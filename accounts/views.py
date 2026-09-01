from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsInstructor

from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# # Test view to get the current logged-in user's information
# class MeView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response(
#             {
#                 "id": request.user.id,
#                 "username": request.user.username,
#                 "email": request.user.email,
#                 "role": request.user.role,
#             }
#         )


# # Test view for instructor permisssion
# class InstructorTestView(APIView):
#     permission_classes = [IsAuthenticated, IsInstructor]

#     def get(self, request):
#         return Response(
#             {
#                 "message": "Welcome, Instructor!",
#                 "user": request.user.username,
#             }
#         )
