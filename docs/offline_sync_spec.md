# Offline Sync Capability Specification

This document defines an implementation-ready plan for emergency offline
operation while keeping Django as the default middleware and API layer.

The goal is not direct database replication. Local restaurant clients should
cache stable reads, queue business commands while disconnected, and replay those
commands to Django when connectivity returns. Django remains the rule-enforcing
boundary and PostgreSQL remains the authoritative store.

## Objectives

- Keep `/api/v1/` as the primary contract for online operation.
- Allow restaurant terminals to continue taking orders during short connectivity
  loss.
- Make catalog, menu, sucursal, and configuration data available from local
  snapshots.
- Replay offline mutations through Django services, not direct PostgreSQL row
  writes.
- Preserve auditability, idempotency, and conflict visibility.
- Make the offline layer mostly transparent for clients while still surfacing
  critical "pending sync" and "needs review" states.

## Non-goals

- Full multi-master PostgreSQL replication.
- Silent acceptance of payments, inventory consumption, or final folios without
  server confirmation.
- Replacing Django as the application middleware.
- Hiding all offline state from operators.
- Supporting arbitrary admin/master-data edits while offline.

## Current API classification

### Snapshot-friendly reads

These resources can be cached locally with versioning and refresh metadata:

- `GET /api/v1/health/`
- `GET /api/v1/schema/`
- `GET /api/v1/sucursales/`
- `GET /api/v1/sucursales/{id}/`
- `GET /api/v1/catalogos/clasificaciones/`
- `GET /api/v1/catalogos/unidades-medida/`
- `GET /api/v1/catalogos/presentaciones/`
- `GET /api/v1/catalogos/tipos-cuenta-contable/`
- `GET /api/v1/registros-maestro/`
- `GET /api/v1/registros-maestro/{id}/`
- `GET /api/v1/registros-maestro/{id}/venta/`
- `GET /api/v1/registros-maestro/{id}/inventario/`
- `GET /api/v1/registros-maestro/{id}/ubicaciones/{ubicacion_id}/`

Notes:

- Catalog and menu snapshots should include a generated timestamp and version.
- Stock snapshots are advisory only. They must not be treated as authoritative
  at replay time.
- Local clients should fetch all pages or use dedicated bulk sync endpoints.

### Read-through but volatile

These may be cached briefly for display, but stale state must be visible:

- `GET /api/v1/comandas/abiertas/`
- `GET /api/v1/comandas/`
- `GET /api/v1/comandas/{id}/`
- `GET /api/v1/comandas/{id}/items/`
- `GET /api/v1/preparacion/ordenes/`
- `GET /api/v1/documentos/`

Notes:

- Use them for "last known state" only.
- Show `last_synced_at` in the local UI.
- Do not make irreversible decisions based only on these cached responses.

### Command/replay required

These write endpoints are not safe as simple response-cache entries:

- `POST /api/v1/comandas/`
- `PATCH /api/v1/comandas/{id}/`
- `POST /api/v1/comandas/{id}/items/`
- `POST /api/v1/comandas/{id}/enviar-a-preparacion/`
- `POST /api/v1/comandas/{id}/items/{item_id}/entregar/`
- `POST /api/v1/comandas/{id}/cerrar/`
- `POST /api/v1/preparacion/ordenes/{id}/items/{item_id}/lista/`
- `POST /api/v1/notas-venta/{id}/pagos/`
- `POST/PATCH/PUT` master-data and document endpoints

Notes:

- These must be represented as queued commands with idempotency keys.
- Replay must call Django services and return operation-level results.
- The local client must retain commands until Django confirms durable handling.

## High-level architecture

```text
Online:
  Frontend/POS client -> Django API -> PostgreSQL

Intermittent/offline:
  Frontend/POS client -> Local data access layer
                         - snapshot store
                         - local operation queue
                         - local ID map
                         - sync worker
                       -> Django sync endpoints when reachable
                       -> PostgreSQL
```

The local data access layer may be implemented as:

- a browser service worker plus IndexedDB;
- an Electron/Tauri/native POS client with SQLite;
- a small local edge service per restaurant;
- a mobile local database and background sync worker.

The selected client technology can vary. The server contract should remain the
same.

## Required server data model

Because this project keeps legacy business tables unmanaged by Django
migrations, create these tables through the same external schema/bootstrap
strategy used for the legacy schema.

### `SyncClient`

Registered offline-capable device or local node.

Recommended fields:

