from types import SimpleNamespace

from django.db import connection, transaction

from restaurante.models import (
    CatalogoClasificacion,
    ClaveFolio,
    ClienteSistema,
    ConfiguracionComanda,
    CuentaContable,
    DetalleUbicacion,
    DocumentoConcepto,
    DocumentoMovimiento,
    LibroContable,
    LibroSucursal,
    NumeracionFolio,
    RecetaItem,
    ReglaRuteoPreparacion,
    RegmaestroUbicacionfisica,
    RegistroMaestro,
    SucursalSistema,
    TipoCuentaContable,
    UbicacionFisica,
)


FLOW_FOLIO_CONFIG = (
    ('Flujo_Almacen', 'FAL'),
    ('Flujo_Caja', 'FCA'),
    ('Flujo_Bancos', 'FBA'),
    ('Flujo_Contable', 'FCO'),
)

DEFAULT_NUMERO_INICIAL = 1
DEFAULT_NUMERO_ACTUAL = 1
DEFAULT_NUMERO_FINAL = 999999
DEFAULT_OPERATIONAL_FOLIO = ('Operacion_DB', 'ODB')
DEFAULT_ACCOUNTING_PERIOD = 'Anual'
DOCUMENTO_MOVIMIENTO_CONFIG = (
    (1, 'Entrada'),
    (2, 'Salida'),
    (3, 'Transferencia'),
)
DEFAULT_CUENTAS_CONTABLES = (
    (1, 'Cuenta operativa cargo', 1),
    (2, 'Cuenta operativa abono', 2),
)
DEFAULT_DOCUMENTO_CONCEPTOS = (
    (1, 'Operacion entrada', 1),
    (2, 'Operacion salida', 2),
    (3, 'Operacion transferencia', 3),
)
COMANDA_FOLIO_CONFIG = (
    ('Orden Comanda', 'OCM'),
    ('Nota de Venta', 'NV'),
    ('Pago Cliente', 'PCL'),
)
COMANDA_DOCUMENTO_MOVIMIENTOS = (
    (10, 'Comanda'),
    (11, 'Venta'),
    (12, 'Pago Cliente'),
)


def ensure_flow_folio_config(dry_run=False, create_default_branch=True):
    """Ensure database-side flow document folios are present.

    The PL/pgSQL workflow functions create generated documents by name. For
    those paths to work, each client/branch pair needs Clave_Folio and
    Numeracion_Folio rows for every Flujo_* document type.
    """
    summary = {
        'cliente_sistema': 0,
        'sucursal_sistema': 0,
        'clave_folio': 0,
        'numeracion_folio': 0,
    }

    with transaction.atomic():
        planned_sucursal = None
        if create_default_branch:
            planned_sucursal = _ensure_default_branch(summary, dry_run)

        sucursales = list(SucursalSistema.objects.order_by('id'))
        if dry_run and planned_sucursal is not None and not sucursales:
            sucursales = [planned_sucursal]
        if not sucursales:
            return summary

        client_ids = sorted(
            {
                sucursal.id_cliente
                for sucursal in sucursales
                if sucursal.id_cliente is not None
            }
        )

        folios_by_client = {}
        for client_id in client_ids:
            folios_by_client[client_id] = {}
            for nombre_documento, clave_folio in FLOW_FOLIO_CONFIG:
                folio = ClaveFolio.objects.filter(
                    nombredocumento=nombre_documento,
                    id_clientesistema=client_id,
                ).first()
                if folio is None:
                    summary['clave_folio'] += 1
                    if dry_run:
                        folio = SimpleNamespace(id=None)
                    else:
                        folio = ClaveFolio.objects.create(
                            id=_next_legacy_id('Clave_Folio'),
                            nombredocumento=nombre_documento,
                            clavefolio=clave_folio,
                            id_clientesistema=client_id,
                        )
                folios_by_client[client_id][nombre_documento] = folio

        for sucursal in sucursales:
            if sucursal.id_cliente is None:
                continue

            for nombre_documento, _clave_folio in FLOW_FOLIO_CONFIG:
                folio = folios_by_client[sucursal.id_cliente].get(nombre_documento)
                if folio is None:
                    continue

                if folio.id is None:
                    exists = False
                else:
                    exists = NumeracionFolio.objects.filter(
                        id_clavefolio=folio.id,
                        id_sucursal_sistema=sucursal.id,
                    ).exists()
                if exists:
                    continue

                summary['numeracion_folio'] += 1
                if not dry_run:
                    NumeracionFolio.objects.create(
                        id=_next_legacy_id('Numeracion_Folio'),
                        id_clavefolio=folio.id,
                        id_sucursal_sistema=sucursal.id,
                        numeroinicial=DEFAULT_NUMERO_INICIAL,
                        numeroactual=DEFAULT_NUMERO_ACTUAL,
                        numerofinal=DEFAULT_NUMERO_FINAL,
                    )

    return summary


