-- Repeatable PostgreSQL database logic for the legacy Restaurante schema.
-- The legacy tables are unmanaged by Django and use externally-created
-- "<table>_ID_seq" sequences, so generated rows assign "ID" explicitly.

CREATE OR REPLACE FUNCTION restaurante_next_legacy_id(p_table_name text)
RETURNS bigint AS $$
DECLARE
    v_sequence_name text := p_table_name || '_ID_seq';
    v_regclass regclass;
    v_next bigint;
BEGIN
    SELECT to_regclass(quote_ident(v_sequence_name)) INTO v_regclass;

    IF v_regclass IS NOT NULL THEN
        RETURN nextval(v_regclass);
    END IF;

    EXECUTE format('SELECT COALESCE(MAX("ID"), 0) + 1 FROM %I', p_table_name)
       INTO v_next;
    RETURN v_next;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION restaurante_cuenta_debit_sign(p_tipo text)
RETURNS integer AS $$
BEGIN
    CASE lower(coalesce(p_tipo, ''))
        WHEN 'activo' THEN RETURN 1;
        WHEN 'costos' THEN RETURN 1;
        WHEN 'costo' THEN RETURN 1;
        WHEN 'gastos' THEN RETURN 1;
        WHEN 'gasto' THEN RETURN 1;
        WHEN 'pasivo' THEN RETURN -1;
        WHEN 'capital' THEN RETURN -1;
        WHEN 'ingresos' THEN RETURN -1;
        WHEN 'ingreso' THEN RETURN -1;
        -- Conservative support for numeric catalog encodings often used in
        -- imported accounting catalogs: 1/4/5 debit-normal, 2/3/6 credit-normal.
        WHEN '1' THEN RETURN 1;
        WHEN '4' THEN RETURN 1;
        WHEN '5' THEN RETURN 1;
        WHEN '2' THEN RETURN -1;
        WHEN '3' THEN RETURN -1;
        WHEN '6' THEN RETURN -1;
        ELSE
            RAISE EXCEPTION 'DB_ERROR_03 unsupported Cuenta_Contable.Tipo: %', p_tipo;
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION restaurante_resolver_cuenta_concreta(
    p_id_cuenta int,
    p_id_documento int
) RETURNS int AS $$
DECLARE
    v_subtipo text;
    v_resuelta int;
BEGIN
    SELECT "Sub_Tipo"::text
      INTO v_subtipo
      FROM "Cuenta_Contable"
     WHERE "ID" = p_id_cuenta;

    IF v_subtipo IS NULL OR v_subtipo = '' THEN
        RETURN p_id_cuenta;
    END IF;

    IF v_subtipo IN ('1', '2') THEN
        SELECT pf."Cuenta_Contable"
          INTO v_resuelta
          FROM "Detalle_Documento" dd
          JOIN "Persona_Fiscal" pf ON pf."ID" = dd."Id_PersonaFiscal"
         WHERE dd."Id_Documento" = p_id_documento
           AND pf."Cuenta_Contable" IS NOT NULL
         ORDER BY dd."ID"
         LIMIT 1;
    ELSIF v_subtipo IN ('3', '4', '5') THEN
        SELECT uf."Cuenta_Contable"
          INTO v_resuelta
          FROM "Detalle_Documento" dd
          JOIN "Ubicacion_Fisica" uf
            ON uf."ID" = COALESCE(dd."Id_UbicacionFisica1", dd."Id_UbicacionFisica2")
         WHERE dd."Id_Documento" = p_id_documento
           AND uf."Cuenta_Contable" IS NOT NULL
         ORDER BY dd."ID"
         LIMIT 1;
    ELSIF v_subtipo = '6' THEN
        SELECT cb."ID_SubcuentaContable"
          INTO v_resuelta
          FROM "Detalle_Documento" dd
          JOIN "Cuenta_Bancaria" cb
            ON cb."ID" = COALESCE(dd."Id_CuentaBancaria1", dd."Id_CuentaBancaria2")
         WHERE dd."Id_Documento" = p_id_documento
           AND cb."ID_SubcuentaContable" IS NOT NULL
         ORDER BY dd."ID"
         LIMIT 1;
    END IF;

    RETURN COALESCE(v_resuelta, p_id_cuenta);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION generar_nuevofolio(
    p_nombre_documento text,
    p_id_sucursal int
) RETURNS TABLE (
    folio text,
    id_clave_folio int,
    id_numeracion_folio int
) AS $$
DECLARE
    v_id_cliente int;
    v_id_corto text;
    v_clave_folio text;
    v_numero_actual int;
    v_numero_final int;
BEGIN
    SELECT "ID_Cliente", "IdentificadorCorto"
      INTO v_id_cliente, v_id_corto
      FROM "Sucursal_Sistema"
     WHERE "ID" = p_id_sucursal;

    IF v_id_cliente IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Sucursal_Sistema for ID %', p_id_sucursal;
    END IF;

    SELECT cf."ID", cf."ClaveFolio"
      INTO id_clave_folio, v_clave_folio
      FROM "Clave_Folio" cf
     WHERE cf."NombreDocumento" = p_nombre_documento
       AND cf."Id_ClienteSistema" = v_id_cliente
     ORDER BY cf."ID" DESC
     LIMIT 1;

    IF id_clave_folio IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Clave_Folio for document %, client %',
            p_nombre_documento, v_id_cliente;
    END IF;

    SELECT nf."ID", nf."NumeroActual", nf."NumeroFinal"
      INTO id_numeracion_folio, v_numero_actual, v_numero_final
      FROM "Numeracion_Folio" nf
     WHERE nf."Id_ClaveFolio" = id_clave_folio
       AND nf."Id_Sucursal_Sistema" = p_id_sucursal
     ORDER BY nf."ID" DESC
     LIMIT 1
     FOR UPDATE;

    IF id_numeracion_folio IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Numeracion_Folio for Clave_Folio %, Sucursal %',
            id_clave_folio, p_id_sucursal;
    END IF;

    IF v_numero_actual IS NULL OR v_numero_final IS NULL OR v_numero_actual > v_numero_final THEN
        RAISE EXCEPTION 'DB_ERROR_01 folio sequence exhausted for Numeracion_Folio %',
            id_numeracion_folio;
    END IF;

    folio := concat_ws(
        '_',
        v_clave_folio,
        COALESCE(NULLIF(v_id_corto, ''), p_id_sucursal::text),
        v_numero_actual::text
    ) || '/' || to_char(CURRENT_DATE, 'YYYYMMDD');

    UPDATE "Numeracion_Folio"
       SET "NumeroActual" = v_numero_actual + 1
     WHERE "ID" = id_numeracion_folio;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION crear_documento(
    p_id_sucursal int,
    p_nombre_documento text,
    p_id_usuario int,
    p_id_documento_origen int DEFAULT NULL,
    p_id_concepto_documento int DEFAULT NULL,
    p_id_movimiento_documento int DEFAULT NULL
) RETURNS bigint AS $$
DECLARE
    v_id_documento bigint;
    v_folio text;
    v_id_clave_folio int;
    v_id_movimiento int := p_id_movimiento_documento;