- `id`
- `client_uuid`
- `display_name`
- `id_sucursal`
- `id_ubicacionfisica`
- `client_type`: `pos`, `kitchen`, `cashier`, `edge_node`
- `status`: `active`, `suspended`, `revoked`
- `last_seen_at`
- `last_successful_sync_at`
- `snapshot_version`
- `created_at`
- `updated_at`

Constraints:

- Unique `client_uuid`.
- Active clients must be scoped to allowed sucursal/ubicacion records.

### `SyncBatch`

One upload attempt from a client.

Recommended fields:

- `id`
- `batch_uuid`
- `client_uuid`
- `status`: `received`, `processing`, `completed`, `partial`, `failed`
- `operation_count`
- `applied_count`
- `duplicate_count`
- `conflict_count`
- `received_at`
- `completed_at`
- `request_hash`
- `response_payload`

Constraints:

- Unique `(client_uuid, batch_uuid)`.

### `SyncOperation`

One queued command within a batch.

Recommended fields:

- `id`
- `operation_uuid`
- `batch_uuid`
- `client_uuid`
- `operation_type`
- `sequence_number`
- `depends_on_operation_uuid`
- `idempotency_key`
- `payload_hash`
- `payload`
- `status`: `pending`, `applied`, `duplicate`, `rejected`, `conflict`,
  `needs_manual_review`
- `server_resource_type`
- `server_resource_id`
- `result_payload`
- `error_code`
- `error_detail`
- `created_client_at`
- `received_server_at`
- `applied_server_at`

Constraints:

- Unique `(client_uuid, operation_uuid)`.
- Unique `idempotency_key`.
- Ordered processing by `sequence_number`.

### `IdempotencyRecord`

Durable replay protection for unsafe requests.

Recommended fields:

- `id`
- `idempotency_key`
- `client_uuid`
- `request_method`
- `request_path`
- `payload_hash`
- `status_code`
- `response_payload`
- `operation_status`
- `created_at`
- `expires_at`

Behavior:

- Same key and same payload hash returns the stored response.
- Same key and different payload hash returns `409 conflict`.
- Records for financial and inventory-affecting operations should have long
  retention.

### `ConflictRecord`

Manual reconciliation trail.

Recommended fields:

- `id`
- `operation_uuid`
- `client_uuid`
- `conflict_type`
- `severity`: `warning`, `blocking`, `financial`, `inventory`
- `local_payload`
- `server_state`
- `resolution_status`: `open`, `resolved`, `dismissed`
- `resolution_notes`
- `created_at`
- `resolved_at`
- `resolved_by_user_id`

## Sync API endpoints

### Register or inspect client

```text
GET  /api/v1/sync/client/
POST /api/v1/sync/client/register/
```

`POST` request:

```json
{
  "client_uuid": "pos-01-uuid",
  "display_name": "POS 01",
  "client_type": "pos",
  "id_sucursal": 1,
  "id_ubicacionfisica": 10
}
```

Response:

```json
{
  "client_uuid": "pos-01-uuid",
  "status": "active",
  "server_time": "2026-05-20T00:00:00Z",
  "sync_contract_version": "1.0"
}
```

### Bootstrap snapshot

```text
GET /api/v1/sync/bootstrap/
```

Query parameters:

- `sucursal_id`
- `include`: comma-separated list such as
  `catalogos,menu,configuracion,ubicaciones`
- `snapshot_version`: optional client version for delta checks

Response:

```json
{
  "snapshot_version": "2026-05-20T00:00:00Z:abc123",
  "generated_at": "2026-05-20T00:00:00Z",
  "server_time": "2026-05-20T00:00:00Z",
  "resources": {
    "sucursales": [],
    "catalogos": {},
    "menu": [],
    "ubicaciones": [],
    "configuracion_comanda": []
  }
}
```

Headers:

- `ETag`
- `Cache-Control: private, max-age=300`
- `X-Snapshot-Version`

If the snapshot did not change, support:

```text
304 Not Modified
```

### Pull changes since snapshot

```text
GET /api/v1/sync/changes/?since={snapshot_version}
```

Response:

```json
{
  "from_snapshot_version": "old",
  "to_snapshot_version": "new",
  "changed": {
    "registros_maestro": [],
    "catalogos": [],
    "configuracion": []
  },
  "deleted": {
    "registros_maestro": []
  }
}
```

Initial implementation may return `409 full_snapshot_required` if deltas are not
yet available.

### Submit queued operations

```text
POST /api/v1/sync/operations/
```

Required headers:

- `X-Sync-Client-ID`
- `Idempotency-Key`
- `X-Request-ID`

Request:

```json
{
  "batch_uuid": "batch-uuid",
  "client_uuid": "pos-01-uuid",
  "snapshot_version": "2026-05-20T00:00:00Z:abc123",
  "client_started_at": "2026-05-20T00:01:00Z",
  "operations": [
    {
      "operation_uuid": "op-1",
      "sequence_number": 1,
      "operation_type": "comanda.create",
      "idempotency_key": "pos-01:op-1",
      "created_client_at": "2026-05-20T00:01:10Z",
      "payload": {
        "local_comanda_id": "local-comanda-1",
        "id_sucursal": 1,
        "id_mesa": 12,
        "numero_comensales": 2,
        "tipo_orden": "venta"
      }
    }
  ]
}
```

Response:

```json
{
  "batch_uuid": "batch-uuid",
  "status": "completed",
  "server_time": "2026-05-20T00:02:00Z",
  "id_map": {
    "local-comanda-1": {
      "resource_type": "comanda",
      "server_id": 123,
      "folio": "OCM-50"
    }
  },
  "results": [
    {
      "operation_uuid": "op-1",
      "status": "applied",
      "server_resource_type": "comanda",
      "server_resource_id": 123,
      "response": {}
    }
  ]
}
```

### Inspect sync status

```text
GET /api/v1/sync/status/
GET /api/v1/sync/batches/{batch_uuid}/
GET /api/v1/sync/conflicts/
GET /api/v1/sync/conflicts/{id}/
PATCH /api/v1/sync/conflicts/{id}/
```

These endpoints power client-side states such as `offline`, `syncing`,
`synced`, and `needs_review`.

## Supported command types

### `comanda.create`

Maps to the existing comanda creation service.

Payload:

- `local_comanda_id`
- `id_sucursal`
- `id_mesa`
- `id_mesero`
- `numero_comensales`
- `tipo_orden`

Replay result:

- server comanda ID
- server documento ID
- final server folio

Conflicts:

- invalid or unauthorized sucursal
- missing/inactive mesa
- duplicate operation UUID
- client not scoped to requested ubicacion

### `comanda.update`

Maps to editable fields currently exposed through the comanda detail PATCH.

Payload:

- `local_or_server_comanda_id`
- partial fields such as `numero_comensales`, `tipo_orden`, `estatus`

Conflicts:

- comanda already closed/cancelled
- stale local status transition
- unauthorized mesa/sucursal

### `comanda.item.add`

Maps to the existing item-add service.

Payload:

- `local_item_id`
- `local_or_server_comanda_id`
- `id_registromaestro`
- `cantidad`
- `precio_unitario`
- `notas`

Replay result:

- server item ID
- server detalle documento ID
- warnings for recipe or inventory validation

Conflicts:

- comanda not editable
- menu item disabled or missing
- no preparation routing rule
- snapshot price differs from current server price
- inventory validation blocks the item

Price handling:

- Include the client price and snapshot version.
- Server decides whether to accept historical price, current price, or reject.
- Initial recommendation: accept the client price if the operation was created
  during offline mode and the item existed in the snapshot, but return a warning
  when server price changed.

### `comanda.send_to_preparation`

Maps to sending pending items to preparation.

Payload:

- `local_or_server_comanda_id`
- optional list of local/server item IDs

Conflicts:

- no pending items
- items already sent by another device
- comanda closed/cancelled
- routing configuration changed

### `preparacion.item.complete`

Maps to marking a kitchen item ready.

Payload:

- `local_or_server_orden_id`
- `local_or_server_item_id`

Conflicts:

- preparation order does not exist yet because a dependency failed
- item already ready or delivered
- item was cancelled

### `comanda.item.deliver`

Maps to marking an item delivered.

Payload:

- `local_or_server_comanda_id`
- `local_or_server_item_id`

Conflicts:

- item not ready
- item cancelled
- comanda closed

### `comanda.close`

Maps to closing the comanda and optionally creating a nota de venta.

Payload:

- `local_or_server_comanda_id`
- `close_requested_at`
- optional `local_nota_venta_id`

Replay result:

- final comanda state
- nota de venta ID and folio, if created
- inventory movements

Conflicts:

- comanda has unprepared or undelivered blocking items
- inventory insufficient and negative inventory is disabled
- comanda already closed/cancelled
- server total differs from local total
- missing ingredient recipe when validation blocks closure

### `nota_venta.payment.record_cash`

Maps to payment registration for cash-like destinations.

Payload:

- `local_payment_id`
- `local_or_server_nota_venta_id`
- `monto`
- `metodo_pago`: `efectivo`
- `destino`: `caja`
- `id_caja`

Replay result:

- payment ID
- payment document ID
- nota de venta status
- cash drawer movement

Conflicts:

- nota de venta is not payable
- payment exceeds remaining balance
- caja unavailable or unauthorized
- duplicate payment operation
- cash drawer closed for the business day

Initial restriction:

- Bank/card payments should remain online-only unless the payment provider has
  a certified offline mode. Offline card authorization is outside this Django
  sync contract.

## Local client behavior

### Online mode

- Send requests directly to Django.
- Persist successful responses needed for local display.
- Store snapshot version and server time.
- Use idempotency keys for all unsafe requests.

### Intermittent mode

- Attempt online request first.
- If the network fails before a response is received, move the operation to the
  local queue and mark it `pending_sync`.
- If the response is received but the acknowledgement is lost, retry with the
  same idempotency key.
- Reads fall back to local snapshots with visible freshness metadata.

### Offline mode

- Serve catalog/menu/configuration reads from local storage.
- Create local temporary IDs for new entities.
- Accept only command types explicitly allowed offline.
- Mark receipts, folios, payments, and inventory-affecting operations as
  provisional.
- Keep a monotonic local sequence number per client.

### Reconnected mode

- Sync in this order:
  1. refresh server time and client status;
  2. refresh snapshot or detect `full_snapshot_required`;
  3. upload queued command batches;
  4. apply ID mappings and final folios;
  5. surface conflicts;
  6. clear applied commands only after durable acknowledgement.

## ID and folio strategy

Local clients must not assign final authoritative folios.

Use temporary display identifiers while offline:

```text
LOCAL-{client_short_id}-{local_counter}
```

Examples:

- `LOCAL-POS01-000012`
- `LOCAL-KITCHEN01-000004`

During replay, Django assigns final folios through the existing server-side
folio logic. The sync response maps local identifiers to final server
identifiers and folios.

Future option:

- Pre-reserved folio blocks per terminal can reduce operator surprise, but this
  requires expiration, revocation, and reconciliation rules. Do not implement
  this in the first offline release.

## Idempotency rules

Every unsafe operation must carry:

- `X-Sync-Client-ID`
- `Idempotency-Key`
- `operation_uuid`
- `payload_hash`

Server behavior:

- New key: process and store response.
- Existing key with same payload hash: return stored response.
- Existing key with different payload hash: return `409 idempotency_conflict`.
- Existing operation already applied in a previous batch: return `duplicate`
  with the original result.

Retention:

- Order and kitchen operations: retain for at least the operational audit
  period.
- Payment and inventory-affecting operations: retain according to financial
  audit requirements.

## Batch processing rules

- Process operations in `sequence_number` order.
- Stop dependent operations when a prerequisite fails.
- Continue independent operations when possible.
- Return operation-level statuses even when the batch is partially applied.
- Make each operation atomic.
- Do not wrap a large offline batch in a single database transaction unless all
  operations must succeed or fail together.

Batch statuses:

- `completed`: all operations applied or duplicate.
- `partial`: at least one operation applied and at least one failed/conflicted.
- `failed`: no operation applied because of request-level validation.
- `needs_manual_review`: one or more conflicts require operator action.

## Conflict response contract

Each failed or conflicted operation should return:

```json
{
  "operation_uuid": "op-10",
  "status": "conflict",
  "code": "inventory_insufficient",
  "detail": "Ingredient 55 requires 3 units but only 1 is available.",
  "severity": "inventory",
  "server_state": {},
  "local_payload": {},
  "recommended_action": "review_or_adjust_order"
}
```

Common status values:

- `applied`
- `duplicate`
- `rejected`
- `conflict`
- `needs_manual_review`

Common conflict codes:

- `client_revoked`
- `scope_denied`
- `snapshot_too_old`
- `dependency_failed`
- `resource_missing`
- `resource_not_editable`
- `folio_conflict`
- `price_changed`
- `routing_missing`
- `inventory_insufficient`
- `recipe_missing`
- `payment_exceeds_balance`
- `payment_destination_unavailable`
- `already_closed`
- `already_paid`

## Edge cases and required behavior

### Network drops after server commit

Problem:

- Client sends a write, Django commits it, response never reaches client.

Required behavior:

- Client retries with the same idempotency key.
- Django returns the stored result instead of creating a duplicate comanda,
  payment, folio, or inventory movement.