def ensure_database_logic_config(dry_run=False, create_default_branch=True):
    """Ensure the minimum reference data used by installed DB workflows.

    This seed is intentionally small and idempotent. It gives local/test
    databases enough document, movement, accounting, and folio configuration to
    execute the PL/pgSQL workflow functions without adding restaurant-specific
    master data such as menu items or vendor/customer catalogs.
    """
    summary = ensure_flow_folio_config(
        dry_run=dry_run,
        create_default_branch=create_default_branch,
    )
    summary.update(
        {
            'documento_movimiento': 0,
            'cuenta_contable': 0,
            'clave_folio_operacional': 0,
            'numeracion_folio_operacional': 0,
            'documento_concepto': 0,
            'libro_contable': 0,
            'libro_sucursal': 0,
        }
    )

    with transaction.atomic():
        for movimiento_id, nombre in DOCUMENTO_MOVIMIENTO_CONFIG:
            if DocumentoMovimiento.objects.filter(id=movimiento_id).exists():
                continue

            summary['documento_movimiento'] += 1
            if not dry_run:
                DocumentoMovimiento.objects.create(
                    id=movimiento_id,
                    movimientodocumento=nombre,
                )

        for cuenta_id, nombre, tipo in DEFAULT_CUENTAS_CONTABLES:
            if CuentaContable.objects.filter(id=cuenta_id).exists():
                continue

            summary['cuenta_contable'] += 1
            if not dry_run:
                CuentaContable.objects.create(
                    id=cuenta_id,
                    nombre=nombre,
                    tipo=tipo,
                    id_cliente=1,
                    sub_tipo='',
                    id_subcuentacontable=None,
                )

        folio = _ensure_operational_folio(summary, dry_run, create_default_branch)
        for concepto_id, concepto, movimiento_id in DEFAULT_DOCUMENTO_CONCEPTOS:
            if DocumentoConcepto.objects.filter(id=concepto_id).exists():
                continue

            summary['documento_concepto'] += 1
            if not dry_run:
                DocumentoConcepto.objects.create(
                    id=concepto_id,
                    conceptodocumento=concepto,
                    id_subcuentacontablecargo=1,
                    id_clavefolio=folio.id,
                    id_movimiento=movimiento_id,
                    id_subcuentacontableabono=2,
                )

        libro = _ensure_current_libro_contable(summary, dry_run)
        sucursales = list(SucursalSistema.objects.order_by('id'))
        if dry_run and not sucursales and create_default_branch:
            sucursales = [SimpleNamespace(id=1)]

        for sucursal in sucursales:
            exists = False
            if libro.id is not None:
                exists = LibroSucursal.objects.filter(
                    id_librocontable=libro.id,
                    id_sucursal=sucursal.id,
                ).exists()
            if exists:
                continue

            summary['libro_sucursal'] += 1
            if not dry_run:
                LibroSucursal.objects.create(
                    id=_next_legacy_id('Libro_Sucursal'),
                    estatus='A',
                    id_sucursal=sucursal.id,
                    id_librocontable=libro.id,
                )

    return summary


