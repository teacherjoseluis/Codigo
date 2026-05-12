from types import SimpleNamespace

from django.db import connection, transaction

from restaurante.models import (
    ClaveFolio,
    ClienteSistema,
    CuentaContable,
    DocumentoConcepto,
    DocumentoMovimiento,
    LibroContable,
    LibroSucursal,
    NumeracionFolio,
    SucursalSistema,
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
