from types import SimpleNamespace

from django.db import connection, transaction

from restaurante.models import (
    ClaveFolio,
    ClienteSistema,
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