def ensure_comanda_flow_config(dry_run=False, create_default_branch=True):
    """Ensure minimal reference data for the high-level comanda API slice."""
    summary = ensure_database_logic_config(
        dry_run=dry_run,
        create_default_branch=create_default_branch,
    )
    summary.update(
        {
            'tipo_cuenta_contable': 0,
            'catalogo_clasificacion': 0,
            'ubicacion_area_preparacion': 0,
            'ubicacion_mesa': 0,
            'detalle_ubicacion': 0,
            'registro_maestro': 0,
            'receta_item': 0,
            'stock_ingrediente': 0,
            'configuracion_comanda': 0,
            'regla_ruteo_preparacion': 0,
            'comanda_clave_folio': 0,
            'comanda_numeracion_folio': 0,
            'comanda_documento_movimiento': 0,
            'comanda_documento_concepto': 0,
        }
    )

    with transaction.atomic():
        sucursal = _ensure_seed_sucursal(summary, dry_run, create_default_branch)
        if sucursal is None:
            return summary

        _ensure_tipo_cuenta_contable(summary, dry_run)
        clasificacion = _ensure_clasificacion_comanda(summary, dry_run)
        area = _ensure_ubicacion(
            summary,
            dry_run,
            key='ubicacion_area_preparacion',
            table_name='Ubicacion_Fisica',
            id_sucursal=sucursal.id,
            nombre='Cocina Principal',
            descripcion='Area de preparacion por default',
            tipo='1',
        )
        bar = _ensure_ubicacion(
            summary,
            dry_run,
            key='ubicacion_area_preparacion',
            table_name='Ubicacion_Fisica',
            id_sucursal=sucursal.id,
            nombre='Bar Principal',
            descripcion='Area de bebidas por default',
            tipo='1',
        )
        mesa = _ensure_ubicacion(
            summary,
            dry_run,
            key='ubicacion_mesa',
            table_name='Ubicacion_Fisica',
            id_sucursal=sucursal.id,
            nombre='Mesa Demo',
            descripcion='Mesa demo para pruebas de comanda',
            tipo='2',
        )
        _ensure_detalle_ubicacion(summary, dry_run, area)
        _ensure_detalle_ubicacion(summary, dry_run, bar)
        ingrediente = _ensure_registro_maestro(
            summary,
            dry_run,
            nombre='Ingrediente Demo',
            tipo='I',
            id_clasificacion=clasificacion.id,
        )
        ingrediente_bebida = _ensure_registro_maestro(
            summary,
            dry_run,
            nombre='Ingrediente Bebida Demo',
            tipo='I',
            id_clasificacion=clasificacion.id,
        )
        platillo = _ensure_registro_maestro(
            summary,
            dry_run,
            nombre='Platillo Demo',
            tipo='P',
            id_clasificacion=clasificacion.id,
        )
        bebida = _ensure_registro_maestro(
            summary,
            dry_run,
            nombre='Bebida Demo',
            tipo='P',
            id_clasificacion=clasificacion.id,
        )
        _ensure_receta_item(summary, dry_run, platillo, ingrediente)
        _ensure_receta_item(summary, dry_run, bebida, ingrediente_bebida)
        _ensure_stock_ingrediente(summary, dry_run, ingrediente, area)
        _ensure_stock_ingrediente(summary, dry_run, ingrediente_bebida, bar)
        _ensure_comanda_runtime_config(summary, dry_run, sucursal)
        _ensure_routing_rule(summary, dry_run, sucursal, clasificacion, area)
        _ensure_routing_rule(
            summary,
            dry_run,
            sucursal,
            clasificacion,
            bar,
            registro=bebida,
        )
        folios = _ensure_comanda_folios(summary, dry_run, sucursal)
        movimientos = _ensure_comanda_movimientos(summary, dry_run)
        _ensure_comanda_conceptos(summary, dry_run, folios, movimientos)

    return summary


def _ensure_default_branch(summary, dry_run):
    if SucursalSistema.objects.exists():
        return None

    cliente = ClienteSistema.objects.order_by('id').first()
    if cliente is None:
        summary['cliente_sistema'] += 1
        if dry_run:
            cliente_id = 1
        else:
            cliente = ClienteSistema.objects.create(
                id=_next_legacy_id('Cliente_Sistema'),
                id_personafiscal=None,
            )
            cliente_id = cliente.id
    else:
        cliente_id = cliente.id

    summary['sucursal_sistema'] += 1
    if not dry_run:
        SucursalSistema.objects.create(
            id=_next_legacy_id('Sucursal_Sistema'),
            nombre='Sucursal Principal',
            direccion='',
            personacontacto='',
            telefono1='',
            telefono2='',
            telefono3='',
            correoelectronico='',
            id_cliente=cliente_id,
            identificadorcorto='DEF',
        )
    return SimpleNamespace(id=1, id_cliente=cliente_id)


