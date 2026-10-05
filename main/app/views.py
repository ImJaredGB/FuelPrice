import requests
import subprocess
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def fuel(request):

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"

    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return Response(
            {"error":"Could not retrive fuel data"},
            status=502
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response(
            {"error":"Could not parse fuel data"},
            status=502
        )
    
    return Response(data)