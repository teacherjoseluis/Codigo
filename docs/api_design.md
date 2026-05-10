# API design roadmap

The API layer should sit above the existing repository/factory domain layer.
Legacy business tables remain unmanaged by Django migrations; API code translates
HTTP requests into domain operations and returns stable response shapes.

## Conventions

- Base path: `/api/v1/`.
- Authentication: Django `contrib.auth` users via DRF session/basic
  authentication to start. Token auth can be added once client requirements are
  clear.
- Permissions: require authenticated users by default. Treat
  `AuthUser_Sucursal` and `AuthUser_UbicacionFisica` as scoping tables, not as
  user sources of truth.
- Writes: call repository/factory classes instead of mutating legacy models
  directly. Use `transaction.atomic()` for workflows that span multiple tables.
- Errors:
  - `ObjectDoesNotExist` -> `404` when the requested resource is missing.
  - `ValueError` -> `400` validation error.
  - `IntegrityError` -> `409` conflict for duplicate/incompatible state.
- Response format: JSON objects/lists using existing model field names during
  the first API phase. Introduce public DTO aliases only when frontend contracts
  require them.
- Versioning: add incompatible changes under a new version prefix.

## Current skeleton

The first API increment exposes safe, read-only endpoints that help validate the
HTTP stack without opening transactional workflows:

```text
GET /api/v1/health/
GET /api/v1/sucursales/
GET /api/v1/sucursales/{id}/
GET /api/v1/catalogos/clasificaciones/
GET /api/v1/catalogos/unidades-medida/
GET /api/v1/catalogos/presentaciones/
GET /api/v1/catalogos/tipos-cuenta-contable/
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

Defer these until the lower-risk endpoints prove the API conventions:

```text
/api/v1/documentos/
/api/v1/documentos/{id}/detalles/
/api/v1/documentos/{id}/movimientos/
/api/v1/documentos/{id}/asientos/
/api/v1/personas-fiscales/
/api/v1/proveedores/
/api/v1/clientes/
/api/v1/empleados/
/api/v1/folios/
/api/v1/cuentas-contables/
```

## Implementation checklist for each endpoint group

1. Define serializer input/output contracts.
2. Add view/viewset that delegates writes to repository/factory classes.
3. Add permission checks for sucursal/ubicacion scope.
4. Add tests for auth, success, not found, validation, and conflict paths.
5. Document endpoint examples and update the endpoint inventory.