def _ensure_seed_sucursal(summary, dry_run, create_default_branch):
    sucursal = SucursalSistema.objects.order_by('id').first()
    if sucursal is not None:
        return sucursal
    if not create_default_branch:
        return None
    planned = _ensure_default_branch(summary, dry_run)
    if dry_run:
        return planned
    return SucursalSistema.objects.order_by('id').first()


def _ensure_tipo_cuenta_contable(summary, dry_run):
    rows = (
        (1, 1, 'AreaPreparacion'),
        (2, 2, 'Mesa'),
    )
    for row_id, tipo, instancia in rows:
        if TipoCuentaContable.objects.filter(instancia=instancia).exists():
            continue
        summary['tipo_cuenta_contable'] += 1
        if not dry_run:
            TipoCuentaContable.objects.create(
                id=row_id,
                tipo=tipo,
                instancia=instancia,
            )


def _ensure_clasificacion_comanda(summary, dry_run):
    clasificacion = CatalogoClasificacion.objects.filter(
        nombreclasificacion='Menu Demo',
    ).first()
    if clasificacion is not None:
        return clasificacion
    summary['catalogo_clasificacion'] += 1
    if dry_run:
        return SimpleNamespace(id=1)
    return CatalogoClasificacion.objects.create(
        id=_next_legacy_id('Catalogo_Clasificacion'),
        nombreclasificacion='Menu Demo',
        estatus='1',
    )


def _ensure_ubicacion(summary, dry_run, key, table_name, id_sucursal, nombre, descripcion, tipo):
    ubicacion = UbicacionFisica.objects.filter(
        id_sucursalsistema=id_sucursal,
        nombre=nombre,
    ).first()
    if ubicacion is not None:
        return ubicacion
    summary[key] += 1
    if dry_run:
        return SimpleNamespace(id=1 if tipo == '1' else 2)
    return UbicacionFisica.objects.create(
        id=_next_legacy_id(table_name),
        id_sucursalsistema=id_sucursal,
        nombre=nombre,
        descripcion=descripcion,
        tipo=tipo,
        default=False,
        id_subcuentacontable=None,
        estatus='1',
        cuenta_contable=1,
    )


def _ensure_detalle_ubicacion(summary, dry_run, area):
    if area.id is None:
        return
    if DetalleUbicacion.objects.filter(id_ubicacionfisica=area.id).exists():
        return
    summary['detalle_ubicacion'] += 1
    if not dry_run:
        DetalleUbicacion.objects.create(
            id=_next_legacy_id('Detalle_Ubicacion'),
            id_ubicacionfisica=area.id,
            direccion='',
            telefono='',
            horariorecepcion='',
            saldoactual=0,
            impresora='',
            terminalsalida='terminal-demo',
            minimocomensales='',
            maximocomensales='',
            tipo='',
        )


def _ensure_registro_maestro(summary, dry_run, nombre, tipo, id_clasificacion):
    registro = RegistroMaestro.objects.filter(nombre=nombre).first()
    if registro is not None:
        return registro
    summary['registro_maestro'] += 1
    if dry_run:
        return SimpleNamespace(id=1 if tipo == 'I' else 2, id_clasificacion=id_clasificacion)
    return RegistroMaestro.objects.create(
        id=_next_legacy_id('Registro_Maestro'),
        nombre=nombre,
        tipo=tipo,
        id_clasificacion=id_clasificacion,
        marca='Demo',
        estatus='1',
    )


def _ensure_receta_item(summary, dry_run, platillo, ingrediente):
    if RecetaItem.objects.filter(
        id_producto=platillo.id,
        id_ingrediente=ingrediente.id,
    ).exists():
        return
    summary['receta_item'] += 1
    if not dry_run:
        RecetaItem.objects.create(
            id=_next_legacy_id('Receta_Item'),
            id_producto=platillo.id,
            id_ingrediente=ingrediente.id,
            cantidad=2,
            merma_porcentaje=0,
            estatus='Activo',
        )


