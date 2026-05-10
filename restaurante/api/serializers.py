from rest_framework import serializers

from restaurante.models import (
    CatalogoClasificacion,
    Presentacion,
    RegistroMaestro,
    SucursalSistema,
    TipoCuentaContable,
    UnidadMedida,
)


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

    class Meta:
        model = RegistroMaestro
        fields = [
            'id',
            'nombre',
            'tipo',
            'id_clasificacion',
            'marca',
            'estatus',
        ]


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