BEGIN
    SELECT gf.folio, gf.id_clave_folio
      INTO v_folio, v_id_clave_folio
      FROM generar_nuevofolio(p_nombre_documento, p_id_sucursal) gf;

    IF v_id_movimiento IS NULL AND p_id_concepto_documento IS NOT NULL THEN
        SELECT "Id_Movimiento"
          INTO v_id_movimiento
          FROM "Documento_Concepto"
         WHERE "ID" = p_id_concepto_documento;
    END IF;

    v_id_documento := restaurante_next_legacy_id('Documento');

    INSERT INTO "Documento" (
        "ID", "Fecha/Hora", "Id_ClaveFolio", "Id_Usuario", "Monto",
        "Id_DocumentoOrigen", "Id_ConceptoDocumento", "FolioInterno",
        "Estatus", "Id_DocumentoMovimiento", "FolioDocumento"
    ) VALUES (
        v_id_documento, LOCALTIMESTAMP, v_id_clave_folio, p_id_usuario, 0,
        p_id_documento_origen, p_id_concepto_documento, '',
        'N', v_id_movimiento, v_folio
    );

    RETURN v_id_documento;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION recalcular_documento(p_id_documento int)
RETURNS numeric AS $$
DECLARE
    v_estatus text;
    v_total numeric;
BEGIN
    SELECT "Estatus"
      INTO v_estatus
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Documento %', p_id_documento;
    END IF;

    IF v_estatus IN ('C', 'X') THEN
        RAISE EXCEPTION 'DB_ERROR_06 Documento % is not editable, status %',
            p_id_documento, v_estatus;
    END IF;

    SELECT COALESCE((SELECT SUM(COALESCE("Subtotal", 0))
                       FROM "Detalle_Documento"
                      WHERE "Id_Documento" = p_id_documento), 0)
         + COALESCE((SELECT SUM(COALESCE("Monto", 0))
                       FROM "Monto_Calculado_Documento"
                      WHERE "Id_Documento" = p_id_documento), 0)
      INTO v_total;

    UPDATE "Documento"
       SET "Monto" = v_total
     WHERE "ID" = p_id_documento;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION cerrar_documento(p_id_documento int)
RETURNS boolean AS $$
DECLARE
    v_estatus text;
    v_open_child bigint;
BEGIN
    SELECT "Estatus"
      INTO v_estatus
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Documento %', p_id_documento;
    END IF;

    IF v_estatus = 'X' THEN
        RAISE EXCEPTION 'DB_ERROR_06 Documento % is cancelled', p_id_documento;
    END IF;

    SELECT "ID"
      INTO v_open_child
      FROM "Documento"
     WHERE "Id_DocumentoOrigen" = p_id_documento
       AND COALESCE("Estatus", '') <> 'C'
     ORDER BY "ID"
     LIMIT 1;

    IF v_open_child IS NOT NULL THEN
        RAISE EXCEPTION 'DB_ERROR_04 Documento % has open child Documento %',
            p_id_documento, v_open_child;
    END IF;

    UPDATE "Documento"
       SET "Estatus" = 'C'
     WHERE "ID" = p_id_documento;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION comparar_existenciasalmacen(
    p_id_registro_maestro int,
    p_id_ubicacion_fisica int,
    p_cantidad numeric
) RETURNS boolean AS $$
DECLARE
    v_disponible numeric;
BEGIN
    SELECT COALESCE(SUM(COALESCE(ed."SaldoCierre", 0)), 0)
      INTO v_disponible
      FROM "Detalle_Documento" dd
      JOIN "ExtraDetalle_Documento" ed ON ed."Id_DetalleDocumento" = dd."ID"
     WHERE dd."Id_RegistroMaestro" = p_id_registro_maestro
       AND COALESCE(dd."Id_UbicacionFisica2", dd."Id_UbicacionFisica1") = p_id_ubicacion_fisica
       AND COALESCE(ed."SaldoCierre", 0) > 0;

    RETURN v_disponible >= COALESCE(p_cantidad, 0);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION comparar_saldobanco(
    p_id_cuenta_bancaria int,
    p_cantidad numeric
) RETURNS boolean AS $$
DECLARE
    v_saldo numeric;
BEGIN
    SELECT COALESCE("Saldo", 0)
      INTO v_saldo
      FROM "Cuenta_Bancaria"
     WHERE "ID" = p_id_cuenta_bancaria
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Cuenta_Bancaria %', p_id_cuenta_bancaria;
    END IF;

    RETURN v_saldo >= COALESCE(p_cantidad, 0);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_costopromedio(
    p_id_registro_maestro int,
    p_id_ubicacion_fisica int
) RETURNS numeric AS $$
DECLARE
    v_existencias numeric;
    v_costo_total numeric;
