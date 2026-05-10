from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.test import TestCase

from restaurante.factory.RegMaestro_factory import RegMaestro
from restaurante.models import (
    AuthUser_Sucursal,
    CatalogoClasificacion,
    CuentaContable,
    DetalleUbicacion,
    RegmaestroPedimento,
    RegmaestroUbicacionfisica,
    RegistroMaestro,
    SucursalSistema,
    TipoCuentaContable,
    UbicacionFisica,
)
from restaurante.repository.AreaPreparacion_repository import AreaPreparacion
from restaurante.repository.Ubicacion_repository import UbicacionFisica_Repo


class LegacyFixtureMixin(object):
    @classmethod
    def setUpTestData(cls):
        TipoCuentaContable.objects.create(
            id=1,
            tipo=1,
            instancia='AreaPreparacion',
        )
        TipoCuentaContable.objects.create(
            id=2,
            tipo=2,
            instancia='Mesa',
        )
        SucursalSistema.objects.create(
            id=1,
            nombre='Sucursal Centro',
            direccion='Centro',
            personacontacto='Contacto',
            telefono1='555-0001',
            telefono2='',
            telefono3='',
            correoelectronico='centro@example.com',
            id_cliente=1,
            identificadorcorto='CEN',
        )
        SucursalSistema.objects.create(
            id=2,
            nombre='Sucursal Norte',
            direccion='Norte',
            personacontacto='Contacto',
            telefono1='555-0002',
            telefono2='',
            telefono3='',
            correoelectronico='norte@example.com',
            id_cliente=1,
            identificadorcorto='NOR',
        )
        CuentaContable.objects.create(
            id=1,
            nombre='Cuenta padre',
            tipo=1,
            id_cliente=1,
            sub_tipo='1',
            id_subcuentacontable=None,
        )
        CatalogoClasificacion.objects.create(
            id=1,
            nombreclasificacion='Insumos',
            estatus='1',
        )
        RegistroMaestro.objects.create(
            id=1,
            nombre='Tomate',
            tipo='I',
            id_clasificacion=1,
            marca='Generica',
            estatus='1',
        )
        RegistroMaestro.objects.create(
            id=2,
            nombre='Cebolla',
            tipo='I',
            id_clasificacion=1,
            marca='Generica',
            estatus='1',
        )
        UbicacionFisica.objects.create(
            id=1,
            id_sucursalsistema=1,
            nombre='Area activa',
            descripcion='Area de preparacion',
            tipo='1',
            default=False,
            id_subcuentacontable=None,
            estatus='1',
            cuenta_contable=1,
        )
        UbicacionFisica.objects.create(
            id=2,
            id_sucursalsistema=1,
            nombre='Area secundaria',
            descripcion='Area de preparacion secundaria',
            tipo='1',
            default=False,
            id_subcuentacontable=None,
            estatus='1',
            cuenta_contable=1,
        )
        UbicacionFisica.objects.create(
            id=3,
            id_sucursalsistema=1,
            nombre='Mesa uno',
            descripcion='No es area de preparacion',
            tipo='2',
            default=False,
            id_subcuentacontable=None,
            estatus='1',
            cuenta_contable=1,
        )
        DetalleUbicacion.objects.create(
            id=1,
            id_ubicacionfisica=1,
            direccion='Centro',
            telefono='555-0001',
            horariorecepcion='08:00-18:00',
            saldoactual=0,
            impresora='',
            terminalsalida='TERM-1',
            minimocomensales='',
            maximocomensales='',
            tipo='',
        )
        RegmaestroUbicacionfisica.objects.create(
            id=1,
            id_registromaestro=1,
            id_ubicacionfisica=3,
            existencias=0,
        )
        RegmaestroPedimento.objects.create(
            id=1,
            id_registromaestro=1,
            tamanominimolote=10,
            existenciasrequeridas=20,
            plancompra=True,
        )
        AuthUser_Sucursal.objects.create(id=1, user=1, sucursal=1)
        cls._sync_sequences()

    @classmethod
    def _sync_sequences(cls):
        if connection.vendor != 'postgresql':
            return

        sequence_values = {
            'AuthUser_Sucursal': 100,
            'Catalogo_Clasificacion': 100,
            'Cuenta_Contable': 100,
            'Detalle_Ubicacion': 100,
            'RegMaestro_Pedimento': 100,
            'RegMaestro_UbicacionFisica': 100,
            'Registro_Maestro': 100,
            'Sucursal_Sistema': 100,
            'Tipo_CuentaContable': 100,
            'Ubicacion_Fisica': 100,
        }
        with connection.cursor() as cursor:
            for table_name, value in sequence_values.items():
                sequence_name = connection.ops.quote_name(
                    '{0}_ID_seq'.format(table_name)
                )
                cursor.execute(
                    'SELECT setval(%s::regclass, %s, true)',
                    [sequence_name, value],
                )