### Duplicate batch upload

Problem:

- The same batch is submitted multiple times after reconnection.

Required behavior:

- `SyncBatch` detects duplicate `(client_uuid, batch_uuid)`.
- Previously applied operations return `duplicate` with original results.

### Local entity dependencies

Problem:

- A queued item references a local comanda ID that does not exist on the server.

Required behavior:

- Server resolves local IDs from earlier successful operations in the same batch
  or prior batches.
- If the create operation failed, dependent operations return
  `dependency_failed`.

### Stale menu or price

Problem:

- Client sells an item using an old snapshot.

Required behavior:

- If item is disabled before replay, return `conflict`.
- If price changed, apply configured policy:
  - accept offline price with warning;
  - apply current price and return adjustment;
  - reject and require review.

Initial recommendation:

- Accept offline price for comanda items created during a valid offline window,
  but mark the operation with `price_changed`.

### Stale routing configuration

Problem:

- Item routing to kitchen/bar changed while client was offline.

Required behavior:

- Replay uses current server routing.
- If no route exists, operation conflicts with `routing_missing`.
- Client should show the item as needing manager review.

### Inventory drift

Problem:

- Local stock snapshot says ingredients are available, but server stock is
  insufficient at close.

Required behavior:

- Server uses current authoritative stock.
- If negative inventory is disallowed, `comanda.close` conflicts.
- If negative inventory is allowed, apply movement and return warnings.

### Kitchen screen offline from POS

Problem:

- POS sends items locally, but kitchen display is also disconnected.

Required behavior:

- Local edge node is preferred for a restaurant-wide offline mode.
- Browser-only clients should clearly show that kitchen acknowledgement is
  pending.
- Printed kitchen tickets can be used as fallback if configured.

### Concurrent terminals edit the same comanda

Problem:

- Two devices queue changes against the same order.

Required behavior:

- Operations are applied in server receive/order sequence, guarded by current
  comanda state.
- Non-conflicting item additions can apply.
- State transitions such as close/cancel/deliver must validate current server
  status.

### Comanda closed before replayed item arrives

Problem:

- An offline terminal queues `comanda.item.add`, but another terminal closes the
  comanda online.

Required behavior:

- Item add returns `resource_not_editable`.
- Conflict record captures the rejected item.
- Operator can create a new comanda or issue an adjustment manually.

### Payment exceeds remaining balance

Problem:

- Offline cash payment is recorded after another payment already settles the
  nota de venta.

Required behavior:

- Replay rejects with `payment_exceeds_balance` or `already_paid`.
- Do not update caja/bank balances.
- Preserve a conflict record for cash drawer reconciliation.

### Cash drawer closed before sync

Problem:

- Cash payment targets a caja that is closed by the time sync runs.

Required behavior:

- Return `payment_destination_unavailable`.
- Allow manager to map the payment to an open drawer or mark it for manual cash
  reconciliation.

### Client clock skew

Problem:

- Local timestamps are inaccurate.

Required behavior:

- Treat client timestamps as informational.
- Use server receipt/application timestamps for authoritative ordering.
- Return server time on every sync response.

### Client revoked while offline

Problem:

- A device is disabled after it has queued operations.

Required behavior:

- Reject new sync batches with `client_revoked`.
- Keep uploaded payloads for audit when possible.
- Require manager review before applying any queued operations.

### Lost local storage

Problem:

- Browser storage or local SQLite is deleted before sync.

Required behavior:

- Server cannot recover unsynced operations.
- Client should warn operators when local backup/export is unavailable.
- Edge-node deployments should persist queue data on durable storage.

### Schema or contract version mismatch

Problem:

- Client sync contract version is older than Django supports.

Required behavior:

- Return `426 upgrade_required` or `409 sync_contract_unsupported`.
- Do not apply ambiguous commands.

### Very large offline queue

Problem:

- Restaurant operates offline for a long period.

Required behavior:

- Limit batch size.
- Support resumable upload by batch.
- Process operations incrementally.
- Show progress and conflicts as they are discovered.

## Security and permissions

- All sync endpoints require authenticated users or device credentials.
- Device credentials must map to a `SyncClient`.
- Enforce sucursal and ubicacion scope during replay.
- Store raw payloads carefully because they may contain financial data.
- Do not allow local clients to bypass Django service validation.
- Record `request_id`, `client_uuid`, authenticated user, and source IP for
  audit.

## Frontend transparency requirements

The offline layer should be transparent for normal flow, but visible for trust.