BEGIN
    SELECT COALESCE("Existencias", 0)
      INTO v_existencias
      FROM "RegMaestro_UbicacionFisica"
     WHERE "Id_RegistroMaestro" = p_id_registro_maestro
       AND "Id_UbicacionFisica" = p_id_ubicacion_fisica;

    IF COALESCE(v_existencias, 0) <= 0 THEN
        RETURN 0;
    END IF;

    SELECT COALESCE(SUM(COALESCE(ed."CostoPrecioTotal", 0)), 0)
      INTO v_costo_total
      FROM "Detalle_Documento" dd
      JOIN "ExtraDetalle_Documento" ed ON ed."Id_DetalleDocumento" = dd."ID"
     WHERE dd."Id_RegistroMaestro" = p_id_registro_maestro
       AND COALESCE(dd."Id_UbicacionFisica2", dd."Id_UbicacionFisica1") = p_id_ubicacion_fisica
       AND COALESCE(ed."SaldoCierre", 0) > 0;

    RETURN v_costo_total / v_existencias;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION aplicar_asiento(p_id_documento int)
RETURNS bigint AS $$
DECLARE
    v_doc record;
    v_id_sucursal int;
    v_id_doccont bigint;
    v_id_libro int;
    v_id_librosucursal int;
    v_id_cuentacargo int;
    v_id_cuentaabono int;
    v_tipo_cargo text;
    v_tipo_abono text;
    v_saldo numeric;
    v_movimiento_id bigint;
BEGIN
    SELECT *
      INTO v_doc
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Documento %', p_id_documento;
    END IF;

    SELECT nf."Id_Sucursal_Sistema"
      INTO v_id_sucursal
      FROM "Numeracion_Folio" nf
     WHERE nf."Id_ClaveFolio" = v_doc."Id_ClaveFolio"
     ORDER BY nf."ID" DESC
     LIMIT 1;

    IF v_id_sucursal IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing sucursal for Documento %', p_id_documento;
    END IF;

    SELECT dc."ID_SubcuentaContableCargo", dc."ID_SubcuentaContableAbono"
      INTO v_id_cuentacargo, v_id_cuentaabono
      FROM "Documento_Concepto" dc
     WHERE dc."ID" = v_doc."Id_ConceptoDocumento";

    IF v_id_cuentacargo IS NULL OR v_id_cuentaabono IS NULL THEN
        SELECT ac."ID_SubcuentaContableCargo", ac."ID_SubcuentaContableAbono"
          INTO v_id_cuentacargo, v_id_cuentaabono
          FROM "Documento_Asiento" da
          JOIN "Asiento_Contable" ac ON ac."ID" = da."Id_Asiento"
         WHERE da."Id_ClaveFolio" = v_doc."Id_ClaveFolio"
           AND da."Id_ConceptoDocumento" = v_doc."Id_ConceptoDocumento"
           AND da."Id_MovimientoDocumento" = COALESCE(
                v_doc."Id_DocumentoMovimiento",
                (SELECT "Id_Movimiento" FROM "Documento_Concepto" WHERE "ID" = v_doc."Id_ConceptoDocumento")
           )
         ORDER BY da."ID"
         LIMIT 1;
    END IF;

    IF v_id_cuentacargo IS NULL OR v_id_cuentaabono IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing accounting mapping for Documento %', p_id_documento;
    END IF;

    v_id_cuentacargo := restaurante_resolver_cuenta_concreta(v_id_cuentacargo, p_id_documento);
    v_id_cuentaabono := restaurante_resolver_cuenta_concreta(v_id_cuentaabono, p_id_documento);

    SELECT "ID"
      INTO v_id_libro
      FROM "Libro_Contable"
     WHERE "Anno" = EXTRACT(ISOYEAR FROM LOCALTIMESTAMP)::int
     ORDER BY "ID" DESC
     LIMIT 1;

    IF v_id_libro IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Libro_Contable for current year';
    END IF;

    SELECT "ID"
      INTO v_id_librosucursal
      FROM "Libro_Sucursal"
     WHERE "ID_LibroContable" = v_id_libro
       AND "ID_Sucursal" = v_id_sucursal
     LIMIT 1
     FOR UPDATE;

    IF v_id_librosucursal IS NULL THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Libro_Sucursal for Libro %, Sucursal %',
            v_id_libro, v_id_sucursal;
    END IF;

    IF EXISTS (
        SELECT 1 FROM "Libro_Sucursal"
         WHERE "ID" = v_id_librosucursal AND "Estatus" = 'C'
    ) THEN
        RAISE EXCEPTION 'DB_ERROR_02 accounting book is closed for Libro_Sucursal %',
            v_id_librosucursal;
    END IF;

    v_id_doccont := crear_documento(
        v_id_sucursal,
        'Flujo_Contable',
        v_doc."Id_Usuario",
        p_id_documento,
        v_doc."Id_ConceptoDocumento",
        v_doc."Id_DocumentoMovimiento"
    );

    v_movimiento_id := restaurante_next_legacy_id('Movimiento_Contable');
    INSERT INTO "Movimiento_Contable" (
        "ID", "ID_LibroSucursal", "ID_DocumentoConcepto", "ID_Documento"
    ) VALUES (
        v_movimiento_id, v_id_librosucursal, v_doc."Id_ConceptoDocumento", p_id_documento
    );

    INSERT INTO "Libro_CuentaContable" ("ID", "Saldo", "ID_LibroSucursal", "ID_CuentaContable")
    SELECT restaurante_next_legacy_id('Libro_CuentaContable'), 0, v_id_librosucursal, c.account_id
      FROM (VALUES (v_id_cuentacargo), (v_id_cuentaabono)) AS c(account_id)
     WHERE NOT EXISTS (
        SELECT 1
          FROM "Libro_CuentaContable" lcc
         WHERE lcc."ID_LibroSucursal" = v_id_librosucursal
           AND lcc."ID_CuentaContable" = c.account_id
     );

    PERFORM 1
      FROM "Libro_CuentaContable"
     WHERE "ID_LibroSucursal" = v_id_librosucursal
       AND "ID_CuentaContable" IN (v_id_cuentacargo, v_id_cuentaabono)
     ORDER BY "ID"
     FOR UPDATE;

    SELECT "Tipo"::text INTO v_tipo_cargo FROM "Cuenta_Contable" WHERE "ID" = v_id_cuentacargo;
    SELECT "Saldo" INTO v_saldo FROM "Libro_CuentaContable"
     WHERE "ID_LibroSucursal" = v_id_librosucursal AND "ID_CuentaContable" = v_id_cuentacargo;

    UPDATE "Libro_CuentaContable"
       SET "Saldo" = COALESCE(v_saldo, 0)
           + (COALESCE(v_doc."Monto", 0) * restaurante_cuenta_debit_sign(v_tipo_cargo))
     WHERE "ID_LibroSucursal" = v_id_librosucursal
       AND "ID_CuentaContable" = v_id_cuentacargo;

    SELECT "Tipo"::text INTO v_tipo_abono FROM "Cuenta_Contable" WHERE "ID" = v_id_cuentaabono;
    SELECT "Saldo" INTO v_saldo FROM "Libro_CuentaContable"
     WHERE "ID_LibroSucursal" = v_id_librosucursal AND "ID_CuentaContable" = v_id_cuentaabono;

    UPDATE "Libro_CuentaContable"
       SET "Saldo" = COALESCE(v_saldo, 0)
           - (COALESCE(v_doc."Monto", 0) * restaurante_cuenta_debit_sign(v_tipo_abono))
     WHERE "ID_LibroSucursal" = v_id_librosucursal
       AND "ID_CuentaContable" = v_id_cuentaabono;

    PERFORM cerrar_documento(v_id_doccont::int);
    RETURN v_id_doccont;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION entrada_movimientoalmacen(p_id_documento int)
