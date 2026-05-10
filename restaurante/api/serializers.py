from rest_framework import serializers

from restaurante.models import (
    CatalogoClasificacion,
    Presentacion,
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
