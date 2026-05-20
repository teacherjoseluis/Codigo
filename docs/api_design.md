# API design roadmap

The API layer should sit above the existing repository/factory domain layer.
Legacy business tables remain unmanaged by Django migrations; API code translates
HTTP requests into domain operations and returns stable response shapes.

## Conventions

- Base path: `/api/v1/`.
- Authentication: Django `contrib.auth` users via DRF token authentication.
  Clients log in with `POST /api/v1/auth/login/` and send
  `Authorization: Token <token>` on protected requests.
- Permissions: require authenticated users by default. Treat
  `AuthUser_Sucursal` and `AuthUser_UbicacionFisica` as scoping tables, not as
  user sources of truth.
- Writes: call repository/factory classes instead of mutating legacy models
  directly. Use `transaction.atomic()` for workflows that span multiple tables.
- Request tracing: every response includes `X-Request-ID`. Clients may pass the
  same header to correlate retries and support tickets.
- Pagination: list endpoints return DRF page envelopes:
  `count`, `next`, `previous`, and `results`. Clients may request
  `page` and `page_size` up to the configured maximum.
- Filtering/search/ordering: list endpoints expose `search` and `ordering`
  query parameters where a stable field set has been defined.
- Schema: `GET /api/v1/schema/` exposes the OpenAPI contract.
- Errors:
  - `ObjectDoesNotExist` -> `404` when the requested resource is missing.
  - `ValueError` -> `400` validation error.
  - `IntegrityError` -> `409` conflict for duplicate/incompatible state.
- Error response format: `detail`, `code`, optional `request_id`, and optional
  `errors` for field-level validation details.
- Success response format: JSON objects using existing model field names during
  the first API phase. Introduce public DTO aliases only when frontend contracts
  require them.
- Versioning: add incompatible changes under a new version prefix.

## Current skeleton

The API increment exposes read-only metadata, Registro Maestro, and the first
transactional workflow endpoints:

```text
GET /api/v1/schema/
GET /api/v1/health/
POST /api/v1/auth/login/
GET /api/v1/auth/me/
POST /api/v1/auth/logout/
GET /api/v1/sucursales/
GET /api/v1/sucursales/{id}/
GET /api/v1/catalogos/clasificaciones/
GET /api/v1/catalogos/unidades-medida/
GET /api/v1/catalogos/presentaciones/
GET /api/v1/catalogos/tipos-cuenta-contable/
GET/POST /api/v1/registros-maestro/
GET/PATCH /api/v1/registros-maestro/{id}/
POST /api/v1/registros-maestro/{id}/disable/
GET/PUT /api/v1/registros-maestro/{id}/{contexto}/
```

`/api/v1/health/` is public. Business endpoints require authentication.

## Endpoint roadmap

### Phase 1: API foundation and read-only metadata

- Add DRF configuration, v1 URL routing, serializers, API tests, and shared
  exception mapping.
- Expose sucursal list/detail endpoints and catalog list endpoints.
- Add OpenAPI/schema generation once the endpoint naming settles.

### Phase 2: physical locations

Map HTTP actions to `UbicacionFisica_Repo`, `Mesa`, `Caja`,
`AreaPreparacion`, and `Almacen`.

```text
GET    /api/v1/ubicaciones/
GET    /api/v1/ubicaciones/{id}/
PATCH  /api/v1/ubicaciones/{id}/status/
POST   /api/v1/ubicaciones/{id}/disable/
GET    /api/v1/ubicaciones/{id}/balance/
GET    /api/v1/ubicaciones/{id}/users/
POST   /api/v1/ubicaciones/{id}/users/
DELETE /api/v1/ubicaciones/{id}/users/{user_id}/
```

Typed resources:

```text
GET/POST  /api/v1/mesas/
GET/PATCH /api/v1/mesas/{id}/
GET/POST  /api/v1/cajas/
GET/PATCH /api/v1/cajas/{id}/
GET/POST  /api/v1/areas-preparacion/
GET/PATCH /api/v1/areas-preparacion/{id}/
GET       /api/v1/areas-preparacion/{id}/stock/{registro_maestro_id}/
GET/POST  /api/v1/almacenes/
GET/PATCH /api/v1/almacenes/{id}/
GET       /api/v1/almacenes/{id}/stock/{registro_maestro_id}/
```

### Phase 3: registro maestro

Map writes through `RegMaestro` and its context factories.