RETURNS void AS $$
DECLARE
    v_doc record;
    v_id_sucursal int;
    v_det record;
    v_extra record;
    v_almacen_estatus text;
    v_id_docalm bigint;
    v_id_detalle bigint;
BEGIN
    SELECT *
      INTO v_doc
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Documento %', p_id_documento;
    END IF;

    SELECT "Id_Sucursal_Sistema"
      INTO v_id_sucursal
      FROM "Numeracion_Folio"
     WHERE "Id_ClaveFolio" = v_doc."Id_ClaveFolio"
     ORDER BY "ID" DESC
     LIMIT 1;

    FOR v_det IN
        SELECT * FROM "Detalle_Documento" WHERE "Id_Documento" = p_id_documento ORDER BY "ID"
    LOOP
        SELECT "Estatus"
          INTO v_almacen_estatus
          FROM "Ubicacion_Fisica"
         WHERE "ID" = v_det."Id_UbicacionFisica1"
         FOR UPDATE;

        IF v_almacen_estatus = 'C' THEN
            RAISE EXCEPTION 'DB_ERROR_02 warehouse % is closed', v_det."Id_UbicacionFisica1";
        END IF;

        FOR v_extra IN
            SELECT * FROM "ExtraDetalle_Documento"
             WHERE "Id_DetalleDocumento" = v_det."ID"
             ORDER BY "ID"
        LOOP
            v_id_docalm := crear_documento(
                v_id_sucursal, 'Flujo_Almacen', v_doc."Id_Usuario",
                p_id_documento, v_doc."Id_ConceptoDocumento", v_doc."Id_DocumentoMovimiento"
            );

            v_id_detalle := restaurante_next_legacy_id('Detalle_Documento');
            INSERT INTO "Detalle_Documento" (
                "ID", "Id_Documento", "Id_RegistroMaestro", "Id_PersonaFiscal",
                "Id_UbicacionFisica1", "Id_UbicacionFisica2", "Subtotal",
                "Comentarios", "Estatus", "Id_CuentaBancaria1", "Id_CuentaBancaria2"
            ) VALUES (
                v_id_detalle, v_id_docalm, v_det."Id_RegistroMaestro", v_det."Id_PersonaFiscal",
                v_det."Id_UbicacionFisica1", v_det."Id_UbicacionFisica2",
                COALESCE(v_extra."CostoPrecioTotal", v_det."Subtotal", 0),
                v_det."Comentarios", v_det."Estatus", v_det."Id_CuentaBancaria1", v_det."Id_CuentaBancaria2"
            );

            INSERT INTO "ExtraDetalle_Documento" (
                "ID", "Id_DetalleDocumento", "NumeroComensales", "Id_Presentacion",
                "Cantidad", "CostoPrecioUnitario", "CostoPrecioTotal",
                "CantidadSurtida", "FechaHoraApertura", "SaldoApertura", "SaldoCierre"
            ) VALUES (
                restaurante_next_legacy_id('ExtraDetalle_Documento'),
                v_id_detalle, v_extra."NumeroComensales", v_extra."Id_Presentacion",
                v_extra."Cantidad", v_extra."CostoPrecioUnitario", v_extra."CostoPrecioTotal",
                v_extra."CantidadSurtida", LOCALTIMESTAMP, v_extra."Cantidad", v_extra."Cantidad"
            );

            INSERT INTO "RegMaestro_UbicacionFisica" (
                "ID", "Id_RegistroMaestro", "Id_UbicacionFisica", "Existencias"
            )
            SELECT restaurante_next_legacy_id('RegMaestro_UbicacionFisica'),
                   v_det."Id_RegistroMaestro", v_det."Id_UbicacionFisica1", 0
             WHERE NOT EXISTS (
                SELECT 1 FROM "RegMaestro_UbicacionFisica"
                 WHERE "Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
                   AND "Id_UbicacionFisica" = v_det."Id_UbicacionFisica1"
             );

            PERFORM 1
              FROM "RegMaestro_UbicacionFisica"
             WHERE "Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
               AND "Id_UbicacionFisica" = v_det."Id_UbicacionFisica1"
             FOR UPDATE;

            UPDATE "RegMaestro_UbicacionFisica"
               SET "Existencias" = COALESCE("Existencias", 0) + COALESCE(v_extra."Cantidad", 0)
             WHERE "Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
               AND "Id_UbicacionFisica" = v_det."Id_UbicacionFisica1";

            UPDATE "Documento"
               SET "Monto" = COALESCE(v_extra."CostoPrecioTotal", v_det."Subtotal", 0)
             WHERE "ID" = v_id_docalm;

            PERFORM aplicar_asiento(v_id_docalm::int);
            PERFORM cerrar_documento(v_id_docalm::int);
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION salida_movimientoalmacen(
    p_id_documento int,
    p_metodo_valuacion int DEFAULT 1
) RETURNS void AS $$
DECLARE
    v_doc record;
    v_id_sucursal int;
    v_det record;
    v_extra record;
    v_lot record;
    v_source_ubicacion int;
    v_almacen_estatus text;
    v_cantidad_retirar numeric;
    v_cantidad_lote numeric;
    v_cantidad_segmento numeric;
    v_costo_salida numeric;
    v_id_docalm bigint;
    v_id_detalle bigint;
