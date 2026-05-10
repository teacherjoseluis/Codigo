from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurante.api.permissions import SucursalScopedQuerysetMixin
from restaurante.api.serializers import (
    AsientoContableSerializer,
    CatalogoClasificacionSerializer,
    ClaveFolioSerializer,
    ClienteSistemaSerializer,
    CuentaContableSerializer,
    DetalleDocumentoSerializer,
    DocumentoAsientoSerializer,
    DocumentoConceptoSerializer,
    DocumentoMovimientoSerializer,
    DocumentoSerializer,
    ExtradetalleDocumentoSerializer,
    MovimientoContableSerializer,
    NumeracionFolioSerializer,
    PersonaFiscalSerializer,
    PersonafiscalProveedorSerializer,
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
    AsientoContable,
    CatalogoClasificacion,
    ClaveFolio,
    ClienteSistema,
    CuentaContable,
    DetalleDocumento,
    Documento,
    DocumentoAsiento,
    DocumentoConcepto,
    DocumentoMovimiento,
    ExtradetalleDocumento,
    MovimientoContable,
    NumeracionFolio,
    PersonaFiscal,
    PersonafiscalProveedor,
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


class SucursalSistemaListAPIView(SucursalScopedQuerysetMixin, generics.ListAPIView):
    serializer_class = SucursalSistemaSerializer
    queryset = SucursalSistema.objects.order_by('id')
    search_fields = ['nombre', 'identificadorcorto']
    ordering_fields = ['id', 'nombre', 'identificadorcorto']


class SucursalSistemaDetailAPIView(SucursalScopedQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = SucursalSistemaSerializer
    queryset = SucursalSistema.objects.order_by('id')
    ordering_fields = ['id', 'nombre', 'identificadorcorto']


class CatalogoClasificacionListAPIView(generics.ListAPIView):
    serializer_class = CatalogoClasificacionSerializer
    queryset = CatalogoClasificacion.objects.order_by('id')
    search_fields = ['nombreclasificacion', 'estatus']
    ordering_fields = ['id', 'nombreclasificacion', 'estatus']


class UnidadMedidaListAPIView(generics.ListAPIView):
    serializer_class = UnidadMedidaSerializer
    queryset = UnidadMedida.objects.order_by('id')
    search_fields = ['unidadmedida']
    ordering_fields = ['id', 'unidadmedida']


class PresentacionListAPIView(generics.ListAPIView):
    serializer_class = PresentacionSerializer
    queryset = Presentacion.objects.order_by('id')
    search_fields = ['nombrepresentacion', 'tipo']
    ordering_fields = ['id', 'nombrepresentacion', 'tipo']


class TipoCuentaContableListAPIView(generics.ListAPIView):
    serializer_class = TipoCuentaContableSerializer
    queryset = TipoCuentaContable.objects.order_by('id')
    search_fields = ['instancia']
    ordering_fields = ['id', 'tipo', 'instancia']


def _apply_validated_data(target, validated_data):
    for attr, value in validated_data.items():
        setattr(target, attr, value)


def _load_registro_maestro(pk):
    registro = RegMaestro()
    registro.get(pk)
    return registro


class RegistroMaestroListCreateAPIView(generics.GenericAPIView):
    serializer_class = RegistroMaestroSerializer
    queryset = RegistroMaestro.objects.order_by('id')
    search_fields = ['nombre', 'tipo', 'marca', 'estatus']
    ordering_fields = ['id', 'nombre', 'tipo', 'marca', 'estatus']

    def get(self, request):
        registros = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(registros)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(registros, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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


class DocumentoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentoSerializer
    queryset = Documento.objects.order_by('-fecha_hora', '-id')
    search_fields = ['foliointerno', 'foliodocumento', 'estatus']
    ordering_fields = ['id', 'fecha_hora', 'monto', 'estatus']


class DocumentoDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DocumentoSerializer
    queryset = Documento.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']
    search_fields = ['foliointerno', 'foliodocumento', 'estatus']
    ordering_fields = ['id', 'fecha_hora', 'monto', 'estatus']


class DocumentoChildListCreateAPIView(generics.ListCreateAPIView):
    parent_url_kwarg = 'documento_id'
    parent_field = 'id_documento'

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.documento = generics.get_object_or_404(
            Documento.objects.all(),
            id=kwargs[self.parent_url_kwarg],
        )

    def get_queryset(self):
        return self.model.objects.filter(
            **{self.parent_field: self.documento.id}
        ).order_by('id')

    def perform_create(self, serializer):
        serializer.save(**{self.parent_field: self.documento.id})


class DocumentoChildDetailAPIView(generics.RetrieveUpdateAPIView):
    parent_url_kwarg = 'documento_id'
    lookup_url_kwarg = 'child_id'
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return self.model.objects.filter(
            **{self.parent_field: self.kwargs[self.parent_url_kwarg]}
        ).order_by('id')


class DocumentoDetalleListCreateAPIView(DocumentoChildListCreateAPIView):
    serializer_class = DetalleDocumentoSerializer
    model = DetalleDocumento
    search_fields = ['comentarios', 'estatus']
    ordering_fields = ['id', 'subtotal', 'estatus']


class DocumentoDetalleDetailAPIView(DocumentoChildDetailAPIView):
    serializer_class = DetalleDocumentoSerializer
    model = DetalleDocumento
    parent_field = 'id_documento'


class DetalleExtraListCreateAPIView(DocumentoChildListCreateAPIView):
    serializer_class = ExtradetalleDocumentoSerializer
    model = ExtradetalleDocumento
    parent_url_kwarg = 'detalle_id'
    parent_field = 'id_detalledocumento'
    ordering_fields = ['id', 'cantidad', 'costopreciototal']

    def initial(self, request, *args, **kwargs):
        APIView.initial(self, request, *args, **kwargs)
        self.detalle = generics.get_object_or_404(
            DetalleDocumento.objects.all(),
            id=kwargs[self.parent_url_kwarg],
            id_documento=kwargs['documento_id'],
        )
        self.documento = self.detalle


class DocumentoMovimientoContableListCreateAPIView(DocumentoChildListCreateAPIView):
    serializer_class = MovimientoContableSerializer
    model = MovimientoContable
    ordering_fields = ['id', 'id_librosucursal', 'id_documentoconcepto']


class DocumentoMovimientoContableDetailAPIView(DocumentoChildDetailAPIView):
    serializer_class = MovimientoContableSerializer
    model = MovimientoContable
    parent_field = 'id_documento'


class DocumentoAsientoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentoAsientoSerializer
    ordering_fields = ['id', 'id_asiento']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.documento = generics.get_object_or_404(
            Documento.objects.all(),
            id=kwargs['documento_id'],
        )

    def get_queryset(self):
        return DocumentoAsiento.objects.filter(
            id_clavefolio=self.documento.id_clavefolio,
            id_conceptodocumento=self.documento.id_conceptodocumento,
            id_movimientodocumento=self.documento.id_documentomovimiento,
        ).order_by('id')

    def perform_create(self, serializer):
        serializer.save(
            id_clavefolio=self.documento.id_clavefolio,
            id_conceptodocumento=self.documento.id_conceptodocumento,
            id_movimientodocumento=self.documento.id_documentomovimiento,
        )


class ClaveFolioListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ClaveFolioSerializer
    queryset = ClaveFolio.objects.order_by('id')
    search_fields = ['nombredocumento', 'clavefolio']
    ordering_fields = ['id', 'nombredocumento', 'clavefolio']


class ClaveFolioDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ClaveFolioSerializer
    queryset = ClaveFolio.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']


class FolioNumeracionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NumeracionFolioSerializer
    ordering_fields = ['id', 'id_sucursal_sistema', 'numeroactual']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.clavefolio = generics.get_object_or_404(
            ClaveFolio.objects.all(),
            id=kwargs['folio_id'],
        )

    def get_queryset(self):
        return NumeracionFolio.objects.filter(
            id_clavefolio=self.clavefolio.id,
        ).order_by('id')

    def perform_create(self, serializer):
        serializer.save(id_clavefolio=self.clavefolio.id)


class DocumentoMovimientoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentoMovimientoSerializer
    queryset = DocumentoMovimiento.objects.order_by('id')
    search_fields = ['movimientodocumento']
    ordering_fields = ['id', 'movimientodocumento']


class DocumentoConceptoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentoConceptoSerializer
    queryset = DocumentoConcepto.objects.order_by('id')
    search_fields = ['conceptodocumento']
    ordering_fields = ['id', 'conceptodocumento', 'id_clavefolio', 'id_movimiento']


class AsientoContableListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AsientoContableSerializer
    queryset = AsientoContable.objects.order_by('id')
    search_fields = ['nombreclasificacion', 'nombreasiento']
    ordering_fields = ['id', 'nombreclasificacion', 'nombreasiento']


class PersonaFiscalListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PersonaFiscalSerializer
    queryset = PersonaFiscal.objects.order_by('id')
    search_fields = ['nombre', 'rfc', 'raz_n_social', 'estatus']
    ordering_fields = ['id', 'nombre', 'rfc', 'estatus']


class PersonaFiscalDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonaFiscalSerializer
    queryset = PersonaFiscal.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']


class ClienteSistemaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ClienteSistemaSerializer
    queryset = ClienteSistema.objects.order_by('id')
    ordering_fields = ['id', 'id_personafiscal']


class ClienteSistemaDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ClienteSistemaSerializer
    queryset = ClienteSistema.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']


class PersonafiscalProveedorListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PersonafiscalProveedorSerializer
    queryset = PersonafiscalProveedor.objects.order_by('id')
    ordering_fields = ['id', 'id_personafiscal', 'diascredito', 'tiemposurtido']


class PersonafiscalProveedorDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonafiscalProveedorSerializer
    queryset = PersonafiscalProveedor.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']


class CuentaContableListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CuentaContableSerializer
    queryset = CuentaContable.objects.order_by('id')
    search_fields = ['nombre', 'sub_tipo']
    ordering_fields = ['id', 'nombre', 'tipo', 'id_cliente', 'sub_tipo']


class CuentaContableDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CuentaContableSerializer
    queryset = CuentaContable.objects.order_by('id')
    http_method_names = ['get', 'patch', 'head', 'options']