```text
GET    /api/v1/registros-maestro/
POST   /api/v1/registros-maestro/
GET    /api/v1/registros-maestro/{id}/
PATCH  /api/v1/registros-maestro/{id}/
POST   /api/v1/registros-maestro/{id}/disable/
GET/PUT /api/v1/registros-maestro/{id}/compra/
GET/PUT /api/v1/registros-maestro/{id}/venta/
GET/PUT /api/v1/registros-maestro/{id}/inventario/
GET/PUT /api/v1/registros-maestro/{id}/contabilidad/
GET/PUT /api/v1/registros-maestro/{id}/pedimento/
GET/PUT /api/v1/registros-maestro/{id}/foto/
GET/PUT /api/v1/registros-maestro/{id}/ubicaciones/{ubicacion_id}/
```

### Phase 4: transactional domains

Implemented as the first transactional API slice. Document creation accepts
optional nested detalles, movimientos contables, and asiento mappings in a
single atomic operation. If a nested row fails validation, the document header
is rolled back.

```text
GET/POST   /api/v1/documentos/
GET/PATCH  /api/v1/documentos/{id}/
GET/POST   /api/v1/documentos/{id}/detalles/
GET/PATCH  /api/v1/documentos/{id}/detalles/{detalle_id}/
GET/POST   /api/v1/documentos/{id}/detalles/{detalle_id}/extras/
GET/POST   /api/v1/documentos/{id}/movimientos/
GET/PATCH  /api/v1/documentos/{id}/movimientos/{movimiento_id}/
GET/POST   /api/v1/documentos/{id}/asientos/

GET/POST   /api/v1/folios/
GET/PATCH  /api/v1/folios/{id}/
GET/POST   /api/v1/folios/{id}/numeraciones/

GET/POST   /api/v1/personas-fiscales/
GET/PATCH  /api/v1/personas-fiscales/{id}/
GET/POST   /api/v1/proveedores/
GET/PATCH  /api/v1/proveedores/{id}/
GET/POST   /api/v1/clientes/
GET/PATCH  /api/v1/clientes/{id}/
GET/POST   /api/v1/cuentas-contables/
GET/PATCH  /api/v1/cuentas-contables/{id}/

GET/POST   /api/v1/catalogos/documento-movimientos/
GET/POST   /api/v1/catalogos/documento-conceptos/
GET/POST   /api/v1/catalogos/asientos-contables/
```

Remaining deferred transactional work:

- `empleados` and employee-specific permissions.
- Posting rules that modify stock balances or accounting ledgers beyond the
  current document, detalle, movimiento, and asiento row persistence.
- Idempotency keys for externally retried document creation requests.
- Deeper concurrency controls around folio reservation and stock movements once
  the frontend request patterns are known.

### Phase 5: high-level comanda vertical slice

The first configuration-backed high-level workflow models a waiter taking an
order, routing line items to kitchen/bar preparation areas, marking items ready
and delivered, creating a nota de venta, and receiving payment. These endpoints
orchestrate lower-level `Documento`, `Detalle_Documento`, and
`ExtraDetalle_Documento` persistence plus comanda-specific support tables.

```text
GET  /api/v1/comandas/abiertas/
POST /api/v1/comandas/
GET/PATCH /api/v1/comandas/{id}/
GET/POST /api/v1/comandas/{id}/items/
POST /api/v1/comandas/{id}/enviar-a-preparacion/
POST /api/v1/comandas/{id}/items/{item_id}/entregar/
POST /api/v1/comandas/{id}/cerrar/

GET  /api/v1/preparacion/ordenes/
POST /api/v1/preparacion/ordenes/{id}/items/{item_id}/lista/

POST /api/v1/notas-venta/{id}/pagos/
```

Minimal support tables for this slice:

- `Configuracion_Comanda`: effective sucursal-level behavior for inventory
  validation and automatic nota de venta creation.
- `Regla_RuteoPreparacion`: item/category routing to preparation areas and
  output modes.
- `Receta_Item`: dish/beverage composition used to validate ingredient
  availability.
- `Comanda`, `Comanda_Item`, `Preparacion_Orden`,
  `Preparacion_OrdenItem`, and `Pago_Cliente`: high-level workflow state that
  does not fit cleanly in the legacy document tables.

## Implementation checklist for each endpoint group

1. Define serializer input/output contracts.
2. Add view/viewset that delegates writes to repository/factory classes.
3. Add permission checks for sucursal/ubicacion scope.
4. Add tests for auth, success, not found, validation, and conflict paths.
5. Document endpoint examples and update the endpoint inventory.