BEGIN
    IF p_metodo_valuacion NOT IN (1, 2, 3) THEN
        RAISE EXCEPTION 'DB_ERROR_07 invalid inventory valuation method %', p_metodo_valuacion;
    END IF;

    SELECT *
      INTO v_doc
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Documento %', p_id_documento;
    END IF;

    SELECT "Id_Sucursal_Sistema"
      INTO v_id_sucursal
      FROM "Numeracion_Folio"
     WHERE "Id_ClaveFolio" = v_doc."Id_ClaveFolio"
     ORDER BY "ID" DESC
     LIMIT 1;

    FOR v_det IN
        SELECT * FROM "Detalle_Documento" WHERE "Id_Documento" = p_id_documento ORDER BY "ID"
    LOOP
        v_source_ubicacion := COALESCE(v_det."Id_UbicacionFisica2", v_det."Id_UbicacionFisica1");

        SELECT "Estatus"
          INTO v_almacen_estatus
          FROM "Ubicacion_Fisica"
         WHERE "ID" = v_source_ubicacion
         FOR UPDATE;

        IF v_almacen_estatus = 'C' THEN
            RAISE EXCEPTION 'DB_ERROR_02 warehouse % is closed', v_source_ubicacion;
        END IF;

        FOR v_extra IN
            SELECT * FROM "ExtraDetalle_Documento"
             WHERE "Id_DetalleDocumento" = v_det."ID"
             ORDER BY "ID"
        LOOP
            v_cantidad_retirar := COALESCE(v_extra."Cantidad", 0);

            IF NOT comparar_existenciasalmacen(
                v_det."Id_RegistroMaestro",
                v_source_ubicacion,
                v_cantidad_retirar
            ) THEN
                RAISE EXCEPTION 'DB_ERROR_04 insufficient inventory for Registro %, Ubicacion %, required %',
                    v_det."Id_RegistroMaestro", v_source_ubicacion, v_cantidad_retirar;
            END IF;

            FOR v_lot IN
                SELECT ed."ID", ed."SaldoCierre", ed."CostoPrecioUnitario", ed."FechaHoraApertura"
                  FROM "ExtraDetalle_Documento" ed
                  JOIN "Detalle_Documento" dd ON dd."ID" = ed."Id_DetalleDocumento"
                 WHERE dd."Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
                   AND COALESCE(dd."Id_UbicacionFisica2", dd."Id_UbicacionFisica1") = v_source_ubicacion
                   AND COALESCE(ed."SaldoCierre", 0) > 0
                 ORDER BY
                   CASE WHEN p_metodo_valuacion = 2 THEN ed."FechaHoraApertura" END DESC,
                   CASE WHEN p_metodo_valuacion <> 2 THEN ed."FechaHoraApertura" END ASC,
                   ed."ID"
                 FOR UPDATE OF ed
            LOOP
                EXIT WHEN v_cantidad_retirar <= 0;

                v_cantidad_lote := COALESCE(v_lot."SaldoCierre", 0);
                v_cantidad_segmento := LEAST(v_cantidad_retirar, v_cantidad_lote);

                IF p_metodo_valuacion = 3 THEN
                    v_costo_salida := get_costopromedio(v_det."Id_RegistroMaestro", v_source_ubicacion);
                ELSE
                    v_costo_salida := COALESCE(v_lot."CostoPrecioUnitario", 0);
                END IF;

                v_id_docalm := crear_documento(
                    v_id_sucursal, 'Flujo_Almacen', v_doc."Id_Usuario",
                    p_id_documento, v_doc."Id_ConceptoDocumento", v_doc."Id_DocumentoMovimiento"
                );

                v_id_detalle := restaurante_next_legacy_id('Detalle_Documento');
                INSERT INTO "Detalle_Documento" (
                    "ID", "Id_Documento", "Id_RegistroMaestro", "Id_PersonaFiscal",
                    "Id_UbicacionFisica1", "Id_UbicacionFisica2", "Subtotal",
                    "Comentarios", "Estatus", "Id_CuentaBancaria1", "Id_CuentaBancaria2"
                ) VALUES (
                    v_id_detalle, v_id_docalm, v_det."Id_RegistroMaestro", v_det."Id_PersonaFiscal",
                    v_det."Id_UbicacionFisica1", v_det."Id_UbicacionFisica2",
                    v_cantidad_segmento * v_costo_salida,
                    v_det."Comentarios", v_det."Estatus", v_det."Id_CuentaBancaria1", v_det."Id_CuentaBancaria2"
                );

                INSERT INTO "ExtraDetalle_Documento" (
                    "ID", "Id_DetalleDocumento", "NumeroComensales", "Id_Presentacion",
                    "Cantidad", "CostoPrecioUnitario", "CostoPrecioTotal",
                    "CantidadSurtida", "FechaHoraApertura", "SaldoApertura", "SaldoCierre"
                ) VALUES (
                    restaurante_next_legacy_id('ExtraDetalle_Documento'),
                    v_id_detalle, v_extra."NumeroComensales", v_extra."Id_Presentacion",
                    v_cantidad_segmento, v_costo_salida, v_cantidad_segmento * v_costo_salida,
                    v_extra."CantidadSurtida", LOCALTIMESTAMP, 0, 0
                );

                UPDATE "ExtraDetalle_Documento"
                   SET "SaldoCierre" = "SaldoCierre" - v_cantidad_segmento,
                       "FechaHoraCierre" = CASE
                            WHEN "SaldoCierre" - v_cantidad_segmento <= 0 THEN LOCALTIMESTAMP
                            ELSE "FechaHoraCierre"
                       END
                 WHERE "ID" = v_lot."ID";

                PERFORM 1
                  FROM "RegMaestro_UbicacionFisica"
                 WHERE "Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
                   AND "Id_UbicacionFisica" = v_source_ubicacion
                 FOR UPDATE;

                UPDATE "RegMaestro_UbicacionFisica"
                   SET "Existencias" = COALESCE("Existencias", 0) - v_cantidad_segmento
                 WHERE "Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
                   AND "Id_UbicacionFisica" = v_source_ubicacion;

                UPDATE "Documento"
                   SET "Monto" = v_cantidad_segmento * v_costo_salida
                 WHERE "ID" = v_id_docalm;

                UPDATE "Detalle_Documento"
                   SET "Subtotal" = COALESCE("Subtotal", 0) + (v_cantidad_segmento * v_costo_salida)
                 WHERE "ID" = v_det."ID";

                PERFORM aplicar_asiento(v_id_docalm::int);
                PERFORM cerrar_documento(v_id_docalm::int);

                v_cantidad_retirar := v_cantidad_retirar - v_cantidad_segmento;
            END LOOP;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION aplicar_movimientoalmacen(
    p_id_documento int,
    p_metodo_valuacion int DEFAULT 1
) RETURNS void AS $$
DECLARE
    v_movimiento int;