def _ensure_stock_ingrediente(summary, dry_run, ingrediente, area):
    if RegmaestroUbicacionfisica.objects.filter(
        id_registromaestro=ingrediente.id,
        id_ubicacionfisica=area.id,
    ).exists():
        return
    summary['stock_ingrediente'] += 1
    if not dry_run:
        RegmaestroUbicacionfisica.objects.create(
            id=_next_legacy_id('RegMaestro_UbicacionFisica'),
            id_registromaestro=ingrediente.id,
            id_ubicacionfisica=area.id,
            existencias=100,
        )


def _ensure_comanda_runtime_config(summary, dry_run, sucursal):
    if ConfiguracionComanda.objects.filter(id_sucursal=sucursal.id).exists():
        return
    summary['configuracion_comanda'] += 1
    if not dry_run:
        ConfiguracionComanda.objects.create(
            id=_next_legacy_id('Configuracion_Comanda'),
            id_sucursal=sucursal.id,
            inventario_habilitado=True,
            inventario_validacion='warn',
            crear_nota_venta_al_cerrar=True,
            permitir_inventario_negativo=True,
        )


def _ensure_routing_rule(
    summary,
    dry_run,
    sucursal,
    clasificacion,
    area,
    registro=None,
):
    if ReglaRuteoPreparacion.objects.filter(
        id_sucursal=sucursal.id,
        id_clasificacion=clasificacion.id,
        id_registromaestro=registro.id if registro else None,
        id_area_preparacion=area.id,
    ).exists():
        return
    summary['regla_ruteo_preparacion'] += 1
    if not dry_run:
        ReglaRuteoPreparacion.objects.create(
            id=_next_legacy_id('Regla_RuteoPreparacion'),
            id_sucursal=sucursal.id,
            id_clasificacion=clasificacion.id,
            id_registromaestro=registro.id if registro else None,
            id_area_preparacion=area.id,
            modo_salida='terminal',
            estatus='Activo',
        )


def _ensure_comanda_folios(summary, dry_run, sucursal):
    folios = {}
    for nombre_documento, clave_folio in COMANDA_FOLIO_CONFIG:
        folio = ClaveFolio.objects.filter(
            nombredocumento=nombre_documento,
            id_clientesistema=sucursal.id_cliente,
        ).first()
        if folio is None:
            summary['comanda_clave_folio'] += 1
            if dry_run:
                folio = SimpleNamespace(id=None, clavefolio=clave_folio)
            else:
                folio = ClaveFolio.objects.create(
                    id=_next_legacy_id('Clave_Folio'),
                    nombredocumento=nombre_documento,
                    clavefolio=clave_folio,
                    id_clientesistema=sucursal.id_cliente,
                )
        folios[nombre_documento] = folio

        exists = False
        if folio.id is not None:
            exists = NumeracionFolio.objects.filter(
                id_clavefolio=folio.id,
                id_sucursal_sistema=sucursal.id,
            ).exists()
        if exists:
            continue
        summary['comanda_numeracion_folio'] += 1
        if not dry_run:
            NumeracionFolio.objects.create(
                id=_next_legacy_id('Numeracion_Folio'),
                id_clavefolio=folio.id,
                id_sucursal_sistema=sucursal.id,
                numeroinicial=DEFAULT_NUMERO_INICIAL,
                numeroactual=DEFAULT_NUMERO_ACTUAL,
                numerofinal=DEFAULT_NUMERO_FINAL,
            )
    return folios


def _ensure_comanda_movimientos(summary, dry_run):
    movimientos = {}
    for movimiento_id, nombre in COMANDA_DOCUMENTO_MOVIMIENTOS:
        movimiento = DocumentoMovimiento.objects.filter(
            movimientodocumento=nombre,
        ).first()
        if movimiento is None:
            summary['comanda_documento_movimiento'] += 1
            if dry_run:
                movimiento = SimpleNamespace(id=movimiento_id)
            else:
                movimiento = DocumentoMovimiento.objects.create(
                    id=movimiento_id,
                    movimientodocumento=nombre,
                )
        movimientos[nombre] = movimiento
    return movimientos


