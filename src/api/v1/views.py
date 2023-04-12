from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def root(request: Request) -> Response:  # pylint: disable=unused-argument
    return Response({"body": "text"})


@api_view(["POST"])
def root(request: Request) -> Response:  # pylint: disable=unused-argument
    return Response({"body": "post textd"})