BEGIN
    SELECT COALESCE(d."Id_DocumentoMovimiento", dc."Id_Movimiento")
      INTO v_movimiento
      FROM "Documento" d
      LEFT JOIN "Documento_Concepto" dc ON dc."ID" = d."Id_ConceptoDocumento"
     WHERE d."ID" = p_id_documento;

    IF v_movimiento = 1 THEN
        PERFORM entrada_movimientoalmacen(p_id_documento);
    ELSIF v_movimiento = 2 THEN
        PERFORM salida_movimientoalmacen(p_id_documento, p_metodo_valuacion);
    ELSIF v_movimiento = 3 THEN
        PERFORM salida_movimientoalmacen(p_id_documento, p_metodo_valuacion);
        PERFORM entrada_movimientoalmacen(p_id_documento);
    ELSE
        RAISE EXCEPTION 'DB_ERROR_07 invalid inventory movement % for Documento %',
            v_movimiento, p_id_documento;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION aplicar_movimientocaja(p_id_documento int)
RETURNS void AS $$
DECLARE
    v_doc record;
    v_id_sucursal int;
    v_movimiento int;
    v_det record;
    v_id_caja int;
    v_estatus text;
    v_saldo numeric;
    v_id_doccaj bigint;
BEGIN
    SELECT *
      INTO v_doc
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    SELECT COALESCE(v_doc."Id_DocumentoMovimiento", dc."Id_Movimiento")
      INTO v_movimiento
      FROM "Documento_Concepto" dc
     WHERE dc."ID" = v_doc."Id_ConceptoDocumento";

    SELECT "Id_Sucursal_Sistema"
      INTO v_id_sucursal
      FROM "Numeracion_Folio"
     WHERE "Id_ClaveFolio" = v_doc."Id_ClaveFolio"
     ORDER BY "ID" DESC
     LIMIT 1;

    FOR v_det IN SELECT * FROM "Detalle_Documento" WHERE "Id_Documento" = p_id_documento ORDER BY "ID"
    LOOP
        v_id_caja := CASE WHEN v_movimiento = 1 THEN v_det."Id_UbicacionFisica1" ELSE v_det."Id_UbicacionFisica2" END;

        SELECT "Estatus"
          INTO v_estatus
          FROM "Ubicacion_Fisica"
         WHERE "ID" = v_id_caja
         FOR UPDATE;

        IF v_estatus = 'C' THEN
            RAISE EXCEPTION 'DB_ERROR_02 cash location % is closed', v_id_caja;
        END IF;

        SELECT COALESCE("SaldoActual", 0)
          INTO v_saldo
          FROM "Detalle_Ubicacion"
         WHERE "ID_UbicacionFisica" = v_id_caja
         FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'DB_ERROR_03 missing Detalle_Ubicacion for cash location %', v_id_caja;
        END IF;

        v_id_doccaj := crear_documento(
            v_id_sucursal, 'Flujo_Caja', v_doc."Id_Usuario",
            p_id_documento, v_doc."Id_ConceptoDocumento", v_movimiento
        );

        INSERT INTO "Detalle_Documento" (
            "ID", "Id_Documento", "Id_PersonaFiscal", "Id_UbicacionFisica1",
            "Id_UbicacionFisica2", "Subtotal", "Comentarios", "Estatus",
            "Id_CuentaBancaria1", "Id_CuentaBancaria2"
        ) VALUES (
            restaurante_next_legacy_id('Detalle_Documento'), v_id_doccaj,
            v_det."Id_PersonaFiscal", v_det."Id_UbicacionFisica1",
            v_det."Id_UbicacionFisica2", v_det."Subtotal", v_det."Comentarios",
            v_det."Estatus", v_det."Id_CuentaBancaria1", v_det."Id_CuentaBancaria2"
        );

        IF v_movimiento = 1 THEN
            v_saldo := v_saldo + COALESCE(v_det."Subtotal", 0);
        ELSIF v_movimiento = 2 THEN
            v_saldo := v_saldo - COALESCE(v_det."Subtotal", 0);
        ELSE
            RAISE EXCEPTION 'DB_ERROR_07 invalid cash movement %', v_movimiento;
        END IF;

        UPDATE "Detalle_Ubicacion"
           SET "SaldoActual" = v_saldo
         WHERE "ID_UbicacionFisica" = v_id_caja;

        UPDATE "Documento" SET "Monto" = COALESCE(v_det."Subtotal", 0) WHERE "ID" = v_id_doccaj;
        PERFORM aplicar_asiento(v_id_doccaj::int);
        PERFORM cerrar_documento(v_id_doccaj::int);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION aplicar_movimientobanco(p_id_documento int)