class UFRepo_Validacion(LegacyFixtureMixin, TestCase):
    def test_uf_sucursalvalida(self):
        area = AreaPreparacion()
        area.sucursal = 666
        self.assertRaises(ObjectDoesNotExist, area.save)

    def test_uf_sucursalnoexiste(self):
        area = AreaPreparacion()
        area.sucursal = None
        self.assertRaises(ValueError, area.save)

    def test_uf_usuarioinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ObjectDoesNotExist, area.user, 999, 'add')

    def test_uf_usuarionoasociado(self):
        area = AreaPreparacion()
        area.get(1)
        self.assertRaises(ObjectDoesNotExist, area.user, 2, 'add')

    def test_uf_comandoinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ValueError, area.user, 1, 'xxx')

    def test_uf_ufinvalida(self):
        area = AreaPreparacion()
        self.assertRaises(ObjectDoesNotExist, area.get, 999)

    def test_uf_tipoinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ValueError, area.get, 3)

    def test_uf_regmaestroinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ObjectDoesNotExist, area.get_stock, 999)

    def test_uf_regmaestronoasociado(self):
        area = AreaPreparacion()
        area.get(1)
        self.assertRaises(ObjectDoesNotExist, area.get_stock, 2)

    def test_uf_getstatus(self):
        self.assertEqual(UbicacionFisica_Repo.get_status(1), '1')

    def test_uf_getstatusinvalido(self):
        self.assertRaises(ObjectDoesNotExist, UbicacionFisica_Repo.get_status, 999)

    def test_uf_setstatusinvalido(self):
        self.assertRaises(ObjectDoesNotExist, UbicacionFisica_Repo.set_status, 999, 2)

    def test_uf_setstatus(self):
        self.assertEqual(UbicacionFisica_Repo.set_status(1, 2), '2')
        self.assertEqual(UbicacionFisica_Repo.get_status(1), '2')

    def test_area_save_preserves_ubicacion_identity(self):
        area = AreaPreparacion()
        area.nombre = 'Nueva area'
        area.descripcion = 'Area creada por prueba'
        area.sucursal = 1
        area.terminalsalida = 'TERM-2'
        area.telefono = '555-2222'
        area.horariorecepcion = '09:00-17:00'

        area.save()

        self.assertTrue(UbicacionFisica.objects.filter(id=area.id).exists())
        self.assertTrue(
            DetalleUbicacion.objects.filter(id_ubicacionfisica=area.id).exists()
        )


class RegMas_Validacion(LegacyFixtureMixin, TestCase):
    def test_regmas_invalido(self):
        regmaestro = RegMaestro()
        self.assertRaises(ObjectDoesNotExist, regmaestro.get, 999)

    def test_regmas_clasific(self):
        regmaestro = RegMaestro()
        regmaestro.id_clasificacion = 999
        regmaestro.marca = 'marca'
        regmaestro.nombre = 'nombre'
        self.assertRaises(ObjectDoesNotExist, regmaestro.save)

    def test_regmas_uf_invalida_save(self):
        regmaestro = RegMaestro()
        contexto = regmaestro.contexto(regmaestro, 'UbicacionFisica')
        contexto.idubicacionfisica = 999
        self.assertRaises(ObjectDoesNotExist, contexto.save)

    def test_regmas_uf_invalida_get(self):
        regmaestro = RegMaestro()
        contexto = regmaestro.contexto(regmaestro, 'UbicacionFisica')
        self.assertRaises(ObjectDoesNotExist, contexto.get, 999)

    def test_regmas_uf_change_uf(self):
        regmaestro = RegMaestro()
        regmaestro.get(1)
        contexto = regmaestro.contexto(regmaestro, 'UbicacionFisica')
        contexto.get(3)
        contexto.idubicacionfisica = 2
        self.assertRaises(ValueError, contexto.save)

    def test_regmas_uf_change_rm(self):
        regmaestro = RegMaestro()
        regmaestro.get(1)
        contexto = regmaestro.contexto(regmaestro, 'UbicacionFisica')
        contexto.get(3)
        contexto.idregistromaestro = 2
        self.assertRaises(ValueError, contexto.save)

    def test_regmas_uf_many_uf(self):
        regmaestro = RegMaestro()
        regmaestro.get(1)
        contexto = regmaestro.contexto(regmaestro, 'UbicacionFisica')
        contexto.idubicacionfisica = 3
        self.assertRaises(ValueError, contexto.save)

    def test_regmas_ped_change_rm(self):
        regmaestro = RegMaestro()
        regmaestro.get(1)
        contexto = regmaestro.contexto(regmaestro, 'Pedimento')
        contexto.get(1)
        contexto.idregistromaestro = 2
        self.assertRaises(ValueError, contexto.save)

    def test_regmas_ped_many_rm(self):
        regmaestro = RegMaestro()
        contexto = regmaestro.contexto(regmaestro, 'Pedimento')
        contexto.idregistromaestro = 1
        self.assertRaises(ValueError, contexto.save)

    def test_regmas_ped_update_keeps_registro_maestro(self):
        regmaestro = RegMaestro()
        regmaestro.get(1)
        contexto = regmaestro.contexto(regmaestro, 'Pedimento')
        contexto.get(1)
        contexto.tamanominimolote = 30

        contexto.save()

        pedimento = RegmaestroPedimento.objects.get(id=1)
        self.assertEqual(pedimento.id_registromaestro, 1)
        self.assertEqual(pedimento.tamanominimolote, 30)
