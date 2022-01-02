from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.models import UninorteUser


@api_view(["DELETE"])
def delete_unverified_users_view(request):

    """
    Delete unverified users, those who registration process was manual

    """

    secret_code = request.query_params.get("secret_code", "")

    if secret_code == settings.DEL_UNVERIFIED_SECRET_CODE:
        amount, _ = (
            UninorteUser.objects.filter(verified=False)
            .filter(created_at__lte=timezone.now() - timedelta(weeks=1))
            .delete()
        )

        return Response(
            {"message": f"Successfully deleted {amount} unverified users"},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"message": "invalid secret code"},
        status=status.HTTP_401_UNAUTHORIZED,
    )