RETURNS void AS $$
DECLARE
    v_doc record;
    v_id_sucursal int;
    v_movimiento int;
    v_det record;
    v_id_cuenta int;
    v_saldo numeric;
    v_id_docban bigint;
BEGIN
    SELECT *
      INTO v_doc
      FROM "Documento"
     WHERE "ID" = p_id_documento
     FOR UPDATE;

    SELECT COALESCE(v_doc."Id_DocumentoMovimiento", dc."Id_Movimiento")
      INTO v_movimiento
      FROM "Documento_Concepto" dc
     WHERE dc."ID" = v_doc."Id_ConceptoDocumento";

    SELECT "Id_Sucursal_Sistema"
      INTO v_id_sucursal
      FROM "Numeracion_Folio"
     WHERE "Id_ClaveFolio" = v_doc."Id_ClaveFolio"
     ORDER BY "ID" DESC
     LIMIT 1;

    FOR v_det IN SELECT * FROM "Detalle_Documento" WHERE "Id_Documento" = p_id_documento ORDER BY "ID"
    LOOP
        v_id_cuenta := CASE WHEN v_movimiento = 1 THEN v_det."Id_CuentaBancaria1" ELSE v_det."Id_CuentaBancaria2" END;

        SELECT COALESCE("Saldo", 0)
          INTO v_saldo
          FROM "Cuenta_Bancaria"
         WHERE "ID" = v_id_cuenta
         FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'DB_ERROR_03 missing Cuenta_Bancaria %', v_id_cuenta;
        END IF;

        IF v_movimiento = 2 AND v_saldo < COALESCE(v_det."Subtotal", 0) THEN
            RAISE EXCEPTION 'DB_ERROR_04 insufficient bank balance for Cuenta_Bancaria %',
                v_id_cuenta;
        END IF;

        v_id_docban := crear_documento(
            v_id_sucursal, 'Flujo_Bancos', v_doc."Id_Usuario",
            p_id_documento, v_doc."Id_ConceptoDocumento", v_movimiento
        );

        INSERT INTO "Detalle_Documento" (
            "ID", "Id_Documento", "Id_PersonaFiscal", "Id_CuentaBancaria1",
            "Id_CuentaBancaria2", "Subtotal", "Comentarios", "Estatus",
            "Id_UbicacionFisica1", "Id_UbicacionFisica2"
        ) VALUES (
            restaurante_next_legacy_id('Detalle_Documento'), v_id_docban,
            v_det."Id_PersonaFiscal", v_det."Id_CuentaBancaria1",
            v_det."Id_CuentaBancaria2", v_det."Subtotal", v_det."Comentarios",
            v_det."Estatus", v_det."Id_UbicacionFisica1", v_det."Id_UbicacionFisica2"
        );

        IF v_movimiento = 1 THEN
            v_saldo := v_saldo + COALESCE(v_det."Subtotal", 0);
        ELSIF v_movimiento = 2 THEN
            v_saldo := v_saldo - COALESCE(v_det."Subtotal", 0);
        ELSE
            RAISE EXCEPTION 'DB_ERROR_07 invalid bank movement %', v_movimiento;
        END IF;

        UPDATE "Cuenta_Bancaria" SET "Saldo" = v_saldo WHERE "ID" = v_id_cuenta;
        UPDATE "Documento" SET "Monto" = COALESCE(v_det."Subtotal", 0) WHERE "ID" = v_id_docban;
        PERFORM aplicar_asiento(v_id_docban::int);
        PERFORM cerrar_documento(v_id_docban::int);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION calcular_montos_detalle(p_id_detalle_documento int)
RETURNS numeric AS $$
DECLARE
    v_det record;
    v_mc record;
    v_monto numeric;
    v_total numeric := 0;
BEGIN
    SELECT * INTO v_det FROM "Detalle_Documento" WHERE "ID" = p_id_detalle_documento;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'DB_ERROR_03 missing Detalle_Documento %', p_id_detalle_documento;
    END IF;

    DELETE FROM "Monto_Calculado_Detalle" WHERE "Id_DetalleDocumento" = p_id_detalle_documento;

    FOR v_mc IN
        SELECT mc.*
          FROM "RegMaestro_Contabilidad" rmc
          JOIN "PerfilImpuesto_MontoCalculado" pimc
            ON pimc."Id_PerfilImpuesto" = rmc."Id_PerfilImpuesto"
          JOIN "Monto_Calculado" mc ON mc."ID" = pimc."Id_MontoCalculado"
         WHERE rmc."Id_RegistroMaestro" = v_det."Id_RegistroMaestro"
           AND COALESCE(mc."Estatus", 'A') <> 'C'
    LOOP
        v_monto := COALESCE(v_mc."MontoFijo", 0)
                 + (COALESCE(v_det."Subtotal", 0) * COALESCE(v_mc."PorcentajeOperacion", 0) / 100.0);

        INSERT INTO "Monto_Calculado_Detalle" (
            "ID", "Id_MontoCalculado", "Id_DetalleDocumento", "Monto"
        ) VALUES (
            restaurante_next_legacy_id('Monto_Calculado_Detalle'),
            v_mc."ID", p_id_detalle_documento, v_monto
        );

        v_total := v_total + v_monto;
    END LOOP;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION calcular_montos_documento(p_id_documento int)
