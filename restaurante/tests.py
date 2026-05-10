from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.test import TestCase
from rest_framework.test import APIClient

from restaurante.factory.RegMaestro_factory import RegMaestro
from restaurante.models import (
    AuthUser_Sucursal,
    CatalogoClasificacion,
    CuentaContable,
    DetalleUbicacion,
    Presentacion,
    RegmaestroCompra,
    RegmaestroContabilidad,
    RegmaestroFoto,
    RegmaestroInventario,
    RegmaestroPedimento,
    RegmaestroUbicacionfisica,
    RegmaestroVenta,
    RegistroMaestro,
    SucursalSistema,
    TipoCuentaContable,
    UbicacionFisica,
    UnidadMedida,
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
            'RegMaestro_Compra': 100,
            'RegMaestro_Contabilidad': 100,
            'RegMaestro_Foto': 100,
            'RegMaestro_Inventario': 100,
            'RegMaestro_Pedimento': 100,
            'RegMaestro_UbicacionFisica': 100,
            'RegMaestro_Venta': 100,
            'Registro_Maestro': 100,
            'Sucursal_Sistema': 100,
            'Tipo_CuentaContable': 100,
            'Unidad_Medida': 100,
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


class APISkeletonTests(LegacyFixtureMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='api-user',
            password='secret',
        )

    def test_health_endpoint_is_public(self):
        response = self.client.get('/api/v1/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['service'], 'restaurante-api')

    def test_business_endpoints_require_authentication(self):
        response = self.client.get('/api/v1/sucursales/')

        self.assertIn(response.status_code, (401, 403))

    def test_sucursal_list_and_detail_endpoints(self):
        self.client.force_authenticate(user=self.user)

        list_response = self.client.get('/api/v1/sucursales/')
        detail_response = self.client.get('/api/v1/sucursales/1/')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(list_response.data[0]['nombre'], 'Sucursal Centro')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['identificadorcorto'], 'CEN')

    def test_catalog_endpoints_return_seeded_metadata(self):
        UnidadMedida.objects.create(id=1, unidadmedida='Kilogramo')
        Presentacion.objects.create(
            id=1,
            nombrepresentacion='Caja',
            tipo='Compra',
        )
        self.client.force_authenticate(user=self.user)

        endpoints = {
            '/api/v1/catalogos/clasificaciones/': 'nombreclasificacion',
            '/api/v1/catalogos/unidades-medida/': 'unidadmedida',
            '/api/v1/catalogos/presentaciones/': 'nombrepresentacion',
            '/api/v1/catalogos/tipos-cuenta-contable/': 'instancia',
        }

        for endpoint, expected_field in endpoints.items():
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data), 1)
            self.assertIn(expected_field, response.data[0])


