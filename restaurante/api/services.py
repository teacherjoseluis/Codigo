from django.db import connection, transaction
from django.db.models import Max
from django.utils import timezone

from restaurante.models import (
    DetalleDocumento,
    Documento,
    DocumentoAsiento,
    MovimientoContable,
)


def next_legacy_id(model_class):
    """Return the next integer ID for legacy tables with external sequences."""
    sequence_name = '{0}_ID_seq'.format(model_class._meta.db_table)
    quoted_sequence_name = '"{0}"'.format(sequence_name)
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute('SELECT to_regclass(%s)', [quoted_sequence_name])
            if cursor.fetchone()[0]:
                cursor.execute('SELECT nextval(%s::regclass)', [quoted_sequence_name])
                return int(cursor.fetchone()[0])

    max_id = model_class.objects.aggregate(max_id=Max('id'))['max_id'] or 0
    return int(max_id) + 1


def create_legacy_instance(model_class, **data):
    if not data.get('id'):
        data['id'] = next_legacy_id(model_class)
    return model_class.objects.create(**data)


@transaction.atomic
def create_documento_with_children(
    documento_data,
    detalles=None,
    movimientos_contables=None,
    asientos=None,
):
    detalles = detalles or []
    movimientos_contables = movimientos_contables or []
    asientos = asientos or []

    if not documento_data.get('fecha_hora'):
        documento_data['fecha_hora'] = timezone.now()
    if not documento_data.get('estatus'):
        documento_data['estatus'] = '1'
    if documento_data.get('monto') is None and detalles:
        documento_data['monto'] = sum(item.get('subtotal') or 0 for item in detalles)

    documento = create_legacy_instance(Documento, **documento_data)

    for detalle_data in detalles:
        detalle_data['id_documento'] = documento.id
        create_legacy_instance(DetalleDocumento, **detalle_data)

    for movimiento_data in movimientos_contables:
        movimiento_data['id_documento'] = documento.id
        create_legacy_instance(MovimientoContable, **movimiento_data)

    for asiento_data in asientos:
        asiento_data.setdefault('id_clavefolio', documento.id_clavefolio)
        asiento_data.setdefault('id_conceptodocumento', documento.id_conceptodocumento)
        asiento_data.setdefault('id_movimientodocumento', documento.id_documentomovimiento)
        create_legacy_instance(DocumentoAsiento, **asiento_data)

    return documento