RETURNS numeric AS $$
DECLARE
    v_total numeric;
BEGIN
    SELECT COALESCE(SUM(COALESCE("Monto", 0)), 0)
      INTO v_total
      FROM "Monto_Calculado_Documento"
     WHERE "Id_Documento" = p_id_documento;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION registrar_montos_documento(p_id_documento int)
RETURNS void AS $$
DECLARE
    v_det record;
BEGIN
    FOR v_det IN SELECT "ID" FROM "Detalle_Documento" WHERE "Id_Documento" = p_id_documento LOOP
        PERFORM calcular_montos_detalle(v_det."ID");
    END LOOP;

    PERFORM recalcular_documento(p_id_documento);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION calcular_puntoreorden(p_id_registro_maestro int)
RETURNS numeric AS $$
DECLARE
    v_inventario_seguridad numeric;
    v_dias_calculo int := 30;
    v_total_entrega int := 7;
    v_consumo numeric;
BEGIN
    SELECT COALESCE("InventarioSeguridad", 0)
      INTO v_inventario_seguridad
      FROM "RegMaestro_Inventario"
     WHERE "Id_RegistroMaestro" = p_id_registro_maestro
     ORDER BY "ID" DESC
     LIMIT 1;

    SELECT COALESCE(SUM(COALESCE(ed."Cantidad", 0)), 0)
      INTO v_consumo
      FROM "Documento" d
      JOIN "Detalle_Documento" dd ON dd."Id_Documento" = d."ID"
      JOIN "ExtraDetalle_Documento" ed ON ed."Id_DetalleDocumento" = dd."ID"
     WHERE dd."Id_RegistroMaestro" = p_id_registro_maestro
       AND COALESCE(d."Id_DocumentoMovimiento", 2) = 2
       AND d."Fecha/Hora" >= LOCALTIMESTAMP - make_interval(days => v_dias_calculo);

    RETURN (COALESCE(v_consumo, 0) / v_dias_calculo * v_total_entrega)
           + COALESCE(v_inventario_seguridad, 0);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE VIEW vw_existencias_almacen AS
SELECT
    rmu."Id_RegistroMaestro",
    rm."Nombre" AS "RegistroMaestro",
    rmu."Id_UbicacionFisica",
    uf."Nombre" AS "UbicacionFisica",
    uf."Id_SucursalSistema",
    rmu."Existencias"
FROM "RegMaestro_UbicacionFisica" rmu
LEFT JOIN "Registro_Maestro" rm ON rm."ID" = rmu."Id_RegistroMaestro"
LEFT JOIN "Ubicacion_Fisica" uf ON uf."ID" = rmu."Id_UbicacionFisica";


CREATE OR REPLACE VIEW vw_movimientos_almacen AS
SELECT
    d."ID" AS "Id_Documento",
    d."Fecha/Hora",
    d."FolioDocumento",
    d."Estatus",
    dd."ID" AS "Id_DetalleDocumento",
    dd."Id_RegistroMaestro",
    dd."Id_UbicacionFisica1",
    dd."Id_UbicacionFisica2",
    ed."Cantidad",
    ed."CostoPrecioUnitario",
    ed."CostoPrecioTotal",
    ed."SaldoCierre"
FROM "Documento" d
JOIN "Detalle_Documento" dd ON dd."Id_Documento" = d."ID"
LEFT JOIN "ExtraDetalle_Documento" ed ON ed."Id_DetalleDocumento" = dd."ID";


CREATE OR REPLACE VIEW vw_movimientos_caja AS
SELECT
    d."ID" AS "Id_Documento",
    d."Fecha/Hora",
    d."FolioDocumento",
    d."Estatus",
    dd."Id_PersonaFiscal",
    dd."Id_UbicacionFisica1",
    dd."Id_UbicacionFisica2",
    dd."Subtotal"
FROM "Documento" d
JOIN "Detalle_Documento" dd ON dd."Id_Documento" = d."ID"
WHERE dd."Id_UbicacionFisica1" IS NOT NULL OR dd."Id_UbicacionFisica2" IS NOT NULL;


CREATE OR REPLACE VIEW vw_movimientos_banco AS
SELECT
    d."ID" AS "Id_Documento",
    d."Fecha/Hora",
    d."FolioDocumento",
    d."Estatus",
    dd."Id_PersonaFiscal",
    dd."Id_CuentaBancaria1",
    dd."Id_CuentaBancaria2",
    dd."Subtotal"
FROM "Documento" d
JOIN "Detalle_Documento" dd ON dd."Id_Documento" = d."ID"
WHERE dd."Id_CuentaBancaria1" IS NOT NULL OR dd."Id_CuentaBancaria2" IS NOT NULL;


CREATE OR REPLACE VIEW vw_movimientos_contables AS
SELECT
    mc."ID" AS "Id_MovimientoContable",
    mc."ID_LibroSucursal",
    mc."ID_DocumentoConcepto",
    mc."ID_Documento",
    d."Fecha/Hora",
    d."FolioDocumento",
    d."Monto"
FROM "Movimiento_Contable" mc
LEFT JOIN "Documento" d ON d."ID" = mc."ID_Documento";