def _ensure_comanda_conceptos(summary, dry_run, folios, movimientos):
    concept_map = (
        ('Orden Comanda', 'Orden Comanda', 'Comanda'),
        ('Nota de Venta', 'Nota de Venta', 'Venta'),
        ('Pago Cliente', 'Pago Cliente', 'Pago Cliente'),
    )
    for nombre_documento, concepto_nombre, movimiento_nombre in concept_map:
        folio = folios[nombre_documento]
        movimiento = movimientos[movimiento_nombre]
        exists = False
        if folio.id is not None:
            exists = DocumentoConcepto.objects.filter(
                conceptodocumento=concepto_nombre,
                id_clavefolio=folio.id,
            ).exists()
        if exists:
            continue
        summary['comanda_documento_concepto'] += 1
        if not dry_run:
            DocumentoConcepto.objects.create(
                id=_next_legacy_id('Documento_Concepto'),
                conceptodocumento=concepto_nombre,
                id_subcuentacontablecargo=1,
                id_clavefolio=folio.id,
                id_movimiento=movimiento.id,
                id_subcuentacontableabono=2,
            )


def _ensure_operational_folio(summary, dry_run, create_default_branch):
    nombre_documento, clave_folio = DEFAULT_OPERATIONAL_FOLIO
    folio = ClaveFolio.objects.filter(
        nombredocumento=nombre_documento,
        id_clientesistema=1,
    ).first()

    if folio is None:
        summary['clave_folio_operacional'] += 1
        if dry_run:
            folio = SimpleNamespace(id=None)
        else:
            folio = ClaveFolio.objects.create(
                id=_next_legacy_id('Clave_Folio'),
                nombredocumento=nombre_documento,
                clavefolio=clave_folio,
                id_clientesistema=1,
            )

    sucursales = list(SucursalSistema.objects.order_by('id'))
    if dry_run and not sucursales and create_default_branch:
        sucursales = [SimpleNamespace(id=1)]
    for sucursal in sucursales:
        exists = False
        if folio.id is not None:
            exists = NumeracionFolio.objects.filter(
                id_clavefolio=folio.id,
                id_sucursal_sistema=sucursal.id,
            ).exists()
        if exists:
            continue

        summary['numeracion_folio_operacional'] += 1
        if not dry_run:
            NumeracionFolio.objects.create(
                id=_next_legacy_id('Numeracion_Folio'),
                id_clavefolio=folio.id,
                id_sucursal_sistema=sucursal.id,
                numeroinicial=DEFAULT_NUMERO_INICIAL,
                numeroactual=DEFAULT_NUMERO_ACTUAL,
                numerofinal=DEFAULT_NUMERO_FINAL,
            )

    return folio


def _ensure_current_libro_contable(summary, dry_run):
    current_year = _current_database_year()
    libro = LibroContable.objects.filter(anno=current_year).order_by('-id').first()
    if libro is not None:
        return libro

    summary['libro_contable'] += 1
    if dry_run:
        return SimpleNamespace(id=None, anno=current_year)

    return LibroContable.objects.create(
        id=_next_legacy_id('Libro_Contable'),
        periodo=DEFAULT_ACCOUNTING_PERIOD,
        anno=current_year,
    )


def _current_database_year():
    with connection.cursor() as cursor:
        cursor.execute('SELECT EXTRACT(ISOYEAR FROM LOCALTIMESTAMP)::int')
        return cursor.fetchone()[0]


def _next_legacy_id(table_name):
    quoted_table_name = connection.ops.quote_name(table_name)
    quoted_id = connection.ops.quote_name('ID')
    if connection.vendor == 'postgresql':
        sequence_name = '{0}_ID_seq'.format(table_name)
        with connection.cursor() as cursor:
            cursor.execute('SELECT to_regclass(quote_ident(%s))', [sequence_name])
            if cursor.fetchone()[0] is not None:
                cursor.execute(
                    'SELECT COALESCE(MAX({0}), 0) FROM {1}'.format(
                        quoted_id,
                        quoted_table_name,
                    )
                )
                max_id = cursor.fetchone()[0]
                if max_id:
                    cursor.execute(
                        'SELECT setval(quote_ident(%s)::regclass, %s, true)',
                        [sequence_name, max_id],
                    )
                cursor.execute(
                    'SELECT nextval(quote_ident(%s)::regclass)',
                    [sequence_name],
                )
                return cursor.fetchone()[0]

    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COALESCE(MAX({0}), 0) + 1 FROM {1}'.format(
                quoted_id,
                quoted_table_name,
            )
        )
        return cursor.fetchone()[0]
