from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurante.api.serializers import (
    CatalogoClasificacionSerializer,
    PresentacionSerializer,
    RegMaestroCompraSerializer,
    RegMaestroContabilidadSerializer,
    RegMaestroFotoSerializer,
    RegMaestroInventarioSerializer,
    RegMaestroPedimentoSerializer,
    RegMaestroUbicacionFisicaSerializer,
    RegMaestroVentaSerializer,
    RegistroMaestroSerializer,
    SucursalSistemaSerializer,
    TipoCuentaContableSerializer,
    UnidadMedidaSerializer,
)
from restaurante.factory.RegMaestro_factory import RegMaestro
from restaurante.models import (
    CatalogoClasificacion,
    Presentacion,
    RegistroMaestro,
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


def _apply_validated_data(target, validated_data):
    for attr, value in validated_data.items():
        setattr(target, attr, value)


def _load_registro_maestro(pk):
    registro = RegMaestro()
    registro.get(pk)
    return registro


class RegistroMaestroListCreateAPIView(APIView):
    def get(self, request):
        registros = RegistroMaestro.objects.order_by('id')
        serializer = RegistroMaestroSerializer(registros, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegistroMaestroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registro = RegMaestro()
        _apply_validated_data(registro, serializer.validated_data)
        registro.save()

        return Response(
            RegistroMaestroSerializer(registro).data,
            status=status.HTTP_201_CREATED,
        )


class RegistroMaestroDetailAPIView(APIView):
    def get(self, request, pk):
        registro = _load_registro_maestro(pk)
        return Response(RegistroMaestroSerializer(registro).data)

    def patch(self, request, pk):
        registro = _load_registro_maestro(pk)
        serializer = RegistroMaestroSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        _apply_validated_data(registro, serializer.validated_data)
        registro.save()

        return Response(RegistroMaestroSerializer(registro).data)


class RegistroMaestroDisableAPIView(APIView):
    def post(self, request, pk):
        registro = _load_registro_maestro(pk)
        registro.disable()
        return Response(RegistroMaestroSerializer(registro).data)


class RegistroMaestroContextAPIView(APIView):
    context_type = None
    serializer_class = None

    def get(self, request, pk, ubicacion_id=None):
        contexto = self._load_context(pk, ubicacion_id)
        return Response(self.serializer_class(contexto).data)

    def put(self, request, pk, ubicacion_id=None):
        contexto, created = self._load_or_initialize_context(pk, ubicacion_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        _apply_validated_data(contexto, serializer.validated_data)
        if self.context_type == 'UbicacionFisica':
            contexto.idubicacionfisica = ubicacion_id
        contexto.save()

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(self.serializer_class(contexto).data, status=response_status)

    def _new_context(self, pk):
        registro = _load_registro_maestro(pk)
        return registro.contexto(registro, self.context_type)

    def _load_context(self, pk, ubicacion_id=None):
        contexto = self._new_context(pk)
        lookup_id = ubicacion_id if self.context_type == 'UbicacionFisica' else pk
        contexto.get(lookup_id)
        return contexto

    def _load_or_initialize_context(self, pk, ubicacion_id=None):
        contexto = self._new_context(pk)
        lookup_id = ubicacion_id if self.context_type == 'UbicacionFisica' else pk

        try:
            contexto.get(lookup_id)
            return contexto, False
        except ObjectDoesNotExist:
            if self.context_type == 'UbicacionFisica':
                contexto.idubicacionfisica = ubicacion_id
            return contexto, True


class RegistroMaestroCompraAPIView(RegistroMaestroContextAPIView):
    context_type = 'Compra'
    serializer_class = RegMaestroCompraSerializer


class RegistroMaestroVentaAPIView(RegistroMaestroContextAPIView):
    context_type = 'Venta'
    serializer_class = RegMaestroVentaSerializer


class RegistroMaestroInventarioAPIView(RegistroMaestroContextAPIView):
    context_type = 'Inventario'
    serializer_class = RegMaestroInventarioSerializer


class RegistroMaestroContabilidadAPIView(RegistroMaestroContextAPIView):
    context_type = 'Contabilidad'
    serializer_class = RegMaestroContabilidadSerializer


class RegistroMaestroPedimentoAPIView(RegistroMaestroContextAPIView):
    context_type = 'Pedimento'
    serializer_class = RegMaestroPedimentoSerializer


class RegistroMaestroFotoAPIView(RegistroMaestroContextAPIView):
    context_type = 'Foto'
    serializer_class = RegMaestroFotoSerializer


class RegistroMaestroUbicacionFisicaAPIView(RegistroMaestroContextAPIView):
    context_type = 'UbicacionFisica'
    serializer_class = RegMaestroUbicacionFisicaSerializer
