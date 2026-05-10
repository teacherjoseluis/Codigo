from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurante.api.serializers import (
    CatalogoClasificacionSerializer,
    PresentacionSerializer,
    SucursalSistemaSerializer,
    TipoCuentaContableSerializer,
    UnidadMedidaSerializer,
)
from restaurante.models import (
    CatalogoClasificacion,
    Presentacion,
    SucursalSistema,
    TipoCuentaContable,
    UnidadMedida,
)


class HealthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'ok',
                'service': 'restaurante-api',
                'version': 'v1',
            }
        )


class SucursalSistemaListAPIView(generics.ListAPIView):
    serializer_class = SucursalSistemaSerializer
    queryset = SucursalSistema.objects.order_by('id')


class SucursalSistemaDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SucursalSistemaSerializer
    queryset = SucursalSistema.objects.order_by('id')


class CatalogoClasificacionListAPIView(generics.ListAPIView):
    serializer_class = CatalogoClasificacionSerializer
    queryset = CatalogoClasificacion.objects.order_by('id')


class UnidadMedidaListAPIView(generics.ListAPIView):
    serializer_class = UnidadMedidaSerializer
    queryset = UnidadMedida.objects.order_by('id')


class PresentacionListAPIView(generics.ListAPIView):
    serializer_class = PresentacionSerializer
    queryset = Presentacion.objects.order_by('id')


class TipoCuentaContableListAPIView(generics.ListAPIView):
    serializer_class = TipoCuentaContableSerializer
    queryset = TipoCuentaContable.objects.order_by('id')
