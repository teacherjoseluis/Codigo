from decimal import Decimal

from django.contrib.auth import authenticate
from rest_framework import serializers

from restaurante.api.permissions import require_ubicacion_scope
from restaurante.api.services import create_documento_with_children, create_legacy_instance
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
    UbicacionFisica,
    UnidadMedida,
)


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate(
            request=request,
            username=attrs.get('username'),
            password=attrs.get('password'),
        )
        if not user:
            raise serializers.ValidationError('Unable to log in with provided credentials.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


class AuthUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()


class SucursalSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SucursalSistema
        fields = [
            'id',
            'nombre',
            'direccion',
            'personacontacto',
            'telefono1',
            'telefono2',
            'telefono3',
            'correoelectronico',
            'id_cliente',
            'identificadorcorto',
        ]


class CatalogoClasificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoClasificacion
        fields = ['id', 'nombreclasificacion', 'estatus']


class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'unidadmedida']


class PresentacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presentacion
        fields = ['id', 'nombrepresentacion', 'tipo']


class TipoCuentaContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCuentaContable
        fields = ['id', 'tipo', 'instancia']


class RegistroMaestroSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(allow_blank=True)
    tipo = serializers.CharField(allow_blank=True)
    id_clasificacion = serializers.IntegerField()
    marca = serializers.CharField(allow_blank=True, required=False, default='')
    estatus = serializers.CharField(allow_blank=True, required=False, default='1')


class RegMaestroUbicacionFisicaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    id_ubicacionfisica = serializers.IntegerField(
        source='idubicacionfisica',
        read_only=True,
    )
    existencias = serializers.IntegerField(allow_null=True, required=False)


class RegMaestroPedimentoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    tamanominimolote = serializers.IntegerField(allow_null=True, required=False)
    existenciasrequeridas = serializers.IntegerField(allow_null=True, required=False)
    plancompra = serializers.BooleanField(allow_null=True, required=False)


class RegMaestroCompraSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    id_presentacioncompra = serializers.IntegerField(
        source='idpresentacioncompra',
        allow_null=True,
        required=False,
    )
    id_presentacioninventario = serializers.IntegerField(
        source='idpresentacioninventario',
        allow_null=True,
        required=False,
    )
    equivalenciaentrepresentacion = serializers.IntegerField(
        allow_null=True,
        required=False,
    )
    id_unidadmedida = serializers.IntegerField(
        source='idunidadmedida',
        allow_null=True,
        required=False,
    )


class RegMaestroVentaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    id_presentacioninventario = serializers.IntegerField(
        source='idpresentacioninventario',
        allow_null=True,
        required=False,
    )
    id_presentacionconsumo = serializers.IntegerField(
        source='idpresentacionconsumo',
        allow_null=True,
        required=False,
    )
    equivalenciaentrepresentaciones = serializers.IntegerField(
        allow_null=True,
        required=False,
    )
    id_unidadmedida = serializers.IntegerField(
        source='idunidadmedida',
        allow_null=True,
        required=False,
    )


class RegMaestroInventarioSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    id_presentacioninventario = serializers.IntegerField(
        source='idpresentacioninventario',
        allow_null=True,
        required=False,
    )
    inventarioseguridad = serializers.IntegerField(allow_null=True, required=False)
    caducidad = serializers.IntegerField(allow_null=True, required=False)
    localidad = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )


class RegMaestroContabilidadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    id_perfilimpuesto = serializers.IntegerField(
        source='idperfilimpuesto',
        allow_null=True,
        required=False,
    )


class RegMaestroFotoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    id_registromaestro = serializers.IntegerField(
        source='idregistromaestro',
        read_only=True,
    )
    path_foto = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )


def _require_exists(model_class, pk, label):
    if pk is None:
        return
    if not model_class.objects.filter(id=pk).exists():
        raise serializers.ValidationError(
            '{0} with id {1} does not exist.'.format(label, pk)
        )


class LegacyCreateModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return create_legacy_instance(self.Meta.model, **validated_data)


class CuentaContableSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = CuentaContable
        fields = [
            'id',
            'nombre',
            'tipo',
            'id_cliente',
            'sub_tipo',
            'id_subcuentacontable',
        ]
        read_only_fields = ['id']


class ClaveFolioSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = ClaveFolio
        fields = [
            'id',
            'nombredocumento',
            'clavefolio',
            'id_clientesistema',
        ]
        read_only_fields = ['id']


class NumeracionFolioSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = NumeracionFolio
        fields = [
            'id',
            'id_clavefolio',
            'id_sucursal_sistema',
            'numeroinicial',
            'numerofinal',
            'numeroactual',
        ]
        read_only_fields = ['id', 'id_clavefolio']

    def validate(self, attrs):
        _require_exists(SucursalSistema, attrs.get('id_sucursal_sistema'), 'Sucursal')
        initial = attrs.get('numeroinicial')
        final = attrs.get('numerofinal')
        current = attrs.get('numeroactual')
        if initial is not None and final is not None and initial > final:
            raise serializers.ValidationError('numeroinicial cannot exceed numerofinal.')
        if current is not None and initial is not None and current < initial:
            raise serializers.ValidationError('numeroactual cannot be lower than numeroinicial.')
        if current is not None and final is not None and current > final:
            raise serializers.ValidationError('numeroactual cannot exceed numerofinal.')
        return attrs


class DocumentoMovimientoSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = DocumentoMovimiento
        fields = ['id', 'movimientodocumento']
        read_only_fields = ['id']


class DocumentoConceptoSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = DocumentoConcepto
        fields = [
            'id',
            'conceptodocumento',
            'id_subcuentacontablecargo',
            'id_clavefolio',
            'id_movimiento',
            'id_subcuentacontableabono',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        _require_exists(ClaveFolio, attrs.get('id_clavefolio'), 'ClaveFolio')
        _require_exists(DocumentoMovimiento, attrs.get('id_movimiento'), 'DocumentoMovimiento')
        return attrs


class AsientoContableSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = AsientoContable
        fields = [
            'id',
            'nombreclasificacion',
            'nombreasiento',
            'id_subcuentacontablecargo',
            'id_subcuentacontableabono',
            'montocalculado',
        ]
        read_only_fields = ['id']


class PersonaFiscalSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = PersonaFiscal
        fields = [
            'id',
            'nombre',
            'direccion',
            'telefono1',
            'telefono2',
            'telefono3',
            'correoelectronico',
            'personacontacto',
            'raz_n_social',
            'rfc',
            'domiciliofiscal',
            'tipo',
            'estatus',
            'fechanacimiento',
            'fechaaniversario',
            'cuentabancaria1',
            'banco1',
            'cuentabancaria2',
            'banco2',
            'cuentabancaria3',
            'banco3',
            'cuenta_contable',
        ]
        read_only_fields = ['id']


class ClienteSistemaSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = ClienteSistema
        fields = ['id', 'id_personafiscal']
        read_only_fields = ['id']

    def validate(self, attrs):
        _require_exists(PersonaFiscal, attrs.get('id_personafiscal'), 'PersonaFiscal')
        return attrs


class PersonafiscalProveedorSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = PersonafiscalProveedor
        fields = [
            'id',
            'id_personafiscal',
            'diascredito',
            'tiemposurtido',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        _require_exists(PersonaFiscal, attrs.get('id_personafiscal'), 'PersonaFiscal')
        return attrs


class DetalleDocumentoSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = DetalleDocumento
        fields = [
            'id',
            'id_documento',
            'id_registromaestro',
            'id_personafiscal',
            'id_ubicacionfisica1',
            'id_ubicacionfisica2',
            'subtotal',
            'comentarios',
            'estatus',
            'id_cuentabancaria1',
            'id_cuentabancaria2',
        ]
        read_only_fields = ['id', 'id_documento']

    def validate(self, attrs):
        _require_exists(RegistroMaestro, attrs.get('id_registromaestro'), 'RegistroMaestro')
        _require_exists(PersonaFiscal, attrs.get('id_personafiscal'), 'PersonaFiscal')
        _require_exists(UbicacionFisica, attrs.get('id_ubicacionfisica1'), 'UbicacionFisica')
        _require_exists(UbicacionFisica, attrs.get('id_ubicacionfisica2'), 'UbicacionFisica')

        request = self.context.get('request')
        if request is not None:
            require_ubicacion_scope(
                request.user,
                [attrs.get('id_ubicacionfisica1'), attrs.get('id_ubicacionfisica2')],
            )
        return attrs


class ExtradetalleDocumentoSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = ExtradetalleDocumento
        fields = [
            'id',
            'id_detalledocumento',
            'numerocomensales',
            'id_presentacion',
            'cantidad',
            'costopreciounitario',
            'costopreciototal',
            'cantidadsurtida',
            'fechahoraapertura',
            'fechahoracierre',
            'saldoapertura',
            'saldocierre',
        ]
        read_only_fields = ['id', 'id_detalledocumento']

    def validate(self, attrs):
        _require_exists(Presentacion, attrs.get('id_presentacion'), 'Presentacion')
        return attrs


class MovimientoContableSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = MovimientoContable
        fields = [
            'id',
            'id_librosucursal',
            'id_documento',
            'id_documentoconcepto',
        ]
        read_only_fields = ['id', 'id_documento']

    def validate(self, attrs):
        _require_exists(DocumentoConcepto, attrs.get('id_documentoconcepto'), 'DocumentoConcepto')
        return attrs


class DocumentoAsientoSerializer(LegacyCreateModelSerializer):
    class Meta:
        model = DocumentoAsiento
        fields = [
            'id',
            'id_clavefolio',
            'id_conceptodocumento',
            'id_movimientodocumento',
            'id_asiento',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        _require_exists(ClaveFolio, attrs.get('id_clavefolio'), 'ClaveFolio')
        _require_exists(DocumentoConcepto, attrs.get('id_conceptodocumento'), 'DocumentoConcepto')
        _require_exists(DocumentoMovimiento, attrs.get('id_movimientodocumento'), 'DocumentoMovimiento')
        _require_exists(AsientoContable, attrs.get('id_asiento'), 'AsientoContable')
        return attrs


class DocumentoSerializer(LegacyCreateModelSerializer):
    detalles = DetalleDocumentoSerializer(many=True, required=False)
    movimientos_contables = MovimientoContableSerializer(many=True, required=False)
    asientos = DocumentoAsientoSerializer(many=True, required=False)

    class Meta:
        model = Documento
        fields = [
            'id',
            'fecha_hora',
            'id_clavefolio',
            'id_usuario',
            'monto',
            'id_documentoorigen',
            'id_conceptodocumento',
            'foliointerno',
            'estatus',
            'id_documentomovimiento',
            'foliodocumento',
            'id_subcuentacontableabono',
            'detalles',
            'movimientos_contables',
            'asientos',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        _require_exists(ClaveFolio, attrs.get('id_clavefolio'), 'ClaveFolio')
        _require_exists(Documento, attrs.get('id_documentoorigen'), 'Documento')
        _require_exists(DocumentoConcepto, attrs.get('id_conceptodocumento'), 'DocumentoConcepto')
        _require_exists(DocumentoMovimiento, attrs.get('id_documentomovimiento'), 'DocumentoMovimiento')
        return attrs

    def create(self, validated_data):
        detalles = validated_data.pop('detalles', [])
        movimientos_contables = validated_data.pop('movimientos_contables', [])
        asientos = validated_data.pop('asientos', [])
        request = self.context.get('request')
        if request is not None and not validated_data.get('id_usuario'):
            validated_data['id_usuario'] = request.user.id
        return create_documento_with_children(
            validated_data,
            detalles=detalles,
            movimientos_contables=movimientos_contables,
            asientos=asientos,
        )

    def update(self, instance, validated_data):
        validated_data.pop('detalles', None)
        validated_data.pop('movimientos_contables', None)
        validated_data.pop('asientos', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['detalles'] = DetalleDocumentoSerializer(
            DetalleDocumento.objects.filter(id_documento=instance.id).order_by('id'),
            many=True,
            context=self.context,
        ).data
        data['movimientos_contables'] = MovimientoContableSerializer(
            MovimientoContable.objects.filter(id_documento=instance.id).order_by('id'),
            many=True,
            context=self.context,
        ).data
        data['asientos'] = DocumentoAsientoSerializer(
            DocumentoAsiento.objects.filter(
                id_clavefolio=instance.id_clavefolio,
                id_conceptodocumento=instance.id_conceptodocumento,
                id_movimientodocumento=instance.id_documentomovimiento,
            ).order_by('id'),
            many=True,
            context=self.context,
        ).data
        return data


class ComandaCreateSerializer(serializers.Serializer):
    id_sucursal = serializers.IntegerField(required=False, allow_null=True)
    id_mesa = serializers.IntegerField()
    id_mesero = serializers.IntegerField(required=False, allow_null=True)
    numero_comensales = serializers.IntegerField(required=False, min_value=1, default=1)
    tipo_orden = serializers.CharField(required=False, allow_blank=True, default='venta')


class ComandaUpdateSerializer(serializers.Serializer):
    numero_comensales = serializers.IntegerField(required=False, min_value=1)
    tipo_orden = serializers.CharField(required=False, allow_blank=True)
    estatus = serializers.CharField(required=False, allow_blank=True)


class ComandaItemCreateSerializer(serializers.Serializer):
    id_registromaestro = serializers.IntegerField()
    cantidad = serializers.DecimalField(
        max_digits=19,
        decimal_places=4,
        min_value=Decimal('0.0001'),
    )
    precio_unitario = serializers.DecimalField(max_digits=19, decimal_places=4, min_value=0)
    notas = serializers.CharField(required=False, allow_blank=True, default='')


class ComandaPaymentSerializer(serializers.Serializer):
    metodo_pago = serializers.CharField(required=False, allow_blank=True, default='efectivo')
    destino = serializers.CharField(required=False, allow_blank=True)
    monto = serializers.DecimalField(
        max_digits=19,
        decimal_places=4,
        min_value=Decimal('0.0001'),
    )
    id_caja = serializers.IntegerField(required=False, allow_null=True)
    id_cuenta_bancaria = serializers.IntegerField(required=False, allow_null=True)


class ComandaItemOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_comanda = serializers.IntegerField()
    id_detalledocumento = serializers.IntegerField()
    id_registromaestro = serializers.IntegerField()
    id_area_preparacion = serializers.IntegerField(allow_null=True)
    cantidad = serializers.CharField()
    precio_unitario = serializers.CharField()
    precio_total = serializers.CharField()
    notas = serializers.CharField(allow_blank=True)
    estatus = serializers.CharField()


class ComandaOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_documento = serializers.IntegerField()
    folio = serializers.CharField(allow_blank=True)
    id_sucursal = serializers.IntegerField()
    id_mesa = serializers.IntegerField()
    id_mesero = serializers.IntegerField(allow_null=True)
    numero_comensales = serializers.IntegerField()
    tipo_orden = serializers.CharField(allow_blank=True)
    estatus = serializers.CharField()
    monto = serializers.IntegerField(allow_null=True)
    items = ComandaItemOutputSerializer(many=True)


class ComandaItemCreateOutputSerializer(serializers.Serializer):
    item = ComandaItemOutputSerializer()
    warnings = serializers.ListField(child=serializers.DictField(), required=False)


class PreparacionOrdenItemOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_comandaitem = serializers.IntegerField()
    estatus = serializers.CharField()


class PreparacionOrdenOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_comanda = serializers.IntegerField()
    id_area_preparacion = serializers.IntegerField(allow_null=True)
    modo_salida = serializers.CharField(allow_blank=True)
    estatus = serializers.CharField()
    fecha_hora_apertura = serializers.DateTimeField(allow_null=True)
    fecha_hora_cierre = serializers.DateTimeField(allow_null=True)
    items = PreparacionOrdenItemOutputSerializer(many=True)


class PreparacionOrdenListOutputSerializer(serializers.Serializer):
    ordenes = PreparacionOrdenOutputSerializer(many=True)


class NotaVentaSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    folio = serializers.CharField(allow_blank=True)
    estatus = serializers.CharField()
    monto = serializers.IntegerField(allow_null=True)


class InventarioMovimientoOutputSerializer(serializers.Serializer):
    id_registromaestro = serializers.IntegerField()
    id_area_preparacion = serializers.IntegerField(allow_null=True)
    cantidad = serializers.IntegerField()
    existencias_antes = serializers.IntegerField()
    existencias_despues = serializers.IntegerField()


class ComandaCloseOutputSerializer(serializers.Serializer):
    comanda = ComandaOutputSerializer()
    nota_venta = NotaVentaSummarySerializer(allow_null=True)
    inventario = InventarioMovimientoOutputSerializer(many=True)


class NotaVentaPaymentOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_nota_venta = serializers.IntegerField()
    id_documento_pago = serializers.IntegerField()
    metodo_pago = serializers.CharField()
    destino = serializers.CharField()
    monto = serializers.CharField()
    estatus = serializers.CharField()
    nota_venta_estatus = serializers.CharField()
    saldo_pagado = serializers.IntegerField()
    saldo_pendiente = serializers.IntegerField()
    movimiento = serializers.DictField()
