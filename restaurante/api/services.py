from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.db.models import Max
from django.utils import timezone

from restaurante.models import (
    ClaveFolio,
    Comanda,
    ComandaItem,
    ConfiguracionComanda,
    DetalleDocumento,
    Documento,
    DocumentoConcepto,
    DocumentoAsiento,
    DocumentoMovimiento,
    ExtradetalleDocumento,
    MovimientoContable,
    NumeracionFolio,
    PagoCliente,
    PreparacionOrden,
    PreparacionOrdenItem,
    RecetaItem,
    ReglaRuteoPreparacion,
    RegmaestroUbicacionfisica,
    RegistroMaestro,
    SucursalSistema,
    UbicacionFisica,
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


def _decimal(value, default='0'):
    if value is None or value == '':
        return Decimal(default)
    return Decimal(str(value))


def _money_to_int(value):
    return int(_decimal(value).quantize(Decimal('1')))


def _first_scoped_sucursal(user):
    if user and user.is_authenticated and not user.is_superuser:
        from restaurante.api.permissions import scoped_sucursal_ids

        sucursal_ids = scoped_sucursal_ids(user)
        if sucursal_ids:
            return sucursal_ids[0]
    sucursal = SucursalSistema.objects.order_by('id').first()
    return sucursal.id if sucursal else None


def _get_runtime_config(sucursal_id):
    config = ConfiguracionComanda.objects.filter(id_sucursal=sucursal_id).first()
    if config:
        return config
    return ConfiguracionComanda(
        id_sucursal=sucursal_id,
        inventario_habilitado=False,
        inventario_validacion='none',
        crear_nota_venta_al_cerrar=True,
        permitir_inventario_negativo=True,
    )


def _get_or_create_folio(nombre_documento, clave_folio, sucursal_id):
    cliente_id = (
        SucursalSistema.objects.filter(id=sucursal_id)
        .values_list('id_cliente', flat=True)
        .first()
    ) or 1
    folio = ClaveFolio.objects.filter(
        nombredocumento=nombre_documento,
        id_clientesistema=cliente_id,
    ).first()
    if not folio:
        folio = create_legacy_instance(
            ClaveFolio,
            nombredocumento=nombre_documento,
            clavefolio=clave_folio,
            id_clientesistema=cliente_id,
        )

    numeracion = NumeracionFolio.objects.filter(
        id_clavefolio=folio.id,
        id_sucursal_sistema=sucursal_id,
    ).first()
    if not numeracion:
        numeracion = create_legacy_instance(
            NumeracionFolio,
            id_clavefolio=folio.id,
            id_sucursal_sistema=sucursal_id,
            numeroinicial=1,
            numerofinal=999999,
            numeroactual=1,
        )
    return folio, numeracion


def _get_or_create_movimiento(nombre):
    movimiento = DocumentoMovimiento.objects.filter(movimientodocumento=nombre).first()
    if movimiento:
        return movimiento
    return create_legacy_instance(DocumentoMovimiento, movimientodocumento=nombre)


def _get_or_create_concepto(nombre, folio, movimiento):
    concepto = DocumentoConcepto.objects.filter(
        conceptodocumento=nombre,
        id_clavefolio=folio.id,
    ).first()
    if concepto:
        return concepto
    return create_legacy_instance(
        DocumentoConcepto,
        conceptodocumento=nombre,
        id_clavefolio=folio.id,
        id_movimiento=movimiento.id,
    )


def _new_documento(nombre_documento, clave_folio, movimiento_nombre, concepto_nombre, user, sucursal_id, **data):
    folio, numeracion = _get_or_create_folio(nombre_documento, clave_folio, sucursal_id)
    movimiento = _get_or_create_movimiento(movimiento_nombre)
    concepto = _get_or_create_concepto(concepto_nombre, folio, movimiento)
    next_number = numeracion.numeroactual or numeracion.numeroinicial or 1
    folio_documento = '{0}-{1}'.format(folio.clavefolio, next_number)
    numeracion.numeroactual = next_number + 1
    numeracion.save(update_fields=['numeroactual'])

    defaults = {
        'fecha_hora': timezone.now(),
        'id_clavefolio': folio.id,
        'id_usuario': user.id if user and user.is_authenticated else None,
        'monto': 0,
        'id_conceptodocumento': concepto.id,
        'estatus': 'Abierto',
        'id_documentomovimiento': movimiento.id,
        'foliodocumento': folio_documento,
    }
    defaults.update(data)
    return create_legacy_instance(Documento, **defaults)


def _resolve_routing(sucursal_id, registro):
    rule = ReglaRuteoPreparacion.objects.filter(
        id_sucursal=sucursal_id,
        id_registromaestro=registro.id,
        estatus__in=['', 'Activo', '1'],
    ).first()
    if rule:
        return rule
    return ReglaRuteoPreparacion.objects.filter(
        id_sucursal=sucursal_id,
        id_clasificacion=registro.id_clasificacion,
        id_registromaestro__isnull=True,
        estatus__in=['', 'Activo', '1'],
    ).first()


def _ingredient_requirements(registro_id, cantidad):
    rows = list(
        RecetaItem.objects.filter(
            id_producto=registro_id,
            estatus__in=['', 'Activo', '1'],
        )
    )
    requirements = []
    for row in rows:
        base = _decimal(row.cantidad)
        merma = _decimal(row.merma_porcentaje)
        required = base * cantidad
        if merma:
            required = required * (Decimal('1') + (merma / Decimal('100')))
        requirements.append(
            {
                'id_ingrediente': row.id_ingrediente,
                'cantidad_requerida': required,
            }
        )
    return requirements


def _validate_ingredient_availability(config, registro_id, cantidad, area_id):
    if not config.inventario_habilitado:
        return []

    requirements = _ingredient_requirements(registro_id, cantidad)
    if not requirements:
        message = 'No recipe is configured for registro maestro {0}.'.format(registro_id)
        if config.inventario_validacion == 'block':
            raise ValueError(message)
        return [{'code': 'missing_recipe', 'detail': message}]

    warnings = []
    for requirement in requirements:
        available = (
            RegmaestroUbicacionfisica.objects.filter(
                id_registromaestro=requirement['id_ingrediente'],
                id_ubicacionfisica=area_id,
            ).values_list('existencias', flat=True).first()
            or 0
        )
        required = requirement['cantidad_requerida']
        if Decimal(str(available)) < required:
            message = (
                'Ingredient {0} requires {1} units but only {2} are available.'
                .format(requirement['id_ingrediente'], required, available)
            )
            if config.inventario_validacion == 'block':
                raise ValueError(message)
            warnings.append({'code': 'insufficient_inventory', 'detail': message})
    return warnings


def _serialize_comanda(comanda):
    documento = Documento.objects.get(id=comanda.id_documento)
    items = list(ComandaItem.objects.filter(id_comanda=comanda.id).order_by('id'))
    return {
        'id': comanda.id,
        'id_documento': comanda.id_documento,
        'folio': documento.foliodocumento,
        'id_sucursal': comanda.id_sucursal,
        'id_mesa': comanda.id_mesa,
        'id_mesero': comanda.id_mesero,
        'numero_comensales': comanda.numero_comensales,
        'tipo_orden': comanda.tipo_orden,
        'estatus': comanda.estatus,
        'monto': documento.monto,
        'items': [_serialize_comanda_item(item) for item in items],
    }


def _serialize_comanda_item(item):
    return {
        'id': item.id,
        'id_comanda': item.id_comanda,
        'id_detalledocumento': item.id_detalledocumento,
        'id_registromaestro': item.id_registromaestro,
        'id_area_preparacion': item.id_area_preparacion,
        'cantidad': str(item.cantidad),
        'precio_unitario': str(item.precio_unitario),
        'precio_total': str(item.precio_total),
        'notas': item.notas,
        'estatus': item.estatus,
    }


def _serialize_preparacion(orden):
    items = PreparacionOrdenItem.objects.filter(
        id_preparacionorden=orden.id,
    ).order_by('id')
    return {
        'id': orden.id,
        'id_comanda': orden.id_comanda,
        'id_area_preparacion': orden.id_area_preparacion,
        'modo_salida': orden.modo_salida,
        'estatus': orden.estatus,
        'fecha_hora_apertura': orden.fecha_hora_apertura,
        'fecha_hora_cierre': orden.fecha_hora_cierre,
        'items': [
            {
                'id': item.id,
                'id_comandaitem': item.id_comandaitem,
                'estatus': item.estatus,
            }
            for item in items
        ],
    }


@transaction.atomic
def create_comanda(data, user):
    sucursal_id = data.get('id_sucursal') or _first_scoped_sucursal(user)
    if not sucursal_id:
        raise ValueError('A sucursal is required to create a comanda.')
    mesa_id = data.get('id_mesa')
    if not UbicacionFisica.objects.filter(id=mesa_id).exists():
        raise ObjectDoesNotExist('Mesa {0} does not exist.'.format(mesa_id))

    documento = _new_documento(
        'Orden Comanda',
        'OCM',
        'Comanda',
        'Orden Comanda',
        user,
        sucursal_id,
    )
    comanda = create_legacy_instance(
        Comanda,
        id_documento=documento.id,
        id_sucursal=sucursal_id,
        id_mesa=mesa_id,
        id_mesero=data.get('id_mesero') or (user.id if user and user.is_authenticated else None),
        numero_comensales=data.get('numero_comensales') or 1,
        tipo_orden=data.get('tipo_orden') or 'venta',
        estatus='Abierta',
    )
    return _serialize_comanda(comanda)


@transaction.atomic
def add_comanda_item(comanda_id, data):
    comanda = Comanda.objects.get(id=comanda_id)
    if comanda.estatus not in ('Abierta', 'En Proceso', 'Lista'):
        raise ValueError('Comanda {0} is not editable.'.format(comanda_id))

    registro = RegistroMaestro.objects.get(id=data['id_registromaestro'])
    cantidad = _decimal(data.get('cantidad'), '1')
    precio_unitario = _decimal(data.get('precio_unitario'), '0')
    precio_total = cantidad * precio_unitario
    rule = _resolve_routing(comanda.id_sucursal, registro)
    if not rule:
        raise ValueError(
            'No preparation routing rule exists for registro maestro {0}.'
            .format(registro.id)
        )

    config = _get_runtime_config(comanda.id_sucursal)
    warnings = _validate_ingredient_availability(
        config,
        registro.id,
        cantidad,
        rule.id_area_preparacion,
    )

    detalle = create_legacy_instance(
        DetalleDocumento,
        id_documento=comanda.id_documento,
        id_registromaestro=registro.id,
        id_ubicacionfisica1=comanda.id_mesa,
        id_ubicacionfisica2=rule.id_area_preparacion,
        subtotal=_money_to_int(precio_total),
        comentarios=data.get('notas') or '',
        estatus='Pendiente',
    )
    create_legacy_instance(
        ExtradetalleDocumento,
        id_detalledocumento=detalle.id,
        cantidad=_money_to_int(cantidad),
        costopreciounitario=_money_to_int(precio_unitario),
        costopreciototal=_money_to_int(precio_total),
        cantidadsurtida=0,
    )
    item = create_legacy_instance(
        ComandaItem,
        id_comanda=comanda.id,
        id_detalledocumento=detalle.id,
        id_registromaestro=registro.id,
        id_area_preparacion=rule.id_area_preparacion,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        precio_total=precio_total,
        notas=data.get('notas') or '',
        estatus='Pendiente',
    )
    _recalculate_comanda_total(comanda)
    return {'item': _serialize_comanda_item(item), 'warnings': warnings}


def _recalculate_comanda_total(comanda):
    total = sum(
        _money_to_int(item.precio_total)
        for item in ComandaItem.objects.filter(id_comanda=comanda.id)
    )
    Documento.objects.filter(id=comanda.id_documento).update(monto=total)
    return total


@transaction.atomic
def send_comanda_to_preparacion(comanda_id):
    comanda = Comanda.objects.get(id=comanda_id)
    pending_items = list(
        ComandaItem.objects.filter(
            id_comanda=comanda.id,
            estatus='Pendiente',
        ).order_by('id')
    )
    if not pending_items:
        raise ValueError('Comanda {0} has no pending items to send.'.format(comanda_id))

    orders_by_area = {}
    for item in pending_items:
        rule = ReglaRuteoPreparacion.objects.filter(
            id_sucursal=comanda.id_sucursal,
            id_area_preparacion=item.id_area_preparacion,
        ).first()
        key = item.id_area_preparacion
        if key not in orders_by_area:
            orders_by_area[key] = create_legacy_instance(
                PreparacionOrden,
                id_comanda=comanda.id,
                id_area_preparacion=item.id_area_preparacion,
                modo_salida=(rule.modo_salida if rule else 'terminal'),
                estatus='Pendiente',
                fecha_hora_apertura=timezone.now(),
            )
        create_legacy_instance(
            PreparacionOrdenItem,
            id_preparacionorden=orders_by_area[key].id,
            id_comandaitem=item.id,
            estatus='Pendiente',
        )
        item.estatus = 'En Preparacion'
        item.save(update_fields=['estatus'])

    comanda.estatus = 'En Proceso'
    comanda.save(update_fields=['estatus'])
    return [_serialize_preparacion(order) for order in orders_by_area.values()]


def list_preparacion_ordenes(area_id=None, estatus=None):
    queryset = PreparacionOrden.objects.order_by('fecha_hora_apertura', 'id')
    if area_id:
        queryset = queryset.filter(id_area_preparacion=area_id)
    if estatus:
        queryset = queryset.filter(estatus=estatus)
    return [_serialize_preparacion(order) for order in queryset]


@transaction.atomic
def complete_preparacion_item(orden_id, item_id):
    orden = PreparacionOrden.objects.get(id=orden_id)
    prep_item = PreparacionOrdenItem.objects.get(
        id_preparacionorden=orden.id,
        id_comandaitem=item_id,
    )
    prep_item.estatus = 'Lista'
    prep_item.save(update_fields=['estatus'])
    ComandaItem.objects.filter(id=item_id).update(estatus='Lista')

    if not PreparacionOrdenItem.objects.filter(
        id_preparacionorden=orden.id,
    ).exclude(estatus='Lista').exists():
        orden.estatus = 'Completada'
        orden.fecha_hora_cierre = timezone.now()
        orden.save(update_fields=['estatus', 'fecha_hora_cierre'])

    _refresh_comanda_ready_status(orden.id_comanda)
    return _serialize_preparacion(orden)


@transaction.atomic
def deliver_comanda_item(comanda_id, item_id):
    item = ComandaItem.objects.get(id=item_id, id_comanda=comanda_id)
    if item.estatus != 'Lista':
        raise ValueError('Only ready items can be delivered.')
    item.estatus = 'Entregada'
    item.save(update_fields=['estatus'])
    _refresh_comanda_ready_status(comanda_id)
    return _serialize_comanda_item(item)


def _refresh_comanda_ready_status(comanda_id):
    comanda = Comanda.objects.get(id=comanda_id)
    active_items = ComandaItem.objects.filter(id_comanda=comanda.id).exclude(
        estatus='Cancelada',
    )
    if active_items.exists() and not active_items.exclude(
        estatus__in=['Lista', 'Entregada'],
    ).exists():
        comanda.estatus = 'Lista'
        comanda.save(update_fields=['estatus'])
    return comanda


@transaction.atomic
def close_comanda(comanda_id, user):
    comanda = Comanda.objects.get(id=comanda_id)
    open_items = ComandaItem.objects.filter(id_comanda=comanda.id).exclude(
        estatus__in=['Lista', 'Entregada', 'Cancelada'],
    )
    if open_items.exists():
        raise ValueError('Comanda has items that are not ready yet.')

    total = _recalculate_comanda_total(comanda)
    Documento.objects.filter(id=comanda.id_documento).update(estatus='Cerrado')
    comanda.estatus = 'Cerrada'
    comanda.save(update_fields=['estatus'])

    config = _get_runtime_config(comanda.id_sucursal)
    nota = None
    if config.crear_nota_venta_al_cerrar:
        nota = _new_documento(
            'Nota de Venta',
            'NV',
            'Venta',
            'Nota de Venta',
            user,
            comanda.id_sucursal,
            monto=total,
            id_documentoorigen=comanda.id_documento,
            estatus='Por Pagar',
        )
    return {
        'comanda': _serialize_comanda(comanda),
        'nota_venta': {
            'id': nota.id,
            'folio': nota.foliodocumento,
            'estatus': nota.estatus,
            'monto': nota.monto,
        } if nota else None,
    }


@transaction.atomic
def register_nota_venta_payment(nota_venta_id, data, user):
    nota = Documento.objects.get(id=nota_venta_id)
    if nota.estatus not in ('Por Pagar', 'Pago Parcial'):
        raise ValueError('Nota de venta {0} is not payable.'.format(nota_venta_id))

    monto = _money_to_int(data.get('monto'))
    destino = data.get('destino') or ('caja' if data.get('metodo_pago') == 'efectivo' else 'banco')
    pago_doc = _new_documento(
        'Pago Cliente',
        'PCL',
        'Pago Cliente',
        'Pago Cliente',
        user,
        _first_scoped_sucursal(user),
        monto=monto,
        id_documentoorigen=nota.id,
        estatus='Cerrado',
    )
    pago = create_legacy_instance(
        PagoCliente,
        id_nota_venta=nota.id,
        id_documento_pago=pago_doc.id,
        metodo_pago=data.get('metodo_pago') or 'efectivo',
        destino=destino,
        monto=monto,
        estatus='Aplicado',
    )

    paid_total = sum(
        _money_to_int(row.monto)
        for row in PagoCliente.objects.filter(id_nota_venta=nota.id)
    )
    nota.estatus = 'Pagada' if paid_total >= (nota.monto or 0) else 'Pago Parcial'
    nota.save(update_fields=['estatus'])
    return {
        'id': pago.id,
        'id_nota_venta': nota.id,
        'id_documento_pago': pago_doc.id,
        'metodo_pago': pago.metodo_pago,
        'destino': pago.destino,
        'monto': str(pago.monto),
        'estatus': pago.estatus,
        'nota_venta_estatus': nota.estatus,
    }
