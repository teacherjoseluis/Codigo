# Database Logic Specification

The implementation in `restaurante/sql/database_logic.sql` was derived from the
local Restaurante reference folder:

- `BD_LOGIC_SPEC.md`
- `BD/Modelo.org`
- `BD/Query.txt`
- `BD/SQL/*.sql`
- `REQS/Servicios.txt`
- `REQS/MontosCalculados.txt`
- `REQS/UI/Forms.txt`
- `REQS/Problemática.docx`
- `REQS/restaurante.xlsm`

Use the root-level `BD_LOGIC_SPEC.md` from the reference package as the
authoritative business specification. This repo-local note exists so future
contributors know where the database artifacts came from and which file to
install.

## Installed Artifact

Run:

```bash
python3 manage.py install_database_logic
python3 manage.py seed_database_logic_config
```

The command executes:

```text
restaurante/sql/database_logic.sql
```

`seed_flow_folio_config` is idempotent supporting-data setup for the generated
flow document names used by the SQL functions: `Flujo_Almacen`, `Flujo_Caja`,
`Flujo_Bancos`, and `Flujo_Contable`.
`seed_database_logic_config` includes that flow setup and also seeds the
minimal document movements, operational source folio/concepts, accounts, and
current accounting book rows needed by database workflow tests and local API
development.

## Implemented Coverage

- `restaurante_next_legacy_id`
- `generar_nuevofolio`
- `crear_documento`
- `recalcular_documento`
- `cerrar_documento`
- `comparar_existenciasalmacen`
- `comparar_saldobanco`
- `get_costopromedio`
- `entrada_movimientoalmacen`
- `salida_movimientoalmacen`
- `aplicar_movimientoalmacen`
- `aplicar_movimientocaja`
- `aplicar_movimientobanco`
- `aplicar_asiento`
- `calcular_montos_detalle`
- `calcular_montos_documento`
- `registrar_montos_documento`
- `calcular_puntoreorden`
- movement/read views prefixed with `vw_`

## Remaining Domain Decisions

The legacy schema and old SQL drafts leave a few business conventions open.
Before production use, confirm these with seed data and workflow tests:

- exact numeric mapping for `Cuenta_Contable.Tipo`;
- whether inventory exits always use `Id_UbicacionFisica2` as the source when
  present;
- whether generated flow documents should be one per origin, one per detail, or
  one per consumed lot segment;
- whether negative cash balances are allowed;
- final rounding rules for calculated amounts and taxes.
