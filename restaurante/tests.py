from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, connection, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from restaurante.database_config import FLOW_FOLIO_CONFIG, ensure_flow_folio_config
from restaurante.factory.RegMaestro_factory import RegMaestro
from restaurante.models import (
    AsientoContable,
    AuthUser_Sucursal,
    AuthUser_UbicacionFisica,
    CatalogoClasificacion,
    ClaveFolio,
    ClienteSistema,
    Comanda,
    ComandaItem,
    ConfiguracionComanda,
    CuentaBancaria,
    CuentaContable,
    DetalleUbicacion,
    DetalleDocumento,
    Documento,
    DocumentoAsiento,
    DocumentoConcepto,
    DocumentoMovimiento,
    ExtradetalleDocumento,
    LibroContable,
    LibroSucursal,
    MontoCalculado,
    MontoCalculadoDetalle,
    MovimientoContable,
    NumeracionFolio,
    PagoCliente,
    PerfilImpuesto,
    PerfilimpuestoMontocalculado,
    PersonaFiscal,
    PersonafiscalProveedor,
    PreparacionOrden,
    PreparacionOrdenItem,
    Presentacion,
    RecetaItem,
    RegmaestroCompra,
    RegmaestroContabilidad,
    RegmaestroFoto,
    RegmaestroInventario,
    RegmaestroPedimento,
    RegmaestroUbicacionfisica,
    RegmaestroVenta,
    ReglaRuteoPreparacion,
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


class FlowFolioConfigEmptyDatabaseTests(TestCase):
    def test_flow_folio_config_dry_run_reports_empty_database_bootstrap(self):
        summary = ensure_flow_folio_config(dry_run=True)

        self.assertEqual(summary['cliente_sistema'], 1)
        self.assertEqual(summary['sucursal_sistema'], 1)
        self.assertEqual(summary['clave_folio'], len(FLOW_FOLIO_CONFIG))
        self.assertEqual(summary['numeracion_folio'], len(FLOW_FOLIO_CONFIG))
        self.assertFalse(ClienteSistema.objects.exists())
        self.assertFalse(SucursalSistema.objects.exists())
        self.assertFalse(ClaveFolio.objects.exists())
        self.assertFalse(NumeracionFolio.objects.exists())

    def test_seed_flow_folio_config_can_bootstrap_empty_database(self):
        call_command('seed_flow_folio_config', verbosity=0)

        self.assertEqual(ClienteSistema.objects.count(), 1)
        self.assertEqual(SucursalSistema.objects.count(), 1)
        self.assertEqual(
            ClaveFolio.objects.filter(
                nombredocumento__in=[
                    nombre_documento
                    for nombre_documento, _clave_folio in FLOW_FOLIO_CONFIG
                ]
            ).count(),
            len(FLOW_FOLIO_CONFIG),
        )
        self.assertEqual(NumeracionFolio.objects.count(), len(FLOW_FOLIO_CONFIG))


class FlowFolioConfigTests(LegacyFixtureMixin, TestCase):
    def test_seed_flow_folio_config_creates_required_flow_rows(self):
        call_command('seed_flow_folio_config', verbosity=0)

        for nombre_documento, clave_folio in FLOW_FOLIO_CONFIG:
            folio = ClaveFolio.objects.get(
                nombredocumento=nombre_documento,
                id_clientesistema=1,
            )
            self.assertEqual(folio.clavefolio, clave_folio)
            self.assertTrue(
                NumeracionFolio.objects.filter(
                    id_clavefolio=folio.id,
                    id_sucursal_sistema=1,
                ).exists()
            )
            self.assertTrue(
                NumeracionFolio.objects.filter(
                    id_clavefolio=folio.id,
                    id_sucursal_sistema=2,
                ).exists()
            )

    def test_seeded_flow_folios_support_database_folio_generation(self):
        call_command('install_database_logic', verbosity=0)
        call_command('seed_flow_folio_config', verbosity=0)

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT folio, id_clave_folio, id_numeracion_folio '
                'FROM generar_nuevofolio(%s, %s)',
                ['Flujo_Almacen', 1],
            )
            folio, id_clave_folio, id_numeracion_folio = cursor.fetchone()

        self.assertTrue(folio.startswith('FAL_CEN_1/'))
        self.assertEqual(
            ClaveFolio.objects.get(id=id_clave_folio).nombredocumento,
            'Flujo_Almacen',
        )
        self.assertEqual(
            NumeracionFolio.objects.get(id=id_numeracion_folio).numeroactual,
            2,
        )


