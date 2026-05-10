from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.test import TestCase
from rest_framework.test import APIClient

from restaurante.factory.RegMaestro_factory import RegMaestro
from restaurante.models import (
    AsientoContable,
    AuthUser_Sucursal,
    AuthUser_UbicacionFisica,
    CatalogoClasificacion,
    ClaveFolio,
    ClienteSistema,
    CuentaContable,
    DetalleUbicacion,
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
        PersonaFiscal.objects.create(
            id=1,
            nombre='Proveedor Fiscal',
            direccion='Centro',
            telefono1='555-1000',
            telefono2='',
            telefono3='',
            correoelectronico='proveedor@example.com',
            personacontacto='Contacto Fiscal',
            raz_n_social='Proveedor Fiscal SA',
            rfc='PFS010101AAA',
            domiciliofiscal='Centro',
            tipo='Proveedor',
            estatus='1',
        )
        ClienteSistema.objects.create(id=1, id_personafiscal=1)
        PersonafiscalProveedor.objects.create(
            id=1,
            id_personafiscal=1,
            diascredito=15,
            tiemposurtido=2,
        )
        ClaveFolio.objects.create(
            id=1,
            nombredocumento='Compra',
            clavefolio='COM',
            id_clientesistema=1,
        )
        DocumentoMovimiento.objects.create(id=1, movimientodocumento='Entrada')
        DocumentoConcepto.objects.create(
            id=1,
            conceptodocumento='Compra insumos',
            id_subcuentacontablecargo=1,
            id_clavefolio=1,
            id_movimiento=1,
            id_subcuentacontableabono=1,
        )
        AsientoContable.objects.create(
            id=1,
            nombreclasificacion='Compras',
            nombreasiento='Cargo inventario',
            id_subcuentacontablecargo=1,
            id_subcuentacontableabono=1,
            montocalculado=True,
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
        AuthUser_UbicacionFisica.objects.create(id=1, user=1, ubicacionfisica=1)
        AuthUser_UbicacionFisica.objects.create(id=2, user=1, ubicacionfisica=3)
        cls._sync_sequences()

    @classmethod
    def _sync_sequences(cls):
        if connection.vendor != 'postgresql':
            return

        sequence_values = {
            'Asiento_Contable': 100,
            'AuthUser_Sucursal': 100,
            'AuthUser_UbicacionFisica': 100,
            'Catalogo_Clasificacion': 100,
            'Cliente_Sistema': 100,
            'Cuenta_Contable': 100,
            'Detalle_Documento': 100,
            'Detalle_Ubicacion': 100,
            'Documento': 100,
            'Documento_Asiento': 100,
            'Documento_Concepto': 100,
            'Documento_Movimiento': 100,
            'ExtraDetalle_Documento': 100,
            'Movimiento_Contable': 100,
            'Numeracion_Folio': 100,
            'Persona_Fiscal': 100,
            'PersonaFiscal_Proveedor': 100,
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
        AuthUser_Sucursal.objects.create(id=201, user=self.user.id, sucursal=1)

    def test_health_endpoint_is_public(self):
        response = self.client.get('/api/v1/health/', HTTP_X_REQUEST_ID='test-request-id')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['service'], 'restaurante-api')
        self.assertEqual(response['X-Request-ID'], 'test-request-id')

    def test_business_endpoints_require_authentication(self):
        response = self.client.get('/api/v1/sucursales/')

        self.assertIn(response.status_code, (401, 403))

    def test_sucursal_list_and_detail_endpoints(self):
        self.client.force_authenticate(user=self.user)

        list_response = self.client.get('/api/v1/sucursales/')
        detail_response = self.client.get('/api/v1/sucursales/1/')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 1)
        self.assertEqual(list_response.data['results'][0]['nombre'], 'Sucursal Centro')
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
            self.assertGreaterEqual(len(response.data['results']), 1)
            self.assertIn(expected_field, response.data['results'][0])

    def test_schema_endpoint_exposes_openapi_contract(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/schema/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['info']['title'], 'Restaurante API')
        self.assertIn('/api/v1/documentos/', response.data['paths'])


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
        self.assertEqual(list_response.data['count'], 2)
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


class TransactionalAPITests(LegacyFixtureMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='transaction-api-user',
            password='secret',
        )
        AuthUser_Sucursal.objects.create(id=101, user=self.user.id, sucursal=1)
        AuthUser_UbicacionFisica.objects.create(
            id=101,
            user=self.user.id,
            ubicacionfisica=1,
        )
        AuthUser_UbicacionFisica.objects.create(
            id=102,
            user=self.user.id,
            ubicacionfisica=3,
        )
        self.client.force_authenticate(user=self.user)

    def test_documento_create_is_atomic_and_returns_nested_transaction_rows(self):
        response = self.client.post(
            '/api/v1/documentos/',
            {
                'id_clavefolio': 1,
                'id_conceptodocumento': 1,
                'id_documentomovimiento': 1,
                'foliointerno': 'TMP-1',
                'foliodocumento': 'COM-101',
                'detalles': [
                    {
                        'id_registromaestro': 1,
                        'id_personafiscal': 1,
                        'id_ubicacionfisica1': 1,
                        'id_ubicacionfisica2': 3,
                        'subtotal': 125,
                        'comentarios': 'Compra de prueba',
                        'estatus': '1',
                    },
                ],
                'movimientos_contables': [
                    {
                        'id_librosucursal': 1,
                        'id_documentoconcepto': 1,
                    },
                ],
                'asientos': [
                    {
                        'id_asiento': 1,
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['monto'], 125)
        self.assertEqual(response.data['id_usuario'], self.user.id)
        self.assertEqual(len(response.data['detalles']), 1)
        self.assertEqual(len(response.data['movimientos_contables']), 1)
        self.assertEqual(len(response.data['asientos']), 1)
        self.assertTrue(Documento.objects.filter(id=response.data['id']).exists())
        self.assertTrue(
            DetalleDocumento.objects.filter(
                id_documento=response.data['id'],
                subtotal=125,
            ).exists()
        )
        self.assertTrue(
            MovimientoContable.objects.filter(id_documento=response.data['id']).exists()
        )
        self.assertTrue(DocumentoAsiento.objects.filter(id_asiento=1).exists())

    def test_documento_create_rolls_back_when_child_validation_fails(self):
        before_count = Documento.objects.count()

        response = self.client.post(
            '/api/v1/documentos/',
            {
                'id_clavefolio': 1,
                'id_conceptodocumento': 1,
                'id_documentomovimiento': 1,
                'detalles': [
                    {
                        'id_registromaestro': 999,
                        'subtotal': 50,
                        'estatus': '1',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'validation_error')
        self.assertEqual(Documento.objects.count(), before_count)

    def test_documento_child_endpoints_enforce_scope_and_support_search(self):
        documento = Documento.objects.create(
            id=1,
            id_clavefolio=1,
            id_usuario=self.user.id,
            monto=80,
            id_conceptodocumento=1,
            foliointerno='TMP-2',
            estatus='1',
            id_documentomovimiento=1,
            foliodocumento='COM-102',
        )

        allowed_response = self.client.post(
            '/api/v1/documentos/{0}/detalles/'.format(documento.id),
            {
                'id_registromaestro': 1,
                'id_personafiscal': 1,
                'id_ubicacionfisica1': 1,
                'subtotal': 80,
                'comentarios': 'Salsa verde',
                'estatus': '1',
            },
            format='json',
        )
        blocked_response = self.client.post(
            '/api/v1/documentos/{0}/detalles/'.format(documento.id),
            {
                'id_registromaestro': 1,
                'id_personafiscal': 1,
                'id_ubicacionfisica1': 2,
                'subtotal': 20,
                'comentarios': 'Sin permiso',
                'estatus': '1',
            },
            format='json',
        )
        search_response = self.client.get(
            '/api/v1/documentos/{0}/detalles/?search=Salsa'.format(documento.id)
        )

        self.assertEqual(allowed_response.status_code, 201)
        self.assertEqual(blocked_response.status_code, 403)
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.data['count'], 1)
        self.assertEqual(search_response.data['results'][0]['comentarios'], 'Salsa verde')

    def test_folios_personas_proveedores_clientes_and_cuentas_endpoints(self):
        folio_response = self.client.post(
            '/api/v1/folios/',
            {
                'nombredocumento': 'Venta',
                'clavefolio': 'VEN',
                'id_clientesistema': 1,
            },
            format='json',
        )
        numeracion_response = self.client.post(
            '/api/v1/folios/{0}/numeraciones/'.format(folio_response.data['id']),
            {
                'id_sucursal_sistema': 1,
                'numeroinicial': 1,
                'numerofinal': 500,
                'numeroactual': 1,
            },
            format='json',
        )
        persona_response = self.client.post(
            '/api/v1/personas-fiscales/',
            {
                'nombre': 'Cliente Fiscal',
                'direccion': 'Norte',
                'telefono1': '555-2000',
                'correoelectronico': 'cliente@example.com',
                'personacontacto': 'Cliente',
                'raz_n_social': 'Cliente Fiscal SA',
                'rfc': 'CFS010101AAA',
                'domiciliofiscal': 'Norte',
                'tipo': 'Cliente',
                'estatus': '1',
            },
            format='json',
        )
        cliente_response = self.client.post(
            '/api/v1/clientes/',
            {'id_personafiscal': persona_response.data['id']},
            format='json',
        )
        proveedor_response = self.client.post(
            '/api/v1/proveedores/',
            {
                'id_personafiscal': persona_response.data['id'],
                'diascredito': 30,
                'tiemposurtido': 4,
            },
            format='json',
        )
        cuenta_response = self.client.post(
            '/api/v1/cuentas-contables/',
            {
                'nombre': 'Inventario nuevo',
                'tipo': 1,
                'id_cliente': 1,
                'sub_tipo': '1',
            },
            format='json',
        )

        self.assertEqual(folio_response.status_code, 201)
        self.assertEqual(numeracion_response.status_code, 201)
        self.assertEqual(persona_response.status_code, 201)
        self.assertEqual(cliente_response.status_code, 201)
        self.assertEqual(proveedor_response.status_code, 201)
        self.assertEqual(cuenta_response.status_code, 201)
        self.assertTrue(NumeracionFolio.objects.filter(id_clavefolio=folio_response.data['id']).exists())
        self.assertTrue(ClienteSistema.objects.filter(id=cliente_response.data['id']).exists())
        self.assertTrue(
            PersonafiscalProveedor.objects.filter(
                id=proveedor_response.data['id'],
                diascredito=30,
            ).exists()
        )