Minimum UI states:

- `online`
- `intermittent`
- `offline`
- `syncing`
- `pending_sync`
- `synced`
- `needs_review`

Display requirements:

- Show a small connectivity/sync indicator.
- Mark local folios and receipts as provisional.
- Show final server folio after sync.
- Warn before accepting high-risk offline payments.
- Expose manager review for unresolved conflicts.

## Observability

Metrics:

- active sync clients
- queue depth by client
- oldest pending operation age
- batch success/partial/failure counts
- conflict counts by type
- duplicate idempotency hits
- average sync processing latency

Logs:

- include `X-Request-ID`, `client_uuid`, `batch_uuid`, and `operation_uuid`.
- log conflicts at warning level.
- log duplicate idempotency hits at info level.
- log financial and inventory conflicts with enough context for audit.

## Implementation phases

### Phase 1: Snapshots

- Add `GET /api/v1/sync/bootstrap/`.
- Package catalogs, sucursales, menu data, routing config, and comanda config.
- Add snapshot versioning and `ETag`.
- Add tests for authentication, scope, response shape, and unchanged snapshots.

Acceptance criteria:

- A local client can fully bootstrap without calling paginated catalog endpoints
  individually.
- Snapshot includes enough data to create a comanda locally.

### Phase 2: Idempotency

- Add `IdempotencyRecord`.
- Add idempotency handling for unsafe existing endpoints.
- Require idempotency headers for sync replay.
- Add duplicate and payload-mismatch tests.

Acceptance criteria:

- Retrying the same comanda create or payment request cannot create duplicates.
- Same key with different payload returns conflict.

### Phase 3: Sync persistence

- Add `SyncClient`, `SyncBatch`, and `SyncOperation`.
- Add client registration/status endpoints.
- Persist batch payloads and operation results.

Acceptance criteria:

- Duplicate batch uploads are detected.
- Operation results remain queryable after processing.

### Phase 4: Comanda replay

- Implement command handlers for:
  - `comanda.create`
  - `comanda.item.add`
  - `comanda.send_to_preparation`
  - `preparacion.item.complete`
  - `comanda.item.deliver`
  - `comanda.close`
- Add local ID mapping.
- Add operation dependency handling.

Acceptance criteria:

- A complete offline order can be queued and replayed through Django.
- Final server IDs and folios are returned to the client.

### Phase 5: Cash payment replay

- Implement `nota_venta.payment.record_cash`.
- Restrict card/bank payments unless explicitly enabled.
- Add cash drawer conflict handling.

Acceptance criteria:

- Offline cash payments sync once and only once.
- Overpayments and closed drawers produce reviewable conflicts.

### Phase 6: Conflict review

- Add `ConflictRecord` endpoints.
- Add manager resolution workflow.
- Add audit output for financial and inventory conflicts.

Acceptance criteria:

- Operators can list, inspect, and resolve conflicts.
- Resolution actions are auditable.

### Phase 7: Client integration

- Implement local snapshot store.
- Implement local command queue.
- Implement sync worker.
- Implement UI state indicators and provisional folio display.

Acceptance criteria:

- POS can take an order offline and sync it later.
- UI distinguishes pending and server-confirmed states.

## Testing strategy

Server automated tests:

- snapshot bootstrap authentication and scoping;
- unchanged snapshot `304` behavior;
- idempotency duplicate replay;
- idempotency payload mismatch;
- duplicate batch upload;
- ordered operation replay;
- dependency failure;
- comanda create/item/add/send/close replay;
- inventory conflict on close;
- cash payment replay;
- overpayment conflict;
- revoked client rejection.

Integration tests:

- simulate network timeout after server commit, then retry;
- replay a batch with mixed applied and conflicted operations;
- replay the same batch twice;
- sync operations from two clients against the same comanda;
- operate from stale snapshot after menu price/status change.

Manual end-to-end tests:

- bootstrap local client online;
- disable network;
- create comanda and add items;
- reconnect;
- confirm final server folio and IDs;
- trigger one conflict and resolve it.

## Implementation guardrails

- Keep Django as the only writer to authoritative PostgreSQL business tables.
- Keep business logic in service/repository/factory layers.
- Use request middleware only for cross-cutting concerns such as request IDs,
  client ID extraction, and idempotency lookup.
- Do not put command replay logic in Django `MIDDLEWARE`.
- Do not create a `restaurante/migrations/` directory unless the unmanaged
  schema strategy changes.
- Prefer explicit sync endpoints over hidden behavior in existing endpoints.