class RegistroMaestroAPITests(LegacyFixtureMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='registro-api-user',
            password='secret',
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_registro_maestro_endpoints_require_authentication(self):
        response = self.client.get('/api/v1/registros-maestro/')

        self.assertIn(response.status_code, (401, 403))

    def test_registro_maestro_list_detail_create_and_patch(self):
        self.authenticate()

        list_response = self.client.get('/api/v1/registros-maestro/')
        detail_response = self.client.get('/api/v1/registros-maestro/1/')
        create_response = self.client.post(
            '/api/v1/registros-maestro/',
            {
                'nombre': 'Aguacate',
                'tipo': 'I',
                'id_clasificacion': 1,
                'marca': 'Campo',
            },
            format='json',
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['nombre'], 'Tomate')
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data['estatus'], '1')
        self.assertTrue(
            RegistroMaestro.objects.filter(
                id=create_response.data['id'],
                nombre='Aguacate',
            ).exists()
        )

        patch_response = self.client.patch(
            '/api/v1/registros-maestro/{0}/'.format(create_response.data['id']),
            {
                'marca': 'Campo premium',
                'estatus': '2',
            },
            format='json',
        )

        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data['nombre'], 'Aguacate')
        self.assertEqual(patch_response.data['marca'], 'Campo premium')
        self.assertEqual(patch_response.data['estatus'], '2')

    def test_registro_maestro_errors_map_to_api_responses(self):
        self.authenticate()

        missing_response = self.client.get('/api/v1/registros-maestro/999/')
        invalid_payload_response = self.client.post(
            '/api/v1/registros-maestro/',
            {
                'nombre': 'Sin clasificacion',
                'tipo': 'I',
            },
            format='json',
        )
        invalid_classification_response = self.client.post(
            '/api/v1/registros-maestro/',
            {
                'nombre': 'Clasificacion inexistente',
                'tipo': 'I',
                'id_clasificacion': 999,
            },
            format='json',
        )

        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(invalid_payload_response.status_code, 400)
        self.assertEqual(invalid_classification_response.status_code, 404)

    def test_registro_maestro_disable_endpoint_uses_domain_rules(self):
        self.authenticate()

        disabled_response = self.client.post('/api/v1/registros-maestro/2/disable/')

        self.assertEqual(disabled_response.status_code, 200)
        self.assertEqual(disabled_response.data['estatus'], 'C')
        self.assertEqual(RegistroMaestro.objects.get(id=2).estatus, 'C')

        RegmaestroUbicacionfisica.objects.filter(
            id_registromaestro=1,
            id_ubicacionfisica=3,
        ).update(existencias=5)
        blocked_response = self.client.post('/api/v1/registros-maestro/1/disable/')

        self.assertEqual(blocked_response.status_code, 400)
        self.assertIn('existencias', blocked_response.data['detail'])

    def test_registro_maestro_context_endpoints_upsert_and_read(self):
        Presentacion.objects.create(
            id=1,
            nombrepresentacion='Caja',
            tipo='Compra',
        )
        Presentacion.objects.create(
            id=2,
            nombrepresentacion='Pieza',
            tipo='Inventario',
        )
        UnidadMedida.objects.create(id=1, unidadmedida='Kilogramo')
        self.authenticate()

        cases = [
            (
                '/api/v1/registros-maestro/2/compra/',
                {
                    'id_presentacioncompra': 1,
                    'id_presentacioninventario': 2,
                    'equivalenciaentrepresentacion': 12,
                    'id_unidadmedida': 1,
                },
                'equivalenciaentrepresentacion',
                12,
                RegmaestroCompra,
            ),
            (
                '/api/v1/registros-maestro/2/venta/',
                {
                    'id_presentacioninventario': 2,
                    'id_presentacionconsumo': 1,
                    'equivalenciaentrepresentaciones': 6,
                    'id_unidadmedida': 1,
                },
                'equivalenciaentrepresentaciones',
                6,
                RegmaestroVenta,
            ),
            (
                '/api/v1/registros-maestro/2/inventario/',
                {
                    'id_presentacioninventario': 2,
                    'inventarioseguridad': 8,
                    'caducidad': 30,
                    'localidad': 'Almacen norte',
                },
                'localidad',
                'Almacen norte',
                RegmaestroInventario,
            ),
            (
                '/api/v1/registros-maestro/2/contabilidad/',
                {
                    'id_perfilimpuesto': 3,
                },
                'id_perfilimpuesto',
                3,
                RegmaestroContabilidad,
            ),
            (
                '/api/v1/registros-maestro/2/pedimento/',
                {
                    'tamanominimolote': 4,
                    'existenciasrequeridas': 9,
                    'plancompra': True,
                },
                'existenciasrequeridas',
                9,
                RegmaestroPedimento,
            ),
            (
                '/api/v1/registros-maestro/2/foto/',
                {
                    'path_foto': '/media/registros/cebolla.png',
                },
                'path_foto',
                '/media/registros/cebolla.png',
                RegmaestroFoto,
            ),
            (
                '/api/v1/registros-maestro/2/ubicaciones/1/',
                {
                    'existencias': 14,
                },
                'existencias',
                14,
                RegmaestroUbicacionfisica,
            ),
        ]

        for endpoint, payload, field, expected_value, model in cases:
            put_response = self.client.put(endpoint, payload, format='json')
            get_response = self.client.get(endpoint)

            self.assertEqual(put_response.status_code, 201)
            self.assertEqual(put_response.data[field], expected_value)
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(get_response.data[field], expected_value)
            self.assertTrue(model.objects.filter(id_registromaestro=2).exists())

    def test_registro_maestro_context_put_updates_existing_resource(self):
        self.authenticate()

        response = self.client.put(
            '/api/v1/registros-maestro/1/pedimento/',
            {
                'tamanominimolote': 25,
                'existenciasrequeridas': 40,
                'plancompra': False,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tamanominimolote'], 25)
        pedimento = RegmaestroPedimento.objects.get(id_registromaestro=1)
        self.assertEqual(pedimento.tamanominimolote, 25)
        self.assertEqual(pedimento.existenciasrequeridas, 40)
        self.assertFalse(pedimento.plancompra)