class ComandaFlowConfigTests(TestCase):
    def test_seed_comanda_flow_config_bootstraps_minimal_demo_flow(self):
        call_command('seed_comanda_flow_config', verbosity=0)

        self.assertTrue(ConfiguracionComanda.objects.exists())
        self.assertTrue(ReglaRuteoPreparacion.objects.exists())
        self.assertTrue(RecetaItem.objects.exists())
        self.assertTrue(
            ClaveFolio.objects.filter(nombredocumento='Orden Comanda').exists()
        )
        self.assertTrue(
            ClaveFolio.objects.filter(nombredocumento='Nota de Venta').exists()
        )
        self.assertTrue(
            ClaveFolio.objects.filter(nombredocumento='Pago Cliente').exists()
        )


class DatabaseLogicWorkflowTests(LegacyFixtureMixin, TestCase):
    def setUp(self):
        call_command('install_database_logic', verbosity=0)
        call_command('seed_database_logic_config', verbosity=0)
        self._ensure_workflow_resources()

    def _ensure_workflow_resources(self):
        DocumentoConcepto.objects.filter(id=1).update(
            id_subcuentacontablecargo=1,
            id_subcuentacontableabono=2,
        )
        if not CuentaBancaria.objects.filter(id=1).exists():
            CuentaBancaria.objects.create(
                id=1,
                nombrebanco='Banco pruebas',
                tipocuenta='Cheques',
                moneda='MXN',
                id_subcuentacontable=1,
                saldo=100,
            )
        if not Presentacion.objects.filter(id=1).exists():
            Presentacion.objects.create(
                id=1,
                nombrepresentacion='Pieza',
                tipo='Inventario',
            )

    def _legacy_id(self, table_name):
        with connection.cursor() as cursor:
            cursor.execute('SELECT restaurante_next_legacy_id(%s)', [table_name])
            return cursor.fetchone()[0]

    def _scalar(self, sql, params=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])
            return cursor.fetchone()[0]

    def _create_documento(self, movement_id=1, concepto_id=1, monto=None):
        documento_id = self._scalar(
            'SELECT crear_documento(%s, %s, %s, NULL, %s, %s)',
            [1, 'Operacion_DB', 1, concepto_id, movement_id],
        )
        if monto is not None:
            Documento.objects.filter(id=documento_id).update(monto=monto)
        return documento_id

    def _add_detalle(self, documento_id, **overrides):
        values = {
            'id': self._legacy_id('Detalle_Documento'),
            'id_documento': documento_id,
            'id_registromaestro': 1,
            'id_personafiscal': 1,
            'id_ubicacionfisica1': None,
            'id_ubicacionfisica2': None,
            'subtotal': 0,
            'comentarios': 'detalle db logic',
            'estatus': '1',
            'id_cuentabancaria1': None,
            'id_cuentabancaria2': None,
        }
        values.update(overrides)
        return DetalleDocumento.objects.create(**values)

    def _add_extra(self, detalle, **overrides):
        values = {
            'id': self._legacy_id('ExtraDetalle_Documento'),
            'id_detalledocumento': detalle.id,
            'numerocomensales': 0,
            'id_presentacion': 1,
            'cantidad': 0,
            'costopreciounitario': 0,
            'costopreciototal': 0,
            'cantidadsurtida': 0,
            'saldoapertura': 0,
            'saldocierre': 0,
        }
        values.update(overrides)
        return ExtradetalleDocumento.objects.create(**values)

    def test_document_lifecycle_functions_create_recalculate_and_close(self):
        documento_id = self._create_documento(movement_id=1, concepto_id=1)
        self._add_detalle(documento_id, subtotal=80)

        total = self._scalar('SELECT recalcular_documento(%s)', [documento_id])
        closed = self._scalar('SELECT cerrar_documento(%s)', [documento_id])

        documento = Documento.objects.get(id=documento_id)
        self.assertEqual(total, 80)
        self.assertTrue(closed)
        self.assertEqual(documento.monto, 80)
        self.assertEqual(documento.estatus, 'C')
        self.assertTrue(documento.foliodocumento.startswith('ODB_CEN_'))

    def test_inventory_entry_and_exit_update_lots_stock_and_generated_documents(self):
        entrada_id = self._create_documento(movement_id=1, concepto_id=1)
        entrada_detalle = self._add_detalle(
            entrada_id,
            id_ubicacionfisica1=1,
            subtotal=100,
        )
        self._add_extra(
            entrada_detalle,
            cantidad=5,
            costopreciounitario=20,
            costopreciototal=100,
        )

        self._scalar('SELECT aplicar_movimientoalmacen(%s, %s)', [entrada_id, 1])

        stock = RegmaestroUbicacionfisica.objects.get(
            id_registromaestro=1,
            id_ubicacionfisica=1,
        )
        self.assertEqual(stock.existencias, 5)
        self.assertTrue(
            Documento.objects.filter(
                id_documentoorigen=entrada_id,
                estatus='C',
            ).exists()
        )

        salida_id = self._create_documento(movement_id=2, concepto_id=2)
        salida_detalle = self._add_detalle(
            salida_id,
            id_ubicacionfisica1=1,
            id_ubicacionfisica2=1,
            subtotal=0,
        )
        self._add_extra(salida_detalle, cantidad=3)

        self._scalar('SELECT aplicar_movimientoalmacen(%s, %s)', [salida_id, 1])

        stock.refresh_from_db()
        self.assertEqual(stock.existencias, 2)
        self.assertTrue(
            ExtradetalleDocumento.objects.filter(
                id_detalledocumento__in=DetalleDocumento.objects.filter(
                    id_documento__in=Documento.objects.filter(
                        id_documentoorigen=entrada_id,
                    ).values('id')
                ).values('id'),
                saldocierre=2,
            ).exists()
        )
        self.assertGreaterEqual(
            Documento.objects.filter(id_documentoorigen__in=[entrada_id, salida_id]).count(),
            2,
        )

    def test_cash_and_bank_movements_update_balances_and_accounting(self):
        caja_id = self._create_documento(movement_id=1, concepto_id=1)
        self._add_detalle(
            caja_id,
            id_ubicacionfisica1=1,
            subtotal=40,
        )

        self._scalar('SELECT aplicar_movimientocaja(%s)', [caja_id])

        detalle_ubicacion = DetalleUbicacion.objects.get(id_ubicacionfisica=1)
        self.assertEqual(detalle_ubicacion.saldoactual, 40)
        self.assertTrue(Documento.objects.filter(id_documentoorigen=caja_id).exists())

        banco_id = self._create_documento(movement_id=2, concepto_id=2)
        self._add_detalle(
            banco_id,
            id_cuentabancaria2=1,
            subtotal=30,
        )

        self._scalar('SELECT aplicar_movimientobanco(%s)', [banco_id])

        cuenta = CuentaBancaria.objects.get(id=1)
        self.assertEqual(cuenta.saldo, 70)
        self.assertGreaterEqual(MovimientoContable.objects.count(), 2)

    def test_bank_movement_rolls_back_when_balance_is_insufficient(self):
        banco_id = self._create_documento(movement_id=2, concepto_id=2)
        self._add_detalle(
            banco_id,
            id_cuentabancaria2=1,
            subtotal=130,
        )

        with self.assertRaises(DatabaseError), transaction.atomic():
            self._scalar('SELECT aplicar_movimientobanco(%s)', [banco_id])

        self.assertEqual(CuentaBancaria.objects.get(id=1).saldo, 100)
        self.assertFalse(Documento.objects.filter(id_documentoorigen=banco_id).exists())

    def test_accounting_amounts_reorder_points_and_read_views_are_executable(self):
        PerfilImpuesto.objects.create(
            id=1,
            nombreperfilimpuesto='IVA pruebas',
            estatus='A',
        )
        MontoCalculado.objects.create(
            id=1,
            nombremontocalculado='IVA',
            montofijo=0,
            porcentajeoperacion=16,
            causaimpuesto=True,
            requiereautorizacion=False,
            id_asientocontable=1,
            tipo='I',
            estatus='A',
        )
        PerfilimpuestoMontocalculado.objects.create(
            id=1,
            id_perfilimpuesto=1,
            id_montocalculado=1,
        )
        RegmaestroContabilidad.objects.create(
            id=1,
            id_registromaestro=1,
            id_perfilimpuesto=1,
        )
        RegmaestroInventario.objects.create(
            id=1,
            id_registromaestro=1,
            id_presentacioninventario=1,
            inventarioseguridad=10,
            caducidad=30,
            localidad='Almacen pruebas',
        )
        documento_id = self._create_documento(movement_id=2, concepto_id=2)
        detalle = self._add_detalle(documento_id, subtotal=100)
        self._add_extra(detalle, cantidad=30)

        monto_detalle = self._scalar('SELECT calcular_montos_detalle(%s)', [detalle.id])
        punto_reorden = self._scalar('SELECT calcular_puntoreorden(%s)', [1])

        self.assertEqual(monto_detalle, 16)
        self.assertEqual(MontoCalculadoDetalle.objects.get(id_detalledocumento=detalle.id).monto, 16)
        self.assertEqual(punto_reorden, 17)
        self.assertGreaterEqual(self._scalar('SELECT COUNT(*) FROM vw_movimientos_almacen'), 1)
        self.assertGreaterEqual(self._scalar('SELECT COUNT(*) FROM vw_movimientos_banco'), 0)
        self.assertGreaterEqual(
            LibroContable.objects.filter(anno__isnull=False).count(),
            1,
        )
        self.assertGreaterEqual(LibroSucursal.objects.count(), 1)


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
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('detail', response.data)
        self.assertIn('code', response.data)

    def test_api_errors_are_json_even_when_request_accepts_html(self):
        response = self.client.get(
            '/api/v1/sucursales/',
            HTTP_ACCEPT='text/html',
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('detail', response.data)
        self.assertIn('code', response.data)

    def test_unmatched_api_route_returns_json_error(self):
        response = self.client.get(
            '/api/v1/does-not-exist/',
            HTTP_X_REQUEST_ID='missing-route-id',
            HTTP_ACCEPT='text/html',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['code'], 'not_found')
        self.assertEqual(response.json()['request_id'], 'missing-route-id')
        self.assertEqual(response['X-Request-ID'], 'missing-route-id')

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


class ComandaHighLevelAPITests(LegacyFixtureMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='waiter-api-user',
            password='secret',
        )
        AuthUser_Sucursal.objects.create(id=301, user=self.user.id, sucursal=1)
        self.client.force_authenticate(user=self.user)
        self._seed_comanda_configuration()

    def _seed_comanda_configuration(self):
        ConfiguracionComanda.objects.create(
            id=1,
            id_sucursal=1,
            inventario_habilitado=True,
            inventario_validacion='warn',
            crear_nota_venta_al_cerrar=True,
            permitir_inventario_negativo=True,
        )
        RegistroMaestro.objects.create(
            id=3,
            nombre='Hamburguesa',
            tipo='P',
            id_clasificacion=1,
            marca='Casa',
            estatus='1',
        )
        RecetaItem.objects.create(
            id=1,
            id_producto=3,
            id_ingrediente=1,
            cantidad=2,
            merma_porcentaje=0,
            estatus='Activo',
        )
        ReglaRuteoPreparacion.objects.create(
            id=1,
            id_sucursal=1,
            id_clasificacion=1,
            id_registromaestro=None,
            id_area_preparacion=1,
            modo_salida='terminal',
            estatus='Activo',
        )
        RegmaestroUbicacionfisica.objects.create(
            id=2,
            id_registromaestro=1,
            id_ubicacionfisica=1,
            existencias=10,
        )

    def test_waiter_order_preparation_delivery_close_and_payment_flow(self):
        create_response = self.client.post(
            '/api/v1/comandas/',
            {
                'id_sucursal': 1,
                'id_mesa': 3,
                'numero_comensales': 2,
                'tipo_orden': 'venta',
            },
            format='json',
        )

        self.assertEqual(create_response.status_code, 201)
        comanda_id = create_response.data['id']
        documento_id = create_response.data['id_documento']
        self.assertEqual(create_response.data['estatus'], 'Abierta')
        self.assertTrue(Documento.objects.filter(id=documento_id).exists())

        list_response = self.client.get('/api/v1/comandas/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data[0]['id'], comanda_id)

        empty_items_response = self.client.get(
            '/api/v1/comandas/{0}/items/'.format(comanda_id)
        )

        self.assertEqual(empty_items_response.status_code, 200)
        self.assertEqual(empty_items_response.data, [])

        item_response = self.client.post(
            '/api/v1/comandas/{0}/items/'.format(comanda_id),
            {
                'id_registromaestro': 3,
                'cantidad': '2.0000',
                'precio_unitario': '150.0000',
                'notas': 'Sin cebolla',
            },
            format='json',
        )

        self.assertEqual(item_response.status_code, 201)
        item_id = item_response.data['item']['id']
        self.assertEqual(item_response.data['item']['estatus'], 'Pendiente')
        self.assertEqual(item_response.data['warnings'], [])
        self.assertEqual(Documento.objects.get(id=documento_id).monto, 300)
        self.assertTrue(
            DetalleDocumento.objects.filter(
                id_documento=documento_id,
                id_registromaestro=3,
                comentarios='Sin cebolla',
            ).exists()
        )
        detalle_id = item_response.data['item']['id_detalledocumento']
        self.assertTrue(
            ExtradetalleDocumento.objects.filter(
                id_detalledocumento=detalle_id,
                cantidad=2,
                costopreciototal=300,
            ).exists()
        )

        items_response = self.client.get(
            '/api/v1/comandas/{0}/items/'.format(comanda_id)
        )

        self.assertEqual(items_response.status_code, 200)
        self.assertEqual(len(items_response.data), 1)
        self.assertEqual(items_response.data[0]['id'], item_id)
        self.assertEqual(items_response.data[0]['precio_total'], '300.0000')

        send_response = self.client.post(
            '/api/v1/comandas/{0}/enviar-a-preparacion/'.format(comanda_id),
            format='json',
        )

        self.assertEqual(send_response.status_code, 200)
        prep_order_id = send_response.data['ordenes'][0]['id']
        self.assertEqual(Comanda.objects.get(id=comanda_id).estatus, 'En Proceso')
        self.assertEqual(ComandaItem.objects.get(id=item_id).estatus, 'En Preparacion')
        self.assertTrue(
            PreparacionOrdenItem.objects.filter(
                id_preparacionorden=prep_order_id,
                id_comandaitem=item_id,
            ).exists()
        )

        list_response = self.client.get('/api/v1/preparacion/ordenes/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data[0]['id'], prep_order_id)

        ready_response = self.client.post(
            '/api/v1/preparacion/ordenes/{0}/items/{1}/lista/'.format(
                prep_order_id,
                item_id,
            ),
            format='json',
        )
        self.assertEqual(ready_response.status_code, 200)
        self.assertEqual(PreparacionOrden.objects.get(id=prep_order_id).estatus, 'Completada')
        self.assertEqual(ComandaItem.objects.get(id=item_id).estatus, 'Lista')
        self.assertEqual(Comanda.objects.get(id=comanda_id).estatus, 'Lista')

        deliver_response = self.client.post(
            '/api/v1/comandas/{0}/items/{1}/entregar/'.format(comanda_id, item_id),
            format='json',
        )
        self.assertEqual(deliver_response.status_code, 200)
        self.assertEqual(ComandaItem.objects.get(id=item_id).estatus, 'Entregada')

        close_response = self.client.post(
            '/api/v1/comandas/{0}/cerrar/'.format(comanda_id),
            format='json',
        )
        self.assertEqual(close_response.status_code, 200)
        nota_venta_id = close_response.data['nota_venta']['id']
        self.assertEqual(Comanda.objects.get(id=comanda_id).estatus, 'Cerrada')
        self.assertEqual(Documento.objects.get(id=documento_id).estatus, 'Cerrado')
        self.assertEqual(Documento.objects.get(id=nota_venta_id).estatus, 'Por Pagar')

        payment_response = self.client.post(
            '/api/v1/notas-venta/{0}/pagos/'.format(nota_venta_id),
            {
                'metodo_pago': 'efectivo',
                'destino': 'caja',
                'monto': '300.0000',
            },
            format='json',
        )

        self.assertEqual(payment_response.status_code, 201)
        self.assertEqual(payment_response.data['nota_venta_estatus'], 'Pagada')
        self.assertTrue(PagoCliente.objects.filter(id_nota_venta=nota_venta_id).exists())
        self.assertEqual(Documento.objects.get(id=nota_venta_id).estatus, 'Pagada')

    def test_inventory_block_mode_validates_ingredients_not_menu_item(self):
        ConfiguracionComanda.objects.filter(id_sucursal=1).update(
            inventario_validacion='block',
        )
        RegmaestroUbicacionfisica.objects.filter(
            id_registromaestro=1,
            id_ubicacionfisica=1,
        ).update(existencias=1)
        create_response = self.client.post(
            '/api/v1/comandas/',
            {
                'id_sucursal': 1,
                'id_mesa': 3,
                'numero_comensales': 2,
            },
            format='json',
        )

        item_response = self.client.post(
            '/api/v1/comandas/{0}/items/'.format(create_response.data['id']),
            {
                'id_registromaestro': 3,
                'cantidad': '2.0000',
                'precio_unitario': '150.0000',
            },
            format='json',
        )

        self.assertEqual(item_response.status_code, 400)
        self.assertIn('Ingredient 1 requires', item_response.data['detail'])
        self.assertFalse(
            ComandaItem.objects.filter(
                id_comanda=create_response.data['id'],
            ).exists()
        )

    def test_comanda_item_requires_positive_quantity(self):
        create_response = self.client.post(
            '/api/v1/comandas/',
            {
                'id_sucursal': 1,
                'id_mesa': 3,
                'numero_comensales': 2,
            },
            format='json',
        )

        item_response = self.client.post(
            '/api/v1/comandas/{0}/items/'.format(create_response.data['id']),
            {
                'id_registromaestro': 3,
                'cantidad': '0.0000',
                'precio_unitario': '150.0000',
            },
            format='json',
        )

        self.assertEqual(item_response.status_code, 400)
        self.assertEqual(item_response.data['code'], 'validation_error')
        self.assertIn('cantidad', item_response.data['errors'])
